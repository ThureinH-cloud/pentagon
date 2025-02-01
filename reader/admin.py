from django.contrib import admin

# Register your models here.
from .models import Subscription,Favorite

admin.site.register(Subscription)
admin.site.register(Favorite)