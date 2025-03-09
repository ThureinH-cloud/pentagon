from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Article,UserNotification,ArticleReview
from .forms import ArticleForm, StandardArticleForm,PremiumArticleForm
from account.models import AccountStatus
from reader.models import Subscription
from django.db.models import Sum,F
from django.contrib.auth.models import User
from django.db.models import Avg,Count

# Create your views here.
def get_account_status(request):
    account_status = AccountStatus.objects.get(user=request.user)
    return account_status

def user_notifications(request):
    user_notifications=UserNotification.objects.filter(user=request.user).count()
    return user_notifications

@login_required(login_url="sign-in")
def admin_dashboard(request):
    users=User.objects.all().exclude(username="admin")
    authors=Article.objects.filter(author__in=users).values("author").distinct().count()
    sub_users=Subscription.objects.filter(is_active=True).exclude(user_id=1).count()
    articles=Article.objects.all().count()
    if request.user.is_staff:
        context={
            "users":users.count(),
            "authors":authors,
            "sub_users":sub_users,
            "articles":articles,
            "account_status":get_account_status(request)
        }
        return render(request,"writer/admin-dashboard.html",context)
    else:
        return redirect("writer-dashboard")

@login_required(login_url="sign-in")
def author_statistics(request):
    authors = AccountStatus.objects.annotate(total_articles=Count("user__article__title")).exclude(user_id=1)
    real_authors=authors.filter(total_articles__gt=0).count()
    context={
        "count":real_authors,
        "authors":authors,
        "account_status":get_account_status(request),
    }
    return render(request,"writer/authors-statistics.html",context)

@login_required(login_url="sign-in")
def article_statistics(request):
    articles=Article.objects.all()
    count=articles.count()
    context={
        "articles":articles,
        "count":count,
        "account_status":get_account_status(request)
    }
    return render(request,"writer/article-statistics.html",context)

@login_required(login_url="sign-in")
def user_statistics(request):
    users=AccountStatus.objects.annotate(name=F("user__username"),email=F("user__email"),date_joined=F("user__date_joined")).exclude(user_id=1)
    print(users)
    context={
        "users":users,
        "account_status":get_account_status(request)
    }
    return render(request, "writer/users-statistics.html", context)

@login_required(login_url="sign-in")
def writer_dashboard(request):
    current_user=request.user
    user_rank=AccountStatus.objects.get(user=current_user)
    
    try:
        articles=Article.objects.all().filter(author=current_user).order_by("-posted_at")
    except Article.DoesNotExist:
        articles=None
    context={
        "articles":articles,
        "user_rank":user_rank,
        "user_notifications":user_notifications(request),
        "account_status":get_account_status(request)
    }
    return render(request, "writer/writer-dashboard.html", context)

@login_required(login_url="sign-in")
def create_article(request):
    article_form=ArticleForm(request.POST or None)
    if request.method == "POST":
        article_author=request.user
        category=request.POST.get("category")
        title=request.POST.get("title")
        content=request.POST.get("content")
        photo=request.FILES.get("photo")
        Article.objects.create(author=article_author, category=category, title=title, content=content, photo=photo)
        # article_form=ArticleForm(request.POST, request.FILES)
        # if article_form.is_valid():
        #     article=article_form.save(commit=False)
        #     article.author=request.user
        #     article.content=article_form.cleaned_data['content']
        #     article.save()
        return redirect("writer-dashboard")
    context={
        "categories":Article.CATEGORY_CHOICES,
        "account_status":get_account_status(request),
        "user_notifications":user_notifications(request),
        "form":article_form
    }
    return render(request, "writer/create-article.html",context)

@login_required(login_url="sign-in")
def create_standard_article(request):
    user_rank=AccountStatus.objects.get(user=request.user)
    categories=Article.CATEGORY_CHOICES

    if user_rank.rank != "Silver" :
        form=StandardArticleForm(request.POST or None)
        if request.method == "POST":
            form=StandardArticleForm(request.POST, request.FILES)
            if form.is_valid():
                article=form.save(commit=False)
                article.author=request.user
                article.save()
                return redirect("writer-dashboard")
        context={
            "form":form,
            "categories":categories,
            "account_status":get_account_status(request),
            "user_notifications":user_notifications(request)
        }
    else:
        return redirect("writer-ranks")
    return render(request, "writer/create-standard-article.html", context)

@login_required(login_url="sign-in")
def create_premium_article(request):
    user_rank=AccountStatus.objects.get(user=request.user)
    categories=Article.CATEGORY_CHOICES
    if user_rank.rank == "Platinum":
        form=PremiumArticleForm(request.POST or None)
        if request.method == "POST":
            form=PremiumArticleForm(request.POST, request.FILES)
            if form.is_valid():
                article=form.save(commit=False)
                article.author=request.user
                article.save()
                return redirect("writer-dashboard")
        context={
            "account_status":get_account_status(request),
            "form":form,
            "categories":categories
        }
    else:
        return redirect("rank_locked")
    return render(request, "writer/create-premium-article.html", context)


@login_required(login_url="sign-in")
def update_article(request,id):
    categories=Article.CATEGORY_CHOICES
    try:
        user=request.user
        article=Article.objects.get(id=id, author=user)
        
    except Article.DoesNotExist:
        return redirect("writer-dashboard")
    
    if request.method == "POST":
        article.author=user
        article.title=request.POST.get("title")
        article.content=request.POST.get("content")
        article.category=request.POST.get("category")
        
        if request.POST.get("is_premium") is not None:
            article.is_premium=request.POST.get("is_premium")
        elif request.POST.get("is_standard") is not None:
            article.is_standard=request.POST.get("is_standard")
        else:
            article.is_premium=False
            article.is_standard=False
            article.save()
        if request.FILES.get("photo") is not None:
            article.photo=request.FILES.get("photo")
        article.save()
        return redirect("writer-dashboard")
    # if article.is_standard is True:
    #     form=StandardArticleForm(request.POST or None, instance=article)
    #     if request.method=='POST':
    #         form=StandardArticleForm(request.POST,request.FILES, instance=article)
    #         if form.is_valid():
    #             form.save()
    #             return redirect("writer-dashboard") 
    # elif article.is_premium is True:
    #     form=PremiumArticleForm(request.POST or None, instance=article)
    #     if request.method=='POST':
    #         form=PremiumArticleForm(request.POST,request.FILES, instance=article)
    #         if form.is_valid():
    #             form.save()
    #             return redirect("writer-dashboard") 
    # else:
    #     form=ArticleForm(request.POST or None, instance=article)
    #     if request.method=='POST':
    #         form=ArticleForm(request.POST,request.FILES, instance=article)
    #         if form.is_valid():
    #             form.save()
    #             return redirect("writer-dashboard") 
       
    # context={
    #     "form":form
    # }
    context={
        "article":article,
        "categories":categories,
        "account_status":get_account_status(request),
    }
    return render(request, "writer/update-article.html",context)

def delete_article(request, id):
    
    article=Article.objects.get(id=id)
    article.delete()
    return redirect("writer-dashboard")

@login_required(login_url="sign-in")
def rank_locked(request):
    return render(request, "writer/rank-locked.html")

@login_required(login_url="sign-in")
def writer_ranks(request):
    return render(request, "writer/writer-ranks.html",{"account_status":get_account_status(request)})

@login_required(login_url="sign-in")
def statistics(request):
    subscription_users=Subscription.objects.all().exclude(user=1)
    total_profit=sum(float(subscription.subscription_cost) for subscription in subscription_users)
    
    context={
        "account_status":get_account_status(request),
        "accounts":subscription_users,
        "count":subscription_users.count(),
        "total_profit":total_profit
    }
    return render(request, "writer/statistics.html",context)

def check_comments(request):
    articles=Article.objects.filter(author=request.user)
    comments=ArticleReview.objects.filter(article__in=articles)
    print(comments)
    context={
        "account_status":get_account_status(request),
        "comments":comments,
        "articles":articles,
        
        }
    return render(request, "writer/check-comments.html",context)