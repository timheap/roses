# Generated by Django 2.0.5 on 2018-05-10 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roses', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feed',
            old_name='url',
            new_name='feed_url',
        ),
        migrations.AddField(
            model_name='feed',
            name='homepage',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
    ]