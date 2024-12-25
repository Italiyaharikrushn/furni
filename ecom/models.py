import uuid
from django.db import models

def get_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"profile_images/{filename}"

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=get_image_upload_to)

    def __str__(self):
        return self.product_name

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=14)
    password = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        default="Select",
    )
    age = models.PositiveIntegerField()
    profession = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.phone.startswith("+91-"):
            self.phone = f"+91-{self.phone}"
        super().save(*args, **kwargs)

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.email})"

class About(models.Model):
    image = models.ImageField(upload_to=get_image_upload_to, blank=True, null=True)
    about_text = models.TextField()

    def __str__(self):
        return "About Us"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.name} - {self.id}"

    def total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.product_name}'
