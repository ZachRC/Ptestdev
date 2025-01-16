from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('subscription/create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('subscription/success/', views.subscription_success, name='subscription-success'),
    path('subscription/cancel/', views.subscription_cancel, name='subscription-cancel'),
    path('account/delete/', views.delete_account, name='delete-account'),
    path('api/auth/login/', views.api_login, name='api-login'),
] 