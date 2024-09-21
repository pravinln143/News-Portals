from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from newsapi import NewsApiClient

from news_portal.celery import app
from news.models import News, Category


@app.task(bind=True)
def fetch_news(self):
    client = NewsApiClient(api_key=settings.NEWSAPI_API_KEY)
    date_from = timezone.now().date() - timedelta(days=1)

    for category in Category.objects.all():
        response = client.get_everything(
            q=category.name, language="en", from_param=date_from
        )
        articles = response.get("articles")
        for article in articles:
            content = article.get("content").split("[")[0]
            content += (
                f"<a href='{article.get('url')}' target='_blank'>"
                f"See full article</a>"
            )
            title = article.get("author")
            if title:
                db_article = News(
                    source=article["source"].get("name"),
                    title=title,
                    description=content,
                    image_url=article.get("urlToImage"),
                    category=category,
                )
                db_article.save()
