from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail import images
from .blocks import (
    HeadingBlock, RichTextBlock, KeyFactsBlock, FAQListBlock, ReferenceListBlock, 
    BulletPointBlock, MarkdownBlock
)
from wagtail.search import index 
# Reviewed metadata
from wagtail.snippets.models import register_snippet 
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class IndexPage(Page):
    subpage_types = ['knowledgebase.CategoryPage']
    max_count = 1  # Only one index page at root

    content_panels = Page.content_panels

    def get_context(self, request, *args, **kwargs):
        """
        Overriding the get_context method to modify the context.
        """
        context = super().get_context(request, *args, **kwargs)

        # Get live CategoryPage children and order them alphabetically by title
        categories = CategoryPage.objects.live().child_of(self).order_by('title')

        context['categories'] = categories
        return context


class CategoryPage(Page):
    intro = RichTextField(blank=True)
    subpage_types = ['knowledgebase.ArticlePage']

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request, *args, **kwargs):
        """
        Overriding the get_context method to modify the context.
        """
        context = super().get_context(request, *args, **kwargs)

        # Get live ArticlePage children and order them alphabetically by title
        articles = ArticlePage.objects.live().child_of(self).order_by('title')

        context['articles'] = articles
        return context


@register_snippet
class Reviewer(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    credentials = models.CharField(max_length=255, blank=True, verbose_name=_("Credentials"))
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Photo")
    )
    bio = models.TextField(blank=True, verbose_name=_("Bio"))

    panels = [
        FieldPanel('name'),
        FieldPanel('credentials'),
        FieldPanel('photo'),
        FieldPanel('bio'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Reviewer")
        verbose_name_plural = _("Reviewers")


class ArticlePage(Page):
    reviewed = models.BooleanField(default=False, verbose_name=_("Reviewed"))
    reviewer = models.ForeignKey(
        Reviewer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Reviewer")
    )
    review_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Review Date"),
        help_text=_("Date the article was last reviewed. Defaults to the last published date.")
    )

    intro = models.TextField(
        blank=True, help_text="A short introductory description or subtitle."
    )
    
    keywords = models.TextField(
        blank=True,
        help_text="Comma-separated keywords to improve searchability"
    )

    article_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Article Image"),
        help_text="Optional image to display with the article"
    )

    lifestyle = models.TextField(
        blank=True, help_text="Lifestyle content"
    )
    
    body = StreamField(
        [
            ('heading', HeadingBlock()),
            ('markdown', MarkdownBlock()),
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
        MultiFieldPanel(
            [
                FieldPanel('reviewed'),
                FieldPanel('reviewer'),
                FieldPanel('review_date'),
            ],
            heading=_("Review Information"),
        ),
        FieldPanel('intro'),
        FieldPanel('keywords'),
        FieldPanel('article_image'),
        FieldPanel('body'),
        FieldPanel('category'),
    ]

    search_fields = Page.search_fields + [  # Define search_fields here
        index.SearchField('title', boost=2),
        index.SearchField('intro', boost=2),
        index.SearchField('keywords'),
        index.SearchField('body'),  # Include the body (StreamField)
        index.RelatedFields('category', [  # Include the category's title
            index.SearchField('title'),
        ]),
    ]

    def save(self, *args, **kwargs):
        """
        Override the save method to update the review_date.
        """
        # If the article is being published and marked as reviewed, 
        # set the review_date to the current date and time
        if self.live and self.reviewed:
            self.review_date = timezone.now()
        # If the article is being marked as not reviewed, clear the review date
        elif self.reviewed == False:
            self.review_date = None

        super().save(*args, **kwargs)