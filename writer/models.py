from django.db import models
import re
from django.contrib.auth.models import User
from account.models import AccountStatus
from django.core.validators import MinLengthValidator

# Create your models here.
class Article(models.Model):
    CATEGORY_CHOICES = [
        ('flutter', 'Flutter'),
        ('react-native', 'React Native'),
        ('node.js', 'Node.JS'),
        ('spring-boot','Spring Boot'),
        ('laravel','Laravel'),
        ('django',"Django"),
        ('aws',"AWS"),
        ('web-development','Web Development'),
        ('mobile-development','Mobile Development'),
        ('cloud','Cloud Architect')
    ]
    title=models.CharField(max_length=100)
    content=models.TextField(
        validators=[
            MinLengthValidator(40, message="Content must be at least 40 characters long.")
        ]
    )
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    view_count = models.PositiveIntegerField(default=0)
    posted_at=models.DateTimeField(auto_now_add=True)
    is_premium=models.BooleanField(default=False)
    is_standard=models.BooleanField(default=False)
    photo=models.ImageField(default='article/default.jpeg', blank=True, null=True,upload_to="article/")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES, 
        default='web-development',
        blank=False,
        null=False
    )
    def get_rating(self):
        reviews = self.article_review.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            return total_rating / len(reviews)
        else:
            return 0
    
    def get_author_name(self):
        return self.author.username
    def get_article_count_by_category(self):
        return Article.objects.filter(category=self.category).count()
    def get_account_status(self):
        try:
            return self.author.account_status.first()
        except AccountStatus.DoesNotExist:
            return None
    def __str__(self):
        return self.title
    def reading_time(self):
        word_count = len(re.findall(r'\w+', self.content))
        words_per_minute = 100
        reading_time = word_count / words_per_minute
        return round(reading_time)

class ArticleReview(models.Model):
    article=models.ForeignKey(Article, on_delete=models.CASCADE,related_name="article_review")
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="article_reviewer")
    comment=models.TextField(blank=True, null=True)
    rating=models.FloatField(default=0,blank=True, null=True)
    author_reply=models.TextField(blank=True, null=True)
    posted_at=models.DateTimeField(auto_now_add=True)
    def comment_count(self):
        return len(self.comment)
    def get_commenter(self):
        return self.user.account_status.first()
    def __str__(self):
        return self.comment
    

class ArticleCollection(models.Model):
    name=models.CharField(max_length=100)
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="article_collection")
    article=models.ForeignKey(Article, on_delete=models.CASCADE, related_name="article_collection")
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.article.title
    
class RecentArticle(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    article=models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username + " - " + self.article.title

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_new_comment = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username + " -  Has Comment" 