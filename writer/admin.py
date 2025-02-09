from django.contrib import admin

# Register your models here.
from .models import Article,ArticleReview,ArticleCollection,RecentArticle

admin.site.register(Article)
admin.site.register(ArticleReview)
admin.site.register(ArticleCollection)
admin.site.register(RecentArticle)