# Generated by Django 5.1.4 on 2024-12-12 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_homepage_hero_cta_homepage_hero_cta_link_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='body',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='hero_cta',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='hero_cta_link',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='hero_text',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='image',
        ),
    ]
