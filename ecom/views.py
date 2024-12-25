from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, User, Contact, About, CartItem, Cart
from django.contrib import messages
from .utils import never_cache_custom
from django.contrib.auth.hashers import make_password, check_password
from .utils import never_cache_custom, user, user_login_required
from django.urls import reverse
from django.http import JsonResponse
import json


# This function handles the user register process
@never_cache_custom
@user
def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = make_password(request.POST["password"])
        gender = request.POST["gender"]
        age = request.POST["age"]

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "product_details/register.html",
                {"name": name, "phone": phone, "gender": gender, "age": age},
            )

        User.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            gender=gender,
            age=age,
        )
        return redirect("login")

    return render(request, "product_details/register.html")


# This function handles the user login process
@never_cache_custom
@user
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, "product_details/login.html")

        user = User.objects.get(email=email)
        if check_password(password, user.password):
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name
            return redirect("home_view")

    return render(request, "product_details/login.html")


# This function handles the user logout process
def logout(request):
    request.session.flush()
    return redirect("home_view")


# This function handles the home page
@never_cache_custom
def home_view(request):
    products = Product.objects.all()
    return render(request, "product_details/index.html", {"products": products})


# This function handles the add_Product page
@never_cache_custom
@user_login_required
def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")

        # Create product
        Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            stock=stock,
            image=image,
        )
        return redirect("home_view")

    return render(request, "product_details/add_product.html")


# This function handles the shop_view page
@never_cache_custom
def shop_view(request):
    products = Product.objects.all()
    return render(request, "product_details/shop.html", {"products": products})


@never_cache_custom
@user_login_required
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not (name and email and message):
            messages.error(request, "All fields are required.")
            return render(request, "product_details/contact.html")

        if Contact.objects.filter(email=email).exists():
            messages.error(request, "This email has already been used.")
        else:
            Contact.objects.create(name=name, email=email, message=message)
            messages.success(request, "Your message has been successfully sent.")
            return redirect(reverse("contact"))

    return render(request, "product_details/contact.html")


@never_cache_custom
def about_view(request):
    about = About.objects.first()
    return render(request, "product_details/about.html", {"about": about})


@never_cache_custom
@user_login_required
def get_cart(request):
    # Get the user from the session
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")  # Redirect to login if no user_id in session

    # Fetch user and cart from the database
    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)

    # Create a list of cart items with their details, including total price
    cart_items = [
        {
            "product": item.product.product_name,
            "quantity": item.quantity,
            "price": float(item.product.price),
            "total_price": float(item.product.price * item.quantity),
        }
        for item in cart.cart_items.all()
    ]

    return render(
        request,
        "product_details/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": sum(item['total_price'] for item in cart_items),
        }
    )

# Cart: Add Product to Cart
@never_cache_custom
@user_login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            # Log the raw body of the request
            print("Request Body:", request.POST)

            user_id = request.session.get("user_id")
            if not user_id:
                return JsonResponse({"error": "User not logged in"}, status=400)

            user = get_object_or_404(User, id=user_id)

            product_id = request.POST.get("product_id")
            if not product_id:
                return JsonResponse({"error": "Product ID is required"}, status=400)

            quantity = request.POST.get("quantity", 1)
            product = get_object_or_404(Product, id=product_id)
            cart, created = Cart.objects.get_or_create(user=user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity += int(quantity)
            cart_item.save()

            return redirect('cart_view')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
