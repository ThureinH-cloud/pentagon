from celery import shared_task
from .models import Subscription
from django.utils import timezone
@shared_task
def delete_expired_subscriptions():
    
    current_date = timezone.now().date()
    expired_subscriptions = Subscription.objects.filter(expires_at__lt=current_date, is_active=True)
    expired_count = expired_subscriptions.count()
    if expired_count > 0:
        expired_subscriptions.delete()
        print("Expired subscriptions are being deleted.")
    else:
        return "No expired subscriptions found."
