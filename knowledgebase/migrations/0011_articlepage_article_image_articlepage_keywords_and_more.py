# Generated by Django 5.1.4 on 2025-01-28 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledgebase', '0010_articlepage_review_date_articlepage_reviewed_and_more'),
        ('wagtailimages', '0027_image_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='article_image',
            field=models.ForeignKey(blank=True, help_text='Optional image to display with the article', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Article Image'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='keywords',
            field=models.TextField(blank=True, help_text='Comma-separated keywords to improve searchability'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='lifestyle',
            field=models.TextField(blank=True, help_text='Lifestyle content'),
        ),
    ]
