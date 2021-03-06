import datetime
import logging
import time

import feedparser
import lxml.etree
from django.db import transaction
from django.utils import timezone
from django.utils.text import Truncator

from .models import Article, Feed, Folder

logger = logging.getLogger(__name__)


def truncate(text, length):
    return Truncator(text).chars(length)


def to_datetime(timetuple):
    if timetuple is None:
        return None
    when = datetime.datetime.fromtimestamp(time.mktime(timetuple))
    return timezone.make_aware(when, timezone=timezone.utc)


@transaction.atomic()
def fetch_feed(feed):
    logger.info("Fetching feed '%s' (URL %s)", feed, feed.feed_url)

    response = feedparser.parse(feed.feed_url)
    now = timezone.now()

    for entry in response.entries:

        # Everything must have a title
        title = entry.title
        # Everything should have a URL, but sometimes it does not
        url = getattr(entry, 'link', None)
        # Everything should have an ID, but sometimes it does not. Make up
        # a decent replacement in this case.
        id = getattr(entry, 'id', url or title)

        # Everything should have a date, but no one can agree on published vs.
        # updated. Also some things do not have dates.
        if hasattr(entry, 'published_parsed'):
            published = to_datetime(entry.published_parsed)
        elif hasattr(entry, 'updated_parsed'):
            published = to_datetime(entry.updated_parsed)
        else:
            published = now

        article, created = Article.objects.update_or_create(
            feed=feed,
            guid=id,
            defaults=dict(
                title=truncate(getattr(entry, 'title', 'Untitled'), 500),
                description=getattr(entry, 'description', ''),
                url=url or feed.homepage,
                published_date=published,
            ),
        )

        logger.info("%s article '%s' (GUID '%s')",
                    "Created" if created else "Updated",
                    article, article.guid)

    feed.last_fetched = now
    feed.save()


def remove_stale_articles(articles, when=None):
    """
    Remove stale articles from the queryset that have been read and are older than
    a threshold.
    """

    articles.stale(when).delete()


@transaction.atomic
def import_opml(opml_string, target_folder):
    xml = lxml.etree.fromstring(opml_string)
    body = xml.find('./body')
    for outline in body.getchildren():
        import_opml_outline(outline, target_folder)


def import_opml_outline(outline, target_folder):
    if outline.get('xmlUrl', None):
        import_opml_feed(outline, target_folder)
    else:
        import_opml_folder(outline, target_folder)


def import_opml_feed(outline, target_folder):
    Feed.objects.create(
        folder=target_folder,
        name=outline.get('title', 'Untitled'),
        feed_url=outline.get('xmlUrl'),
        homepage=outline.get('htmlUrl', ''),
        fetch_interval=datetime.timedelta(hours=1),
    )


def import_opml_folder(outline, target_folder):
    folder = Folder.objects.create(
        user=target_folder.user,
        name=outline.get('text', 'Untitled folder'),
        parent=target_folder,
    )

    for child in outline:
        import_opml_outline(child, folder)
