from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AccountStatus(models.Model):
    is_verified=models.BooleanField(default=False)
    profile=models.ImageField(max_length=100, blank=True,default="account/default.jpeg",null=True,upload_to="media/account")
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="account_status")
    rank=models.CharField(max_length=20,blank=True, default="Silver")
    created_at=models.DateTimeField(auto_now=True)
    def get_profile_by_user(self):
        return self.user.account_status.first()
    def __str__(self):
        return self.user.username