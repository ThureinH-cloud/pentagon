from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AccountStatus(models.Model):
    is_verified=models.BooleanField(default=False)
    profile=models.ImageField(max_length=100, blank=True,default="account/default.jpeg",null=True,upload_to="media/account")
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="account_status")
    created_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username