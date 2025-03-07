from celery import shared_task
from .models import Article
from django.contrib.auth.models import User
from account.models import AccountStatus
from django.db.models import Avg,Count,Sum

@shared_task
def update_user_rank():
    users = User.objects.exclude(username="admin")
    
    for user in users:
        try:
            user_page_view = Article.objects.filter(author=user).aggregate(total_views=Sum('view_count'))
            user_articles = Article.objects.filter(author=user).aggregate(total_articles=Count('id'))
            
            total_views = user_page_view['total_views'] or 0  
            total_articles = user_articles['total_articles'] or 0
            if total_articles > 0:
                user_metrics = total_views / total_articles
                print(user_metrics)
            else:
                print("Skipping user due to zero articles.")
                continue
                
            user_metrics = total_views / total_articles 
            
            print(f"{user.username} Total Views: {total_views}, Total Articles: {total_articles}")
            print(f"User Metrics: {user_metrics}")

            account_status = AccountStatus.objects.get(user=user)

            if user_metrics >= 1000 and total_articles >= 10:
                account_status.rank = 'Platinum'
                print("User reached Platinum.")
            elif user_metrics >= 500 and total_articles >= 5:
                account_status.rank = 'Gold'
                print("User reached Gold.")
            else:
                print("User did not reach a new rank.")

            account_status.save()
        
        except Exception as e:
            print(f"Error processing user {user.username}: {e}")
