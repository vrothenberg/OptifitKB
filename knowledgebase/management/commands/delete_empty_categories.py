# knowledgebase/management/commands/delete_empty_categories.py

from django.core.management.base import BaseCommand, CommandError
from knowledgebase.models import CategoryPage, ArticlePage
from wagtail.management.commands.fixtree import Command as FixTreeCommand

class Command(BaseCommand):
    help = "Deletes empty CategoryPage instances (categories with no articles)."

    def handle(self, *args, **options):
        # Find empty categories using the correct reverse relationship name
        empty_categories = CategoryPage.objects.filter(articles__isnull=True)
        category_count = empty_categories.count()

        if category_count == 0:
            self.stdout.write(self.style.WARNING("No empty categories found."))
            return

        # Confirmation prompt
        self.stdout.write(self.style.WARNING(f"Are you sure you want to delete {category_count} empty categories?"))
        confirmation = input("Type 'yes' to confirm: ")

        if confirmation.lower() != 'yes':
            self.stdout.write("Deletion cancelled.")
            return

        # Delete empty categories
        try:
            for category in empty_categories:
                category.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted empty category: {category.title}"))

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {category_count} empty categories."))
        except Exception as e:
            raise CommandError(f"An error occurred while deleting empty categories: {e}")

        # Validate tree integrity
        FixTreeCommand().handle()