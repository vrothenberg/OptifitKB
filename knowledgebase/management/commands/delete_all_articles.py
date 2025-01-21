# knowledgebase/management/commands/delete_all_articles.py

from django.core.management.base import BaseCommand, CommandError
from knowledgebase.models import ArticlePage, CategoryPage
from wagtail.management.commands.fixtree import Command as FixTreeCommand

class Command(BaseCommand):
    help = "Deletes all ArticlePage instances and empty CategoryPage instances."

    def handle(self, *args, **options):
        # Get all articles
        articles = ArticlePage.objects.all()
        article_count = articles.count()

        if article_count == 0:
            self.stdout.write(self.style.WARNING("No articles found."))
        else:
            # Confirmation prompt for deleting articles
            self.stdout.write(self.style.WARNING(f"Are you sure you want to delete all {article_count} articles?"))
            confirmation = input("Type 'yes' to confirm: ")

            if confirmation.lower() != 'yes':
                self.stdout.write("Article deletion cancelled.")
            else:
                # Delete the articles
                try:
                    for article in articles:
                        article.delete()
                        self.stdout.write(self.style.SUCCESS(f"Deleted: {article.title}"))

                    self.stdout.write(self.style.SUCCESS(f"Successfully deleted all {article_count} articles."))
                except Exception as e:
                    raise CommandError(f"An error occurred while deleting articles: {e}")

        # Find and delete empty categories
        self.delete_empty_categories()

        # Validate tree integrity
        FixTreeCommand().handle()

    def delete_empty_categories(self):
        """Finds and deletes empty CategoryPage instances."""
        # Use the correct related_name 'articles'
        empty_categories = CategoryPage.objects.filter(articles__isnull=True)
        category_count = empty_categories.count()

        if category_count == 0:
            self.stdout.write(self.style.WARNING("No empty categories found."))
            return

        # Confirmation prompt for deleting categories
        self.stdout.write(self.style.WARNING(f"Are you sure you want to delete {category_count} empty categories?"))
        confirmation = input("Type 'yes' to confirm: ")

        if confirmation.lower() != 'yes':
            self.stdout.write("Category deletion cancelled.")
            return

        # Delete empty categories
        try:
            for category in empty_categories:
                category.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted empty category: {category.title}"))

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {category_count} empty categories."))
        except Exception as e:
            raise CommandError(f"An error occurred while deleting empty categories: {e}")