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
    path('update-subscription/<subId>/',views.update_subscription,name="update-subscription"),
    path('subscription-update-success/', views.subscription_update_success, name="subscription-update-success"),
    path('tab/',views.tab,name="tab"),
    path('standard-posts/subscription-posts/',views.subscription_posts,name="subscription-posts"),
    path('favorite/<int:id>/',views.article_favorite,name="article-favorite"),
    path('favorite/<int:id>/',views.article_favorite,name="article-favorite")
]