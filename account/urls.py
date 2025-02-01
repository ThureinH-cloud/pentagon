from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("sign-in/", views.sign_in, name="sign-in"),
    path("sign-up/", views.sign_up, name="sign-up"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('sign-out/',views.sign_out,name="sign-out"),
    path('profile/',views.profile,name="profile"),
    path('verify-email/<uidb64>/<token>/',views.verify_email,name='verify_email'),
    path('verify-email-success/',views.verify_email_success,name='verify-email-success'),
    path('reset-password/',auth_views.PasswordResetView.as_view(template_name='account/password-reset.html'),name="reset_password"),
    path('reset-password-sent/',auth_views.PasswordResetDoneView.as_view(template_name='account/password-reset-sent.html'),name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password-reset-form.html'), name="password_reset_confirm"),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password-reset-complete.html'), name="password_reset_complete"),
    path('locked/',views.locked,name="locked"),
    path('create-subscription/',views.create_subscription,name='create-subscription')
]