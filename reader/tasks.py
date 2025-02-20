from celery import shared_task
from .models import Subscription
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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

@shared_task
def send_comment_task(comment_text="Default Comment",username="Something"):
    channel_layer=get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "comments_group",
        {
            "type":"comment",
            "comment":comment_text,
            "username":username
        }
    )