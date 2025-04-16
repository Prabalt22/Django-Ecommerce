from django.shortcuts import render, redirect
from . models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django.db.models import Q
import json
from cart.cart import Cart

def search(request):
    # Determine if they filled out the form
	if request.method == "POST":
		searched = request.POST['searched']
		# Query The Products DB Model
		searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
		# Test for null
		if not searched:
			messages.success(request, "That Product Does Not Exist...Please try Again.")
			return render(request, "search.html", {})
		else:
			return render(request, "search.html", {'searched':searched})
	else:
		return render(request, "search.html", {})

def update_info(request):
    if request.user.is_authenticated:
        # get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        # get user original form
        form = UserInfoForm(request.POST or None, instance=current_user)
        # get current user's shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        
        
        shipping_form =  ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            
            messages.success(request, "Your Info Has Been Updated!!")
            return redirect('home')
        return render(request, 'update_info.html',{'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In!!")
        return redirect('home')
    

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        
        if user_form.is_valid():
            user_form.save()
            
            login(request, current_user)
            messages.success(request, "User Has Been Updated!!")
            return redirect('home')
        return render(request, 'update_user.html',{'user_form':user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')
        
    # return render(request, 'update_user.html',{'user_form':user_form})


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories':categories})

def category(request, poo):
    poo = poo.replace('-',' ') 
    try:
        category = Category.objects.get(name=poo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products})
    except Exception as e:
        messages.success(request, ("That Catofory doesn't exist"))
        return redirect('home')

def product(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product.html', {'product':product})

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products':products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id = request.user.id)
            # get their saved cart from database
            saved_cart = current_user.old_cart
            if saved_cart:
                # convert to dictionary using Json
                converted_cart = json.loads(saved_cart)
                # add the loaded cart dictionary to our session
                # get the cart
                cart = Cart(request)
                # loop thru the cart and add the item from the databse
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
            
            messages.success(request, ("You have been logged in successfully"))
            return redirect('home')
        else:
            messages.success(request, ("There was an error, "))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    messages.success(request, ("You have logged out...Success"))
    logout(request)
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # login in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("User Name Created - Please Fill Out Your User Info Below"))
            return redirect('update_info')
        else:
            print(form.errors)
            messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})
            