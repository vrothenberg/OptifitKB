import json
from pathlib import Path
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from django.utils.text import slugify
from knowledgebase.models import IndexPage, CategoryPage, ArticlePage
from knowledgebase.utils import generate_wagtail_streamfield_data
from wagtail.management.commands.fixtree import Command as FixTreeCommand
from wagtail.images import get_image_model

# python manage.py import_articles --category-name category --json-path path/to/your/file.json
class Command(BaseCommand):
    help = "Import articles from JSON into Wagtail"

    def add_arguments(self, parser):
        parser.add_argument('--category-name', type=str, required=True, help='Name of the CategoryPage (e.g., "Bites", "Brain Health").')
        parser.add_argument('--json-path', type=str, required=True, help='Path to the JSON file containing article data.')

    def handle(self, *args, **kwargs):
        category_name = kwargs.get('category_name')
        json_path = kwargs.get('json_path')

        # Validate JSON file
        json_file = Path(json_path)
        if not json_file.is_file():
            self.stderr.write(f"JSON file not found at {json_path}.")
            return

        # Load JSON content
        try:
            with open(json_file, 'r') as f:
                article_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stderr.write(f"Error decoding JSON: {e}")
            return

        # Ensure the IndexPage exists
        index_page = self.get_or_create_index_page()
        index_page.refresh_from_db()

        # Ensure the CategoryPage exists
        category_page = self.get_or_create_category_page(index_page, category_name)
        category_page.refresh_from_db()

        # Generate StreamField data for the article
        streamfield_data = generate_wagtail_streamfield_data(article_data)

        # Check for an existing article with the same title
        existing_article = category_page.get_children().type(ArticlePage).filter(title=article_data['title']).first()
        if existing_article:
            self.update_existing_article(existing_article, article_data, streamfield_data)
        else:
            # Create the new ArticlePage
            self.create_article_page(category_page, article_data, streamfield_data)

        # Validate tree integrity
        self.stdout.write("Validating tree integrity...")

        FixTreeCommand().handle()

    def get_or_create_index_page(self):
        """Ensure that an IndexPage exists, or create it."""
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stderr.write("Default Wagtail site not found.")
            return

        root_page = site.root_page
        index_page = IndexPage.objects.filter(title="Index").first()

        if not index_page:
            index_page = IndexPage(
                title="Index",
                slug="index",
            )
            root_page.add_child(instance=index_page)
            index_page.save_revision().publish()
            self.stdout.write("Created IndexPage: Index")

        return index_page

    def get_or_create_category_page(self, index_page, category_name):
        """Ensure that the CategoryPage exists, or create it."""
        slug = slugify(category_name)
        category_page = CategoryPage.objects.filter(slug=slug, path__startswith=index_page.path).first()

        if not category_page:
            category_page = CategoryPage(
                title=category_name,
                slug=slug,
            )
            index_page.add_child(instance=category_page)
            category_page.save_revision().publish()
            self.stdout.write(f"Created CategoryPage: {category_name}")

        return category_page
    
    def update_existing_article(self, article, article_data, streamfield_data):
        """Update an existing ArticlePage with new data and publish a new revision."""
        self.stdout.write(f"Updating existing article: {article.title}")

        # Get the specific instance of the article (i.e. ArticlePage instance)
        article = article.specific

        # Update intro
        article.intro = article_data.get('subtitle', '')

        # Convert keywords from list to comma-separated string if needed.
        keywords = article_data.get('keywords', '')
        if isinstance(keywords, list):
            keywords = ", ".join(keywords)
        article.keywords = keywords

        # Update the article image if provided
        article_image_id = article_data.get('article_image', None)
        if article_image_id:
            try:
                Image = get_image_model()
                article.article_image = Image.objects.get(pk=article_image_id)
            except (Image.DoesNotExist, ValueError) as e:
                self.stderr.write(f"Invalid article image ID: {article_image_id}. Error: {e}")
                article.article_image = None
        else:
            article.article_image = None

        # Update the StreamField data (body)
        article.body = streamfield_data

        # Publish a new revision using the specific instance
        article.specific.save_revision().publish()
        self.stdout.write(f"Successfully updated article: {article.title}")


    def archive_existing_article(self, article):
        """Unpublish and move the article to an 'Archived' location instead of deleting."""
        self.stdout.write(f"Archiving existing article: {article.title}")
        article.unpublish()

        archive_page = Page.objects.filter(title="Archived").first()
        if not archive_page:
            site_root = Site.objects.filter(is_default_site=True).first().root_page
            archive_page = Page(title="Archived", slug="archived")
            site_root.add_child(instance=archive_page)
            archive_page.save_revision().publish()
            self.stdout.write("Created 'Archived' page for deleted articles.")

        article.move(archive_page, pos="last-child")

    def delete_existing_article(self, article):
        """Delete an existing article."""
        self.stdout.write(f"Deleting existing article: {article.title}")
        try:
            article.delete()
        except Exception as e:
            self.stderr.write(f"Error deleting ArticlePage: {e}")

    def create_article_page(self, category_page, article_data, streamfield_data):
        """Create a new ArticlePage."""
        try:
            # Get the StreamField definition from the ArticlePage model
            body_field = ArticlePage._meta.get_field('body')
            stream_value = streamfield_data

            # Handle the article image
            article_image_id = article_data.get('article_image', None)
            article_image = None
            if article_image_id:
                try:
                    Image = get_image_model()
                    article_image = Image.objects.get(pk=article_image_id)
                except (Image.DoesNotExist, ValueError) as e:
                    self.stderr.write(f"Invalid article image ID: {article_image_id}. Error: {e}")
                    article_image = None

            # Convert keywords from list to comma-separated string if needed.
            keywords = article_data.get('keywords', '')
            if isinstance(keywords, list):
                keywords = ", ".join(keywords)
            
            # Create the ArticlePage with the StreamField value
            article_page = ArticlePage(
                title=article_data['title'],
                intro=article_data.get('subtitle', ''),
                keywords=keywords,
                article_image=article_image,
                body=stream_value,
                category=category_page
            )

            category_page.add_child(instance=article_page)
            article_page.save_revision().publish()
            self.stdout.write(f"Successfully imported article: {article_data['title']}")
        except Exception as e:
            self.stderr.write(f"Error creating ArticlePage: {e}")