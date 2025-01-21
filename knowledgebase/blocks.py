# knowledgebase/blocks.py
from django import forms
from wagtail import blocks
from markdown import Markdown  # Or from mistune import Markdown
from django.utils.safestring import mark_safe


class HeadingBlock(blocks.StructBlock):
    heading_text = blocks.CharBlock(label="Heading Text", max_length=255)
    level = blocks.ChoiceBlock(
        choices=[('h2', 'Heading 2'), ('h3', 'Heading 3'), ('h4', 'Heading 4')],
        default='h2'
    )

    class Meta:
        icon = 'title'
        label = 'Heading'


class RichTextBlock(blocks.RichTextBlock):
    class Meta:
        icon = 'doc-full'
        label = 'Rich Text'


class KeyFactsBlock(blocks.StructBlock):
    content = blocks.ListBlock(
        blocks.TextBlock(label="Fact"), label="Key Facts"
    )

    class Meta:
        icon = 'list-ul'
        label = 'Key Facts'

class BulletPointBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super().__init__(blocks.TextBlock(label="Point"), **kwargs)

    class Meta:
        icon = 'list-ul'
        label = 'Bullet Points'


class FAQBlock(blocks.StructBlock):
    question = blocks.CharBlock(label="Question")
    answer = blocks.RichTextBlock(label="Answer")

    class Meta:
        icon = 'help'
        label = 'FAQ'


class FAQListBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super().__init__(FAQBlock(), **kwargs)

    class Meta:
        icon = 'help-inverse'
        label = 'FAQs'


class ReferenceListBlock(blocks.ListBlock):
    def __init__(self, **kwargs):
        super().__init__(blocks.StructBlock([
            ('reference_number', blocks.IntegerBlock()),
            ('authors', blocks.CharBlock(required=False)),
            ('year', blocks.CharBlock(required=False)),
            ('title', blocks.CharBlock()),
            ('journal_source', blocks.CharBlock(required=False)),
            ('url_doi', blocks.URLBlock(required=False)),
        ]), **kwargs)

    class Meta:
        icon = 'list-ol'
        label = 'References'



class MarkdownBlock(blocks.TextBlock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If using wagtail-markdown, you might set a custom widget here
        # self.field.widget = forms.Textarea(attrs={'class': 'markdown-widget'})

    def render_basic(self, value, context=None):
        md = Markdown(extensions=['extra', 'codehilite'])  # Add extensions as needed
        return mark_safe(md.convert(value))