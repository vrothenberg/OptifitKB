from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class HomePage(Page):
    subpage_types = ['knowledgebase.IndexPage', 'about.AboutPage']
    # Just a basic page; can add fields if needed
    content_panels = Page.content_panels
    