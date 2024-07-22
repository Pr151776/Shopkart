from django.shortcuts import render,redirect
from . models import *
from django.contrib import messages
from .forms import CustomUserForm
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse
import json

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{'products':products})

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            pwd = request.POST.get('password')
            user = authenticate(request,username=name,password=pwd)
    
            if user is not None:
                login(request,user)
                messages.success(request,"Login Successfull")
                return redirect('/')
            else:
                messages.error(request,"Invalid User name or Password")
                return redirect('/login')
        return render(request,"shop/login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged Out Successfull")
    return redirect('/')

def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You Login Now...!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})

def collections(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"catagory": catagory})

def collectionsview(request,name):
    if (Catagory.objects.filter(name=name,status=0)):
        products = Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products": products,"category_name" : name})
    else:
        messages.warning(request,"No such catagory found")
        return redirect ('/collections')

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products = Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product.html",{'products':products})
        else:
            messages.error(request,"No Such Product Found")
            return redirect ('/collections')
    else:
        messages.error(request,"No Such Category Found")
        return redirect ('/collections')
    
def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            # print(data['product_qty'])
            # print(data['pid'])
            # print(request.user.id)

            product_qty = data['product_qty']
            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)

            if product_status:
                if Cart.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Cart'},status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status':'Product Added to Cart'},status=200)
                    else:
                        return JsonResponse({'status':'Product stock Not Available'},status=200)
        else:
            return JsonResponse({'status':'Login to add cart'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)
    
def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{'cart':cart})
    else:
        return redirect('/')
    
def remove_cart(request,cid):
    cartItem = Cart.objects.get(id=cid)
    cartItem.delete()
    return redirect('/cart')

def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            # print(data['product_qty'])
            # print(data['pid'])
            # print(request.user.id)

            product_id = data['pid']
            product_status = Product.objects.get(id=product_id)

            if product_status:
                if Favourite.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Favourite'},status=200)
                else:
                    Favourite.objects.create(user=request.user,product_id=product_id)
                    return JsonResponse({'status':'Product Added to Favourite'},status=200)
        else:
            return JsonResponse({'status':'Login to add Favourite'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)
    
def fav_view_page(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        return render(request,"shop/favourite.html",{'fav':fav})
    else:
        return redirect('/')
    
def remove_fav(request,cid):
    favItem = Favourite.objects.get(id=cid)
    favItem.delete()
    return redirect('/wish')