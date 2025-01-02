from django.shortcuts import render, redirect
from .models import Product, User, Contact, About, CartItem, Cart, Order, OrderItem, BillingAddress
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .utils import never_cache_custom, user, user_login_required
from django.http import JsonResponse, HttpResponseNotAllowed
import json


# User Registration
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

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(
                request,
                "product_details/register.html",
                {
                    "name": name,
                    "phone": phone,
                    "gender": gender,
                    "age": age,
                },
            )

        # Create a new user
        User.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            gender=gender,
            age=age,
        )
        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    return render(request, "product_details/register.html")

# User Login
@never_cache_custom
@user
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Both email and password are required.")
            return render(request, "product_details/login.html")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return render(request, "product_details/login.html")

        if check_password(password, user.password):
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name
            messages.success(request, f"Welcome, {user.name}!")
            return redirect("home_view")

        messages.error(request, "Invalid email or password.")
    return render(request, "product_details/login.html")

# User Logout
def logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("home_view")

# Home Page
@never_cache_custom
def home_view(request):
    products = Product.objects.all()
    return render(request, "product_details/index.html", {"products": products})

# Add Product
@never_cache_custom
@user_login_required
def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        # Create new product
        Product.objects.create(
            product_name=product_name,
            description=description,
            price=price,
            image=image,
        )
        messages.success(request, "Product added successfully!")
        return redirect("home_view")

    return render(request, "product_details/add_product.html")

# Shop View
@never_cache_custom
def shop_view(request):
    products = Product.objects.all()
    return render(request, "product_details/shop.html", {"products": products})

# Contact Page
@never_cache_custom
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not (name and email and message):
            messages.error(request, "All fields are required.")
            return render(request, "product_details/contact.html")

        # Save contact message
        Contact.objects.create(name=name, email=email, message=message)
        messages.success(request, "Thank you for reaching out!")
        return redirect("home_view")

    return render(request, "product_details/contact.html")

# About Page
@never_cache_custom
def about_view(request):
    about = About.objects.first()
    return render(request, "product_details/about.html", {"about": about})

# View Cart
@never_cache_custom
@user_login_required
def get_cart(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
        cart = Cart.objects.get(user=user)
    except (User.DoesNotExist, Cart.DoesNotExist):
        return redirect("home_view")

    cart_items = cart.cart_items.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(
        request,
        "product_details/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": total_price,
        },
    )

# Add to Cart
@never_cache_custom
@user_login_required
def add_to_cart(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        try:
            user = User.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
            cart, _ = Cart.objects.get_or_create(user=user)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product
            )
            cart_item.quantity += quantity
            cart_item.save()

            messages.success(request, f"{product.product_name} added to cart.")
        except (User.DoesNotExist, Product.DoesNotExist):
            messages.error(request, "Error adding product to cart.")

    return redirect("shop_view")

# Update Cart
@never_cache_custom
@user_login_required
def update_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data["item_id"]
        quantity = data["quantity"]

        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.save()

        # Recalculate cart total
        cart = cart_item.cart
        cart.total_price = sum(
            item.product.price * item.quantity for item in cart.cart_items.all()
        )
        cart.save()

        return JsonResponse(
            {
                "success": True,
                "item_total_price": cart_item.total_price(),
                "cart_total_price": cart.total_price,
            }
        )

    return HttpResponseNotAllowed(["POST"])

# Remove from Cart
@never_cache_custom
@user_login_required
def remove_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        CartItem.objects.filter(id=item_id).delete()
        messages.success(request, "Item removed from cart.")

    return redirect("cart_view")

# Checkout
@never_cache_custom
@user_login_required
def checkout(request):
    user_id = request.session.get("user_id")

    try:
        user = User.objects.get(id=user_id)
        cart = Cart.objects.get(user=user)
    except (User.DoesNotExist, Cart.DoesNotExist):
        return redirect("home_view")

    # Get or create the billing address
    billing_address, created = BillingAddress.objects.get_or_create(user=user)

    if request.method == "POST":
        # Handle form submission for billing address and order creation
        street_address = request.POST.get("street_address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pin_code = request.POST.get("pin_code")
        country = request.POST.get("country")
        contact_number = request.POST.get("contact_number")

        # Update or create billing address
        billing_address.street_address = street_address
        billing_address.city = city
        billing_address.state = state
        billing_address.pin_code = pin_code
        billing_address.country = country
        billing_address.contact_number = contact_number
        billing_address.save()

        # Create the order
        order = Order.objects.create(user=user, total_price=cart.total_price())
        for item in cart.cart_items.all():
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        # Redirect to payment
        return redirect("payment_view", order_id=order.id)

    return render(
        request,
        "product_details/checkout.html",
        {
            "cart": cart,
            "total_price": cart.total_price(),
            "billing_address": billing_address,
        },
    )

def payment_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect("home_view")

    if request.method == "POST":
        # Handle payment processing logic here
        order.status = "Processing"
        order.save()

        # After successful payment, redirect to a success page
        return redirect("order_success", order_id=order.id)

    return render(request, "product_details/payment.html", {"order": order})