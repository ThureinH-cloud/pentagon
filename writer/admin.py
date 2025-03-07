from django.contrib import admin

# Register your models here.
from .models import Article,ArticleReview,UserNotification

admin.site.register(Article)
admin.site.register(ArticleReview)
admin.site.register(UserNotification)