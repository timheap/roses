# Generated by Django 2.0.5 on 2018-05-09 23:59

import uuid

import django.db.models.deletion
import enumchoicefield.fields
import mptt.fields
import positions.fields
from django.conf import settings
from django.db import migrations, models

import roses.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=255)),
                ('order', positions.fields.PositionField(default=-1)),
                ('last_fetched', models.DateTimeField(blank=True, null=True)),
                ('fetch_interval', models.DurationField()),
                ('show_as', enumchoicefield.fields.EnumChoiceField(enum_class=roses.models.FeedDisplayStyle, max_length=11, verbose_name='Display articles as')),
            ],
            options={
                'ordering': ['folder', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='roses.Folder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(blank=True)),
                ('guid', models.CharField(blank=True, db_index=True, max_length=255)),
                ('published_date', models.DateTimeField()),
                ('xml', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roses.Feed')),
            ],
            options={
                'ordering': ['-published_date'],
            },
        ),
        migrations.AddField(
            model_name='feed',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roses.Folder'),
        ),
        migrations.AlterIndexTogether(
            name='article',
            index_together={('feed', 'guid')},
        ),
    ]
