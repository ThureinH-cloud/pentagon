from datetime import datetime, timedelta
from django.db import IntegrityError
from django.shortcuts import render,redirect
from .forms import CreateUserForm,LoginForm,UpdateUserForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import AccountStatus
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from reader.models import Subscription
from django.template.loader import render_to_string
from reader.paypal import get_access_token,get_subscription_details
# Create your views here.
def sign_up( request):
    form=CreateUserForm(request.POST or None)
    if form.is_valid():
        current_user=form.save(commit=False)
        form.save()
        AccountStatus.objects.create(user=current_user)
        token = default_token_generator.make_token(current_user)
        uid = urlsafe_base64_encode(str(current_user.id).encode())
        verification_link = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        full_link = f"{settings.SITE_URL}{verification_link}"
        context={
            'full_link':full_link
        }
        send_mail('Welcome To Pentagon','', from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[current_user.email],html_message=render_to_string('account/verify-email-sent.html',context))
        return redirect('sign-in')
    return render(request, 'account/sign-up.html', {"form":form})

def sign_in(request):
    form=LoginForm()
    if request.method=="POST":
        form=LoginForm(request,data=request.POST)
        if form.is_valid():
            name=request.POST['username']
            password=request.POST['password']
            user=authenticate(request, username=name, password=password)
            if user is not None:
                login(request, user)
                return redirect('client-home')
    return render(request, 'account/sign-in.html', {"form":form})
def home(request):
    user=request.user
    if user.is_authenticated:
       return redirect("client-home") 
    return render(request, "account/index.html",{'user':user})
@login_required(login_url='sign-in')
def dashboard(request):
    return render(request, "account/dashboard.html")

@login_required(login_url='sign-in')
def profile(request):
    update_form=UpdateUserForm(request.POST or None, instance=request.user)
    account_status=AccountStatus.objects.get(user=request.user)
    
    
    try:
        user_subscription=Subscription.objects.get(user_id=request.user.id)
    except Subscription.DoesNotExist:
        user_subscription="None"
    context={
        "form":update_form,
        "account_status":account_status,
        "user_subscription":user_subscription
    }
    return render(request, "writer/profile.html",context)

@login_required(login_url='sign-in')
def sign_out(request):
    logout(request)
    return redirect("sign-in")

def verify_email(request,uidb64,token):
        uid = urlsafe_base64_decode(uidb64).decode()
        user=User.objects.get(id=uid)
        user_status = AccountStatus.objects.get(user_id=user.id)
        if default_token_generator.check_token(user, token):
            user_status.is_verified = True
            user_status.save()
            return redirect('verify-email-success')
        else:
            return redirect('home')

def locked(request):
    return render(request, 'account/locked.html')

def verify_email_success(request):
    return render(request, 'account/verify-email-success.html')

def create_subscription(request):
    email=request.user.email
    plan=request.GET.get("plan")
    token=request.GET.get("token")
    subId=urlsafe_base64_decode(token).decode()
    selected_sub_plan=plan
    if selected_sub_plan=='Standard':
        sub_cost='4.99'
    elif selected_sub_plan=="Premium":
        sub_cost='9.99'
    access_token = get_access_token()
    result=get_subscription_details(access_token, subId)
    if result is None:
        messages.error(request, "Subscription already exists or invalid data provided.")
        return redirect("home")
    try:
        Subscription.objects.create(subscriber_email=email,subscription_plan=selected_sub_plan,subscription_cost=sub_cost,paypal_subscription_id=subId,is_active=True,user=request.user,expires_at=datetime.now()+timedelta(days=30))
    except IntegrityError:
        messages.error(request, "Subscription already exists or invalid data provided.")
        return redirect("home")

    return redirect("subscription-success")