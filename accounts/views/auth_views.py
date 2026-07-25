from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from accounts.forms import FarmerRegistrationForm, LoginForm
from accounts.models import UserProfile, SystemLog

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def log_system_action(user, action, description, ip_address):
    SystemLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address
    )

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            first_name = full_name.split(' ')[0] if full_name else ''
            last_name = ' '.join(full_name.split(' ')[1:]) if full_name else ''
            
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=first_name,
                last_name=last_name
            )
            
            profile = user.profile
            profile.role = 'farmer'
            profile.phone = form.cleaned_data.get('phone', '')
            profile.gender = form.cleaned_data.get('gender', 'N')
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            
            login(request, user)
            log_system_action(user, 'register', 'New farmer registration', get_client_ip(request))
            messages.success(request, _('Account created successfully! Welcome to AmaranthusAI.'))
            return redirect('accounts:farmer_dashboard')
    else:
        form = FarmerRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                # Case-insensitive username lookup fallback
                existing_user = User.objects.filter(username__iexact=username).first()
                if existing_user:
                    user = authenticate(request, username=existing_user.username, password=password)

            if user is not None:
                if hasattr(user, 'profile') and not user.profile.is_active:
                    messages.error(request, 'Your account has been disabled.')
                    return render(request, 'accounts/login.html', {'form': form})
                    
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(30*24*3600)
                    
                log_system_action(user, 'login', 'User login', get_client_ip(request))
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('accounts:dashboard')
            else:
                messages.error(request, _('Invalid username or password.'))
    else:
        form = LoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        log_system_action(request.user, 'logout', 'User logout', get_client_ip(request))
        logout(request)
    return redirect('disease_app:home')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Use console backend or standard email sending
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_url}",
                "noreply@amaranthus.com",
                [email],
                fail_silently=False,
            )
        messages.success(request, "If an account exists with that email, a reset link has been sent.")
        return redirect('accounts:password_reset_done')
        
    return render(request, 'accounts/password_reset.html')

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_generator = PasswordResetTokenGenerator()
    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password1')
            new_password_confirm = request.POST.get('new_password2')
            if new_password and new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful.')
                return redirect('accounts:password_reset_complete')
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')
