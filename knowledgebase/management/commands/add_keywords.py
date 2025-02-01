import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page, Site
from knowledgebase.models import IndexPage, CategoryPage, ArticlePage

class Command(BaseCommand):
    help = ("Publish the latest draft (if one exists) and then update an ArticlePage’s "
            "keywords from JSON only if the keywords field is empty.")

    def add_arguments(self, parser):
        parser.add_argument(
            '--category-name',
            type=str,
            required=True,
            help='Name of the CategoryPage (e.g., "Allergies").'
        )
        parser.add_argument(
            '--json-path',
            type=str,
            required=True,
            help='Path to the JSON file containing article data.'
        )

    def handle(self, *args, **kwargs):
        category_name = kwargs.get('category_name')
        json_path = kwargs.get('json_path')

        # Validate that the JSON file exists.
        json_file = Path(json_path)
        if not json_file.is_file():
            self.stderr.write(f"JSON file not found at {json_path}.")
            return

        # Load JSON content.
        try:
            with open(json_file, 'r') as f:
                article_data = json.load(f)
        except json.JSONDecodeError as e:
            self.stderr.write(f"Error decoding JSON: {e}")
            return

        # Ensure the JSON has a title and keywords.
        if "title" not in article_data:
            self.stderr.write("JSON does not contain a 'title' field.")
            return
        if "keywords" not in article_data:
            self.stderr.write("JSON does not contain a 'keywords' field.")
            return

        # Ensure the IndexPage and CategoryPage exist.
        index_page = self.get_or_create_index_page()
        index_page.refresh_from_db()

        category_page = self.get_or_create_category_page(index_page, category_name)
        category_page.refresh_from_db()

        # Locate the ArticlePage by title.
        article = category_page.get_children().type(ArticlePage).filter(title=article_data["title"]).first()
        if not article:
            self.stderr.write(f"Article with title '{article_data['title']}' not found in category '{category_name}'.")
            return

        # Work with the specific instance.
        article = article.specific

        # If an unpublished draft exists, publish it.
        if article.has_unpublished_changes:
            self.stdout.write("Unpublished draft found. Publishing draft...")
            latest_revision = article.get_latest_revision()
            latest_revision.publish()
            article.refresh_from_db()
            self.stdout.write("Draft published.")

        # Now, update keywords only if the field is empty.
        if not article.keywords.strip():
            new_keywords = article_data.get("keywords", "")
            if isinstance(new_keywords, list):
                new_keywords = ", ".join(new_keywords)

            # Update the live model directly.
            ArticlePage.objects.filter(pk=article.pk).update(keywords=new_keywords)
            article.refresh_from_db()
            self.stdout.write(f"Keywords updated for article '{article.title}': {article.keywords}")
        else:
            self.stdout.write(f"Article '{article.title}' already has keywords; no update performed.")

    def get_or_create_index_page(self):
        """Ensure that an IndexPage exists, or create it."""
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stderr.write("Default Wagtail site not found.")
            return

        root_page = site.root_page
        index_page = IndexPage.objects.filter(title="Index").first()

        if not index_page:
            index_page = IndexPage(title="Index", slug="index")
            root_page.add_child(instance=index_page)
            index_page.save_revision().publish()
            self.stdout.write("Created IndexPage: Index")

        return index_page

    def get_or_create_category_page(self, index_page, category_name):
        """Ensure that the CategoryPage exists, or create it."""
        slug = slugify(category_name)
        category_page = CategoryPage.objects.filter(slug=slug, path__startswith=index_page.path).first()

        if not category_page:
            category_page = CategoryPage(title=category_name, slug=slug)
            index_page.add_child(instance=category_page)
            category_page.save_revision().publish()
            self.stdout.write(f"Created CategoryPage: {category_name}")

        return category_page
