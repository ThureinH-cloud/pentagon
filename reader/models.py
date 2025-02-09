from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta
from writer.models import Article
# Create your models here.
class Subscription(models.Model):
    subscriber_email=models.CharField(max_length=255,unique=True)
    subscription_plan=models.CharField(max_length=255)
    subscription_cost=models.CharField(max_length=255)
    paypal_subscription_id=models.CharField(max_length=255,unique=True)
    is_active=models.BooleanField(default=False)
    user=models.OneToOneField(User,max_length=255,blank=True,on_delete=models.CASCADE,unique=True,related_name="sub_user")
    created_at=models.DateField(auto_now_add=True)
    expires_at=models.DateField(blank=True, null=True,default=datetime.now()+timedelta(days=30))
    def remaining(self):
        if self.expires_at:
            time_remaining=self.expires_at-datetime.now().date()
            return time_remaining.days
        else:
            return None
    def __str__(self):
        return f'{self.subscriber_email} - {self.subscription_plan} subscription'
    

class Favorite(models.Model):
    article=models.ForeignKey(Article, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    def get_article(self):
        return self.article
    def __str__(self):
        return self.user.username +"-" + self.article.title