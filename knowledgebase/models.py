# knowledgebase/models.py

from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from .blocks import (
    HeadingBlock, RichTextBlock, KeyFactsBlock, FAQListBlock, ReferenceListBlock, 
    BulletPointBlock
)

class IndexPage(Page):
    subpage_types = ['knowledgebase.CategoryPage']
    max_count = 1  # Only one index page at root

    content_panels = Page.content_panels

class CategoryPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = ['knowledgebase.ArticlePage']

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]



class ArticlePage(Page):
    intro = models.TextField(
        blank=True, help_text="A short introductory description or subtitle."
    )
    body = StreamField(
        [
            ('heading', HeadingBlock()),
            ('rich_text', RichTextBlock()),
            ('bullet_points', BulletPointBlock()),
            ('key_facts', KeyFactsBlock()),
            ('faqs', FAQListBlock()),
            ('references', ReferenceListBlock()),
        ],
        blank=True,
        use_json_field=True,  # Use JSON field for storage
        verbose_name="Article Content"
    )

    category = models.ForeignKey(
        'knowledgebase.CategoryPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='articles',
        help_text="The category this article belongs to."
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('category'),
    ]

    def save(self, *args, **kwargs):
        # Auto-assign the category if not set
        if not self.category:
            self.category = self.get_parent().specific
        super().save(*args, **kwargs)
