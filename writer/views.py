from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Article
from .forms import ArticleForm,StandardArticleForm,PremiumArticleForm,ArticleCollectionForm

# Create your views here.
@login_required(login_url="sign-in")
def writer_dashboard(request):
    current_user=request.user.id
    try:
        articles=Article.objects.all().filter(author_id=current_user).order_by("-posted_at")
        
    except Article.DoesNotExist:
        articles="None"
    context={
        "articles":articles
    }
    return render(request, "writer/writer-dashboard.html", context)

@login_required(login_url="sign-in")
def create_article(request):
    form=ArticleForm(request.POST or None)
    if request.method == "POST":
        form=ArticleForm(request.POST,request.FILES)
        if form.is_valid():
            article=form.save(commit=False)
            article.author=request.user
            article.save()
            return redirect("writer-dashboard")
    context={
        "form":form,
        
    }
    return render(request, "writer/create-article.html",context)

@login_required(login_url="sign-in")
def create_standard_article(request):
    form=StandardArticleForm(request.POST or None)
    if request.method == "POST":
        form=StandardArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article=form.save(commit=False)
            article.author=request.user
            article.save()
            return redirect("writer-dashboard")
    context={
        "form":form
    }
    return render(request, "writer/create-standard-article.html", context)

def update_article(request,id):
    try:
        user=request.user.id
        article=Article.objects.get(id=id, author_id=user)
    except Article.DoesNotExist:
        return redirect("writer-dashboard")
    form=None
    if article.is_standard is True:
        form=StandardArticleForm(request.POST or None, instance=article)
        if request.method=='POST':
            form=StandardArticleForm(request.POST,request.FILES, instance=article)
            if form.is_valid():
                form.save()
                return redirect("writer-dashboard") 
    elif article.is_premium is True:
        form=PremiumArticleForm(request.POST or None, instance=article)
        if request.method=='POST':
            form=PremiumArticleForm(request.POST,request.FILES, instance=article)
            if form.is_valid():
                form.save()
                return redirect("writer-dashboard") 
    else:
        form=ArticleForm(request.POST or None, instance=article)
        if request.method=='POST':
            form=ArticleForm(request.POST,request.FILES, instance=article)
            if form.is_valid():
                form.save()
                return redirect("writer-dashboard") 
       
    context={
        "form":form
    }
    return render(request, "writer/update-article.html", context)

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

def writer_ranks(request):
    return render(request, "writer/writer-ranks.html")