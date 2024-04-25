import datetime
from django.shortcuts import render, HttpResponse, redirect

from orders.models import Order
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from django.template.defaultfilters import slugify
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from vendor.models import Vendor



# Restricting Customer to accesing the vendorDasboard
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restricting Vendor to accesing the custDasboard
def ceck_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged In")
        return redirect("myAccount")
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():

            # Create The user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            # Send Verification Email
            email_subject = "foodOnline Account verification mail"
            email_template = "accounts/emails/accounts_verification_email.html"
            send_verification_email(request, user, email_subject, email_template)

            messages.success(request, 'Account has been registered successfully!!! Check Your email for activation link.')
            return redirect('registerUser')
        else:
            print('Invailid form')
            print(form.errors)
    
    else:
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/registerUser.html', context)





# Register Vendor
def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged In")
        return redirect("myAccount")
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid():

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user

            # Send Verification Email
            email_subject = "foodOnline Account verification mail"
            email_template = "accounts/emails/accounts_verification_email.html"
            send_verification_email(request, user, email_subject, email_template)

            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)

            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            
            messages.success(request, 'Account has been registered successfully!!! Check Your email for activation link.')
            return redirect('registerVendor') 
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, 'accounts/registerVendor.html', context)



def activate(request, uidb64, token):
    # Activate the user by setting is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError,OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Congratulations!!! Your account is activated.")
        return redirect("myAccount")
    else:
        messages.error(request, "Invailid activation link")
        return redirect("myAccount")


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged In")
        return redirect("myAccount")
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are loged In.")
            return redirect("myAccount")
        
        else:
            messages.error(request, "Invailid login credentials.")
            return redirect("login")

    return render(request, 'accounts/login.html')

def logout(request):
        auth.logout(request)
        messages.info(request, "You are logout")
        return redirect("login")


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirecturl = detectUser(user)
    return redirect(redirecturl)

@login_required(login_url="login")
@user_passes_test(test_func=ceck_role_customer)
def custDashboard(request):
    return render(request, 'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendordashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')
    recent_orders = orders[:10]

    # current month's revenue
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    # total revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
    }
    return render(request, 'accounts/vendorDashboard.html', context)



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            #send password reset email
            email_subject = "Reset password email"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, email_subject, email_template)

            messages.success(request, "Password reset link has been sent to your email address.")
            return redirect("login")
        else:
            messages.success(request, "Account does not exist.")
            return redirect("login")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError,OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password.")
        return redirect('reset_password')
    else:
        messages.error(request, "This link has been expired")
        return redirect("myaccount")
    

def reset_password(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session['uid']
            if pk is not None:
                user = User.objects.get(pk=pk)
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.success(request, "You password is set successfully.")
                return redirect("login")
            else:
                messages.error(request, "You session has been expired.")
                return redirect('forgot_password')
        else:
            messages.error(request, "Password doesn't match.")
    return render(request, 'accounts/reset_password.html')