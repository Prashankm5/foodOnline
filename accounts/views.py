from django.shortcuts import render, HttpResponse, redirect
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages, auth
from vendor.forms import VendorForm
from django.template.defaultfilters import slugify
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied





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
        return redirect("dashboard")
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

            messages.success(request, 'Your account has been registered successfully!!!')
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
        return redirect("dashboard")
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

            # vendor_name = v_form.cleaned_data['vendor_name']
            # vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)

            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            
            messages.success(request, 'Your account has been registered successfully!!!')
            return redirect('registerVendor') 
    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, 'accounts/registerVendor.html', context)


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
def custdashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url="login")
@user_passes_test(test_func=check_role_vendor)
def vendordashboard(request):
    return render(request, 'accounts/vendorDashboard.html')



