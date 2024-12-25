from django.shortcuts import render, redirect
from .models import Product, User, Contact, About, CartItem
from django.contrib import messages
from .utils import never_cache_custom
from django.contrib.auth.hashers import make_password, check_password
from .utils import never_cache_custom, user, user_login_required
from django.urls import reverse
from .forms import CartAddProductForm

# This function handles the user register process
@never_cache_custom
@user
def register(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = make_password(request.POST['password'])
        gender = request.POST['gender']
        age = request.POST['age']

        # Check if the email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, f"The email '{email}' is already registered. Please use a different email.")
            return render(request, 'product_details/register.html', {
                'name': name,
                'phone': phone,
                'gender': gender,
                'age': age
            })

        # Create a new user if no conflicts exist
        User.objects.create(
            name=name, 
            email=email, 
            phone=phone, 
            password=password, 
            gender=gender, 
            age=age
        )
        messages.success(request, "Your account has been created successfully. Please log in.")
        return redirect('login')

    # Render the registration form for GET requests
    return render(request, 'product_details/register.html')

# This function handles the user login process
@never_cache_custom
@user
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, 'product_details/login.html')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('home_view')
            else:
                messages.error(request, "Invalid email or password. Please try again.")
        except User.DoesNotExist:
            messages.error(request, "No user found with this email address.")

    return render(request, 'product_details/login.html')

# This function handles the user logout process
def logout(request):
    request.session.flush()
    return redirect('home_view')

#This function handles the home page
@never_cache_custom
def home_view(request):
    products = Product.objects.all()
    return render(request, 'product_details/index.html', {'products': products})

#This function handles the add_Product page
@never_cache_custom
@user_login_required
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

#This function handles the shop_view page
@never_cache_custom
def shop_view(request):
    products = Product.objects.all()
    return render(request, 'product_details/shop.html', {'products': products})

@never_cache_custom
@user_login_required
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and email and message):
            messages.error(request, "All fields are required.")
            return render(request, 'product_details/contact.html')

        if Contact.objects.filter(email=email).exists():
            messages.error(request, "This email has already been used.")
        else:
            Contact.objects.create(name=name, email=email, message=message)
            messages.success(request, "Your message has been successfully sent.")
            return redirect(reverse('contact'))

    return render(request, 'product_details/contact.html')

@never_cache_custom
@user_login_required
def about_view(request):
    about = About.objects.first()
    return render(request, 'product_details/about.html', {'about': about})

@never_cache_custom
@user_login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'product_details/cart.html',{'cart_items':cart_items, 'total_price':total_price})

@never_cache_custom
@user_login_required
def cart_add(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)

    cart_item.quantity += 1
    cart_item.save()
    return redirect('ecom:view_cart')
    # cart = Cart(request)
    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    #     cart.add(product=product, quantity=cd['quantity'], update_quantity=cd['update'])
    # return redirect('cart:cart_detail')
