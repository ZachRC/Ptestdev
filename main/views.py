from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CustomUser
from django.db.models import Q
from .stripe_utils import create_subscription_session, handle_subscription_success, cancel_subscription, delete_stripe_customer
import json

def index(request):
    return render(request, 'main/index.html')

def login_view(request):
    if request.method == 'POST':
        login_identifier = request.POST.get('login_identifier')
        password = request.POST.get('password')
        
        # First try to authenticate with the identifier as is (email)
        user = authenticate(request, username=login_identifier, password=password)
        
        if not user:
            try:
                # Try to find user by username
                user_by_username = CustomUser.objects.get(username=login_identifier)
                # If found, authenticate with their email
                user = authenticate(request, username=user_by_username.email, password=password)
            except CustomUser.DoesNotExist:
                try:
                    # Try to find user by email
                    user_by_email = CustomUser.objects.get(email=login_identifier)
                    # If found, authenticate with their email
                    user = authenticate(request, username=user_by_email.email, password=password)
                except CustomUser.DoesNotExist:
                    user = None
        
        if user is not None:
            login(request, user)
            return redirect('main:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'main/login.html')

@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_subscription_active:
                return JsonResponse({
                    'token': 'desktop_token',  # In a real app, generate a proper token
                    'user': {
                        'email': user.email,
                        'username': user.username,
                        'is_subscription_active': user.is_subscription_active,
                        'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None
                    }
                })
            else:
                return JsonResponse({
                    'error': 'Subscription required',
                    'message': 'Active subscription required to use the desktop app'
                }, status=403)
        else:
            return JsonResponse({
                'error': 'Invalid credentials',
                'message': 'Invalid email or password'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'error': 'Server error',
            'message': str(e)
        }, status=500)

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('main:register')
            
        if CustomUser.objects.filter(Q(email=email) | Q(username=username)).exists():
            messages.error(request, 'Email or username already exists')
            return redirect('main:register')
            
        user = CustomUser.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        login(request, user)
        return redirect('main:dashboard')
        
    return render(request, 'main/register.html')

@login_required
def dashboard(request):
    context = {
        'stripe_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'main/dashboard.html', context)

@login_required
def create_checkout_session(request):
    try:
        session = create_subscription_session(request.user)
        return JsonResponse({'sessionId': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def subscription_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, 'No session ID provided')
        return redirect('main:dashboard')
        
    try:
        user = handle_subscription_success(session_id)
        if user:
            messages.success(request, 'Successfully subscribed!')
        else:
            messages.error(request, 'Error processing subscription')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('main:dashboard')

@login_required
def subscription_cancel(request):
    if request.method == 'POST':
        success, message = cancel_subscription(request.user)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, f'Error cancelling subscription: {message}')
    return redirect('main:dashboard')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        try:
            # Delete Stripe customer and subscriptions if they exist
            delete_stripe_customer(user)
            # Delete the user account
            user.delete()
            logout(request)
            messages.success(request, 'Your account has been successfully deleted.')
            return redirect('main:index')
        except Exception as e:
            messages.error(request, f'Error deleting account: {str(e)}')
            return redirect('main:dashboard')
    return redirect('main:dashboard')
