from django.forms import ModelForm
from .models import Article,ArticleCollection
from django import forms
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields=['title','content','photo','category']

class StandardArticleForm(ModelForm):
    class Meta:
        model=Article
        fields=['title','content','photo','category','is_standard']  

class PremiumArticleForm(ModelForm):
    class Meta:
        model=Article
        fields=['title','content','photo','category','is_premium']

# class ArticleReviewForm(ModelForm):
#     class Meta:
#         model = ArticleReview
#         fields=['rating','comment']
        
#     rating = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)],widget=StarRatingWidget)

class ArticleCollectionForm(ModelForm):
    class Meta:
        model=ArticleCollection
        fields=['name']