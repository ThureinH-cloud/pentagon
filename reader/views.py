from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Subscription,Favorite
from account.models import AccountStatus
from writer.models import Article,ArticleReview
from django.contrib.auth.models import User
from .paypal import get_access_token,cancel_subscription,update_subscription_plan
from django.db.models import Avg,Count
from django.http import HttpResponse
from django.core.paginator import Paginator

# Create your views here.
@login_required(login_url="sign-in")
def client_home(request):
    query=request.GET.get("search","")
    
    if query:
        articles=Article.objects.filter(title__icontains=query)
        context={
            "results":articles
        }
        return render(request,"reader/search_results.html",context)
    articles=Article.objects.all()
    paginator=Paginator(articles,2)
    page_number=request.GET.get("page")
    page_object=paginator.get_page(page_number)
    account_status=AccountStatus.objects.get(user_id=request.user.id)
    accounts=AccountStatus.objects.exclude(user__username="admin")
    articles=Article.objects.all()
    categories=Article.objects.values('category').distinct()
    
    context={
        'account_status':account_status,
        'accounts':accounts,
        'categories':categories,
        "page_objects":page_object
    }
    return render(request, "reader/home.html",context)

    
@login_required(login_url="sign-in")
def article_detail(request,id):
    article=Article.objects.get(id=id)
    try:
        article_favorite=Favorite.objects.get(article=article,user=request.user)
    except:
        article_favorite=None
    if article.is_premium is True:
        try:
            Subscription.objects.get(user=request.user, is_active=True,subscription_plan='Premium')
        except Subscription.DoesNotExist:
            return redirect("subscription-locked")
    elif article.is_standard is True:
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
    article_author=article.author
    account_status=AccountStatus.objects.get(user_id=request.user.id)

    context={
        "article":article,
        'article_author':article_author,
        'reading_time': article.reading_time(),
        'account_status':account_status,
        'article_reviews':article_reviews,
        'user_favorites':user_favorites,
        'article_favorite':article_favorite
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
        article_standard_authors=Article.objects.filter(is_standard=True).values('author').distinct()
        article_authors=User.objects.filter(id__in=article_standard_authors)
        accounts=AccountStatus.objects.filter(user__in=article_authors)
        context={
            "articles":articles,
            "accounts":accounts
            
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
        "param":param
    }
    return render(request, "reader/subscription-posts-filter.html", context)

@login_required(login_url="sign-in")
def premium_posts(request):
    try:
        sub_user=Subscription.objects.get(user=request.user,is_active=True)
    except Subscription.DoesNotExist:
        return redirect("subscription-locked")
    if sub_user.subscription_plan == "Premium":
        articles=Article.objects.filter(is_premium=True)
        context={
            "articles":articles,
        }
        return render(request, "reader/premium-posts.html", context)
    else:
        return redirect("subscription-locked")
@login_required(login_url="sign-in")
def subscription_locked(request):
    return render(request, "reader/subscription-locked.html")

@login_required(login_url='sign-in')
def subscription_plans(request):
    return render(request, "reader/subscription-plans.html")

def search(request):
    pass

@login_required(login_url="sign-in")
def subscription_success(request):
    return render(request, "reader/subscription-success.html")

@login_required(login_url="sign-in")
def category(request,category):
    category_articles=Article.objects.filter(category=category)
    context={
        "category_articles":category_articles,
        "category":category
    }
    return render(request, "reader/category_articles.html", context)

def author(request,author):
    pass

@login_required(login_url="sign-in")
def delete_subscription(request,subId):
    access_token=get_access_token()
    cancel_subscription(access_token,subId)
    sub=Subscription.objects.get(subscriber_email=request.user.email,paypal_subscription_id=subId)
    sub.delete()
    return render(request, "reader/delete-subscription.html")

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
def tab(request):
    param=request.GET.get("select")
    articles=None
    if "Latest" in param:
        articles=Article.objects.all().order_by("-posted_at")
    elif "Highest" in param:
        articles=Article.objects.annotate(avg_rating=Avg('article_review__rating')).order_by("-avg_rating")
    else:
        articles=Article.objects.annotate(favorite_count=Count('favorite__article')).order_by("-favorite_count")
    context={
        "articles":articles,
        "param":param
    }
    return render(request, "reader/select-tab.html",context)

@login_required(login_url="sign-in")
def article_favorite(request,id):
    articleObj=Article.objects.get(id=id)
    if request.method == "POST":
        Favorite.objects.create(user=request.user, article=articleObj)
    return redirect("client-home")

def remove_favorite(request, id):
    article=Article.objects.get(id=id)
    if request.method == "POST":
        Favorite.objects.get(user=request.user, article=article).delete()
    return redirect("client-home")


