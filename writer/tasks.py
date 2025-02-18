from celery import shared_task
from .models import Article
from django.contrib.auth.models import User
from account.models import AccountStatus
from django.db.models import Avg,Count,Sum

@shared_task
def update_user_rank():
    users=User.objects.exclude(username="admin")
    for user in users:
        user_page_view=Article.objects.filter(author=user).aggregate(total_views=Sum('view_count'))
        user_articles=Article.objects.filter(author=user).aggregate(total_articles=Count('id'))
        print(user.username,user_page_view)
        print(user_articles)
        user_metrics=user_page_view['total_views']/user_articles['total_articles']
        print(user_metrics)
        if user_metrics>=1000 and user_articles.total_articles>=10:
            account_status=AccountStatus.objects.get(user=user)
            account_status.rank='Platinum'
            account_status.save()
            print("User reached Platinum.")
        elif user_metrics>=500 and user_articles.total_articles>=5:
            account_status=AccountStatus.objects.get(user=user)
            account_status.rank='Gold'
            account_status.save()
            print("User reached Gold.")
        else:
            print("No users reached.")

@shared_task
def clean_recent_articles():
    users=User.objects.annotate(article_count=Count("recentarticle"))
    for user in users:
        print(user.article_count)