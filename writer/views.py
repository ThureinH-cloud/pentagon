from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Article
from .forms import ArticleForm, StandardArticleForm,PremiumArticleForm,ArticleCollectionForm
from account.models import AccountStatus
# Create your views here.
def get_account_status(request):
    account_status = AccountStatus.objects.get(user=request.user)
    return account_status
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
            "account_status":get_account_status(request)
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
        "categories":categories
    }
    return render(request, "writer/update-article.html",context)

def delete_article(request, id):
    
    article=Article.objects.get(id=id)
    article.delete()
    return redirect("writer-dashboard")

def create_collection(request):
    article_collection_form=ArticleCollectionForm(instance=request.user)
    context={
        "form":article_collection_form
    }
    return render(request, "writer/create-collection.html",context)

@login_required(login_url="sign-in")
def rank_locked(request):
    return render(request, "writer/rank-locked.html")

@login_required(login_url="sign-in")
def writer_ranks(request):
    return render(request, "writer/writer-ranks.html",{"account_status":get_account_status(request)})