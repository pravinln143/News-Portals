from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField(max_length=15)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    source = models.CharField(max_length=20, blank=True, null=True)
    likes = models.ManyToManyField(get_user_model(), related_name="news_like")

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title}"

    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    article = models.ForeignKey(News, on_delete=models.PROTECT)
    posted_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    posted_at = models.DateTimeField(default=timezone.now)
    comment = models.TextField()

    def __str__(self):
        return f"{self.article.__str__()}: {self.posted_by.get_full_name()}"

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"


class Banner(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    url = models.URLField()
    posted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} : {self.url}"

    class Meta:
        verbose_name = "banner"
        verbose_name_plural = "banners"




