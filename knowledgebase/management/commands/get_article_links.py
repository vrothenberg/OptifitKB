# knowledgebase/management/commands/get_article_links.py

import csv
from django.core.management.base import BaseCommand
from django.urls import reverse
from wagtail.models import Page
from django.conf import settings
from django.apps import apps
from urllib.parse import urljoin

class Command(BaseCommand):
    help = 'Gets all article page admin URLs, live URLs, and titles and outputs them to a CSV file.'

    def handle(self, *args, **options):
        article_data = []

        try:
            # Dynamically get the ArticlePage model
            ArticlePage = apps.get_model('knowledgebase', 'ArticlePage')

        except LookupError:
            self.stdout.write(self.style.ERROR('Could not find an ArticlePage model. Check that this model exists and it is called "ArticlePage". Alternatively pass the argument --article-page-type with the model name and --app with the app name'))
            return

        # Get all ArticlePage instances
        article_pages = ArticlePage.objects.all().live()

        base_url = 'https://kb.optifit.dev/'

        for article_page in article_pages:
            admin_url = reverse('wagtailadmin_pages:edit', args=[article_page.id])
            full_admin_url = urljoin(base_url, admin_url)

            # Use .url attribute for the live URL
            live_url = urljoin(base_url, article_page.url) if article_page.url else ""  # Handle cases where .url might be None
           
            article_data.append((article_page.title, full_admin_url, live_url))

        # Output to CSV
        with open('article_links.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Admin URL', 'Live URL'])  # Write header row
            writer.writerows(article_data)

        self.stdout.write(self.style.SUCCESS('Successfully wrote article data to article_links.csv'))