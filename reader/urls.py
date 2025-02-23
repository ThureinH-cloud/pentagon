from django.urls import path
from . import views
urlpatterns = [
    path('',views.client_home,name="client-home"),
    path('standard-posts/',views.standard_posts,name="standard-posts"),
    path('premium-posts/', views.premium_posts, name="premium-posts"),
    path('post/<int:id>/',views.article_detail,name="post-detail"),
    path('search/', views.search, name="search"),
    path('category/<str:category>/', views.category, name="category"),
    path('author/<str:author>/', views.author, name="author"),
    path('subscription-success/', views.subscription_success, name="subscription-success"),
    path('subscription-locked/',views.subscription_locked,name="subscription-locked"),
    path('subscription-plans/',views.subscription_plans,name="subscription-plans"),
    path('delete-subscription/<subId>/',views.delete_subscription,name='delete-subscription'),
    path('deactivate-subscription',views.deactivate_subscription,name="deactivate-subscription"),
    path('update-subscription/<subId>/',views.update_subscription,name="update-subscription"),
    path('subscription-update-success/', views.subscription_update_success, name="subscription-update-success"),
    path('tab/',views.tab,name="tab"),
    path('standard-posts/subscription-posts/',views.subscription_posts,name="subscription-posts"),
    path('premium-posts/subscription-posts/',views.premium_subscription_posts,name="premium_subscription-posts"),
    path('favorite/<int:id>/',views.article_favorite,name="article-favorite"),
    path('del-favorite/<int:id>/',views.remove_favorite,name="remove-favorite"),
    path('article-review/<int:id>',views.article_review,name="article-review"),
    path('paypal-update-confirmed/',views.subscription_update_success,name="paypal-update"),
    path('confirm-update-subscription/',views.confirm_update_subscription,name="confirm-update"),
    path('update-author-reply/<int:id>/',views.update_author_reply,name="update-author-reply")
]