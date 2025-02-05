from celery import shared_task
from .models import AccountStatus,Article

@shared_task
def update_account_status():
    # user=AccountStatus.objects.get(id=user_id)
    # articles=Article.objects.filter(author=user)
    # total_views=sum(article.view_count for article in articles)
    # avg_views=total_views/len(articles)
    # if avg_views>1000:
    #     user.rank="Platinum"
    #     print("User Rank reached to Platinum")
    # elif avg_views>500:
    #     user.rank="Gold"
    #     print("User Rank reached to Gold")
    