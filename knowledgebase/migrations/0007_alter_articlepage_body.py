# Generated by Django 5.1.4 on 2024-12-16 23:06

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('knowledgebase', '0006_alter_articlepage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='body',
            field=wagtail.fields.StreamField([('heading', 2), ('rich_text', 3), ('bullet_points', 6), ('key_facts', 9), ('faqs', 10), ('references', 11)], blank=True, block_lookup={0: ('wagtail.blocks.CharBlock', (), {'label': 'Heading Text', 'max_length': 255}), 1: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('h2', 'Heading 2'), ('h3', 'Heading 3'), ('h4', 'Heading 4')]}), 2: ('wagtail.blocks.StructBlock', [[('heading_text', 0), ('level', 1)]], {}), 3: ('knowledgebase.blocks.RichTextBlock', (), {}), 4: ('wagtail.blocks.TextBlock', (), {'label': 'Point'}), 5: ('wagtail.blocks.ListBlock', (4,), {'label': 'Bullet Points'}), 6: ('wagtail.blocks.StructBlock', [[('content', 5)]], {}), 7: ('wagtail.blocks.TextBlock', (), {'label': 'Fact'}), 8: ('wagtail.blocks.ListBlock', (7,), {'label': 'Key Facts'}), 9: ('wagtail.blocks.StructBlock', [[('content', 8)]], {}), 10: ('knowledgebase.blocks.FAQListBlock', (), {}), 11: ('knowledgebase.blocks.ReferenceListBlock', (), {})}, verbose_name='Article Content'),
        ),
    ]