from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subscription,Favorite
from account.models import AccountStatus
from writer.models import Article,ArticleReview,RecentArticle
from django.contrib import messages
from .paypal import get_access_token,cancel_subscription, get_subscription_details,update_subscription_plan
from django.db.models import Avg,Count
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.urls import reverse
# Create your views here.

def get_account_status(request):
    account_status = AccountStatus.objects.get(user=request.user)
    return account_status
@login_required(login_url="sign-in")
def client_home(request):
    recent_articles=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]

    query=request.GET.get("search","")
    if query:
        articles=Article.objects.filter(title__icontains=query)
        print(articles)
        context={
            "results":articles,
            "recent_articles":recent_articles,
            "query":query
        }
        return render(request,"reader/search_results.html",context)
    articles=Article.objects.all()
    paginator=Paginator(articles,2)
    page_number=request.GET.get("page")
    page_object=paginator.get_page(page_number)
    users=User.objects.all()
    authors=Article.objects.filter(author__in=users).values('author').distinct()
    accounts=AccountStatus.objects.filter(user__in=authors)
    print(accounts)
    categories=Article.objects.values('category').distinct()
    context={
        'account_status':get_account_status(request),
        'accounts':accounts,
        'categories':categories,
        "page_objects":page_object,
        "recent_articles":recent_articles,
        "show_spinner":True
    }
    return render(request, "reader/home.html",context)

    
@login_required(login_url="sign-in")
def article_detail(request,id):
    article=Article.objects.get(id=id)
    account_status=AccountStatus.objects.get(user=request.user)
    reviewer_check=ArticleReview.objects.filter(article=article,user=request.user)
    reply_check=ArticleReview.objects.filter(article=article, user=request.user, author_reply__isnull=False)
    
    if reviewer_check.exists():
        exist=False
    else:
        exist=True
    print(exist)
    try:
        article_favorite=Favorite.objects.get(article=article,user=request.user)
    except:
        article_favorite=None
        
    if article.is_premium is True:
        if article.author != request.user and account_status.rank is not "Platinum":
            try:
                Subscription.objects.get(user=request.user, is_active=True, subscription_plan='Premium')
            except Subscription.DoesNotExist:
                if account_status.rank == "Gold" and article.author == request.user:
                    pass
                return redirect("subscription-locked")          
    elif article.is_standard is True:
        if article.author != request.user and account_status.rank is not "Gold":
            try:
                sub=Subscription.objects.get(user=request.user, is_active=True)
                if sub.subscription_plan == 'Standard' or 'Premium':
                    pass
            except Subscription.DoesNotExist:
                return redirect("subscription-locked")
    else:
        pass
    article_reviews=ArticleReview.objects.filter(article=article)
    user_favorites=Favorite.objects.filter(user=request.user)
    
    if not request.session.get(f'viewed_post_{id}', False):
        article.view_count += 1
        article.save()
        request.session[f'viewed_post_{id}'] = True

    context={
        "article":article,
        'reading_time': article.reading_time(),
        'account_status':account_status,
        'article_reviews':article_reviews,
        'user_favorites':user_favorites,
        'article_favorite':article_favorite,
        'reviewer':exist
    }
    return render(request, "reader/post-detail.html", context)

@login_required(login_url="sign-in")
def standard_posts(request):
    try:
        sub_user=Subscription.objects.get(user=request.user,is_active=True)
    except Subscription.DoesNotExist:
        return redirect("subscription-locked")
    
    if sub_user.subscription_plan == 'Premium' or 'Standard':
        articles=Article.objects.filter(is_standard=True)
        article_standard_authors=Article.objects.filter(is_standard=True).values('author')
        article_categories=Article.objects.filter(is_standard=True).values("category").distinct()
        accounts=AccountStatus.objects.filter(user__in=article_standard_authors)
        recent_articles=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]
        query=request.GET.get("search","")
        if query:
            articles=Article.objects.filter(title__icontains=query)
            print(articles)
            context={
                "results":articles,
                "recent_articles":recent_articles,
                "query":query
            }
            return render(request,"reader/search_results.html",context)
        context={
            "articles":articles,
            "accounts":accounts,
            "account_status":get_account_status(request),
            "recent_articles":recent_articles,
            "categories":article_categories
        }
        return render(request, "reader/standard-posts.html", context)
    else:
        return redirect("subscription-locked")
    
@login_required(login_url="sign-in")
def subscription_posts(request):
    param=request.GET.get("select")
    try:
        Subscription.objects.get(user=request.user,is_active=True)
    except Subscription.DoesNotExist:
        return redirect("subscription-locked")
    if "Latest" in param:
        articles=Article.objects.filter(is_standard=True).order_by("-posted_at")
    elif "Highest" in param:
        articles=Article.objects.filter(is_standard=True).annotate(avg_rating=Avg('article_review__rating')).order_by("-avg_rating")
    elif "Most Favorite" in param:
        articles=Article.objects.filter(is_standard=True).annotate(favorite_count=Count('favorite__article')).order_by("-favorite_count")
    context={
        "articles":articles,
        "param":param,
        "account_status":get_account_status(request)
    }
    return render(request, "reader/subscription-posts-filter.html", context)

@login_required(login_url="sign-in")
def premium_subscription_posts(request):
    param=request.GET.get("select")
    recent_articles=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]

    try:
        Subscription.objects.get(user=request.user,is_active=True)
    except Subscription.DoesNotExist:
        return redirect("subscription-locked")
    if "Latest" in param:
        articles=Article.objects.filter(is_premium=True).order_by("-posted_at")
    elif "Highest" in param:
        articles=Article.objects.filter(is_premium=True).annotate(avg_rating=Avg('article_review__rating')).order_by("-avg_rating")
    elif "Most Favorite" in param:
        articles=Article.objects.filter(is_premium=True).annotate(favorite_count=Count('favorite__article')).order_by("-favorite_count")
    context={
        "articles":articles,
        "param":param,
        "recent_articles":recent_articles,
        "account_status":get_account_status(request)
    }
    return render(request, "reader/premium-posts-filter.html", context)

@login_required(login_url="sign-in")
def premium_posts(request):
    recent_articles=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]

    try:
        sub_user=Subscription.objects.get(user=request.user,is_active=True)
    except Subscription.DoesNotExist:
        return redirect("subscription-locked")
    if sub_user.subscription_plan == "Premium":
        articles=Article.objects.filter(is_premium=True).select_related("author")
        authors=AccountStatus.objects.filter(user__in=articles.values("author"))
        categories=Article.objects.filter(is_premium=True).values("category")
        context={
            "articles":articles,
            "account_status":get_account_status(request),
            "authors":authors,
            "categories":categories,
            "recent_articles":recent_articles
        }
        return render(request, "reader/premium-posts.html", context)
    else:
        return redirect("subscription-locked")
@login_required(login_url="sign-in")
def subscription_locked(request):
    return render(request, "reader/subscription-locked.html",{"account_status":get_account_status(request)})

@login_required(login_url='sign-in')
def subscription_plans(request):
    account_status=AccountStatus.objects.get(user=request.user)
    return render(request, "reader/subscription-plans.html",{"account_status":account_status})

def search(request):
    pass

@login_required(login_url="sign-in")
def subscription_success(request):
    sub_user=Subscription.objects.get(user=request.user)
    context={
        "SubscriptionPlan":sub_user.subscription_plan,
        "account_status":get_account_status(request)
    }
    return render(request, "reader/subscription-success.html",context)

@login_required(login_url="sign-in")
def category(request,category):
    category_articles=Article.objects.filter(category=category)
    categories=Article.objects.values("category").distinct()
    authors=Article.objects.filter(category=category).values("author").distinct()
    accounts=AccountStatus.objects.filter(user__in=authors)
    recent_articles=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]

    context={
        "category_articles":category_articles,
        "category":category,
        "categories":categories,
        "accounts":accounts,
        "recent_articles":recent_articles,
        "account_status":get_account_status(request)
    }
    return render(request, "reader/category_articles.html", context)

def author(request,author):
    pass

@login_required(login_url="sign-in")
def delete_subscription(request,subId):
    access_token=get_access_token()
    cancel_subscription(access_token,subId)
    try:
        if request.method == "POST":
            sub=Subscription.objects.get(subscriber_email=request.user.email,paypal_subscription_id=subId)
            sub.delete()
        else:
            return redirect("subscription-plans")
    except Subscription.DoesNotExist:
        messages.error(request,"Subscription doesn't exist")
        return redirect("subscription-plans")
    return redirect("deactivate-subscription")

@login_required(login_url="sign-in")
def deactivate_subscription(request):
    account_status=AccountStatus.objects.get(user=request.user)
    return render(request, "reader/delete-subscription.html",{"account_status":account_status})


@login_required(login_url="sign-in")
def update_subscription(request,subId):
    access_token=get_access_token()
    approve_url=update_subscription_plan(access_token,subId)
    if approve_url:
        return redirect(approve_url)
    else:
        return HttpResponse("Error: Unable to update subscription plan.")

@login_required(login_url='sign-in')
def subscription_update_success(request):
    return render(request, "reader/subscription-update-success.html")

@login_required(login_url="sign-in")
def confirm_update_subscription(request):
    try:
        sub_details=Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        return redirect("subscription-plans")
    access_token = get_access_token()
    result=get_subscription_details(access_token, sub_details.paypal_subscription_id)
    if result['plan_id']=="P-2EA74263YC2500708M6KPIXI":
        sub_details.subscription_plan="Premium"
        sub_details.subscription_cost="9.99"
        sub_details.save()
        return redirect("subscription-success")
    else:
        messages.error(request, "Subscription already exists or invalid data provided.")
        return redirect("subscription-plans")

@login_required(login_url="sign-in")
def tab(request):
    param=request.GET.get("select")
    articles=None
    recent_posts=RecentArticle.objects.filter(user=request.user).select_related("article").order_by("-created_at")[:5]
    if "Latest" in param:
        articles=Article.objects.all().order_by("-posted_at")
        categories=articles.values("category").distinct()
        authors=User.objects.filter(id__in=articles.values("author"))
        accounts=AccountStatus.objects.filter(user__in=authors)
    elif "Highest" in param:
        articles=Article.objects.annotate(avg_rating=Avg('article_review__rating')).order_by("-avg_rating")
        categories=articles.values("category").distinct()
        authors=User.objects.filter(id__in=articles.values("author"))
        accounts=AccountStatus.objects.filter(user__in=authors)
    else:
        articles=Article.objects.annotate(favorite_count=Count('favorite__article')).order_by("-favorite_count")
        categories=articles.values("category").distinct()
        authors=User.objects.filter(id__in=articles.values("author"))
        accounts=AccountStatus.objects.filter(user__in=authors)
    context={
        "articles":articles,
        "param":param,
        "account_status":get_account_status(request),
        "recent_posts":recent_posts,
        "accounts":accounts,
        "categories":categories
    }
    return render(request, "reader/select-tab.html",context)

def article_favorite(request,id):
    articleObj=Article.objects.get(id=id)
    if request.method == "POST":
        Favorite.objects.create(user=request.user, article=articleObj)
    return redirect(reverse("post-detail", args=[articleObj.id]))


def remove_favorite(request, id):
    article=Article.objects.get(id=id)
    if request.method == "POST":
        Favorite.objects.get(user=request.user, article=article).delete()
    return redirect(reverse("post-detail",args=[article.id]))

@login_required(login_url="sign-in")
def article_review(request,id):
    if request.method == "POST":
        article=Article.objects.get(id=id)
        comment=request.POST.get("comment")
        rating=request.POST.get("rating")
        if rating is None:
            rating=0
        ArticleReview.objects.create(user=request.user, article=article, comment=comment, rating=rating) 
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "comments_group",
            {
                "type": "send_comment",
                "text": comment,
                "user": request.user.username,
            }
        )
        return redirect(reverse("post-detail", args=[id]))


def update_author_reply(request,id):
    article_review=ArticleReview.objects.get(article=id)
    if request.method == "POST":
        article_review.author_reply=request.POST.get("author_reply")
        article_review.save()
        return redirect(reverse("post-detail",args=[id]))