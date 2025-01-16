from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from django.db.models import Q

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
    return render(request, 'main/dashboard.html')
