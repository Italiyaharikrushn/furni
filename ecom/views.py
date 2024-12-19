from django.shortcuts import render, redirect
from .models import Product, User
from django.contrib import messages
from .utils import never_cache_custom
from django.contrib.auth.hashers import make_password, check_password

def home_view(request):
    products = Product.objects.all()
    return render(request, 'product_details/index.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            image=image
        )
        return redirect('home_view')

    return render(request, 'product_details/add_product.html')

def shop_view(request):
    products = Product.objects.all()
    return render(request, 'product_details/shop.html', {'products': products})
