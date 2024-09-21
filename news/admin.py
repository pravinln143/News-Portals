from django.contrib import admin

from news.models import Category, News, Comment, Banner


admin.site.register(Category)
admin.site.register(News)
admin.site.register(Comment)
admin.site.register(Banner)
