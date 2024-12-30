from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # User Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    
    # Home and About
    path("", views.home_view, name="home_view"),
    path("about/", views.about_view, name="about_view"),
    
    # Products
    path("add_product/", views.add_product, name="add_product"),
    path("shop/", views.shop_view, name="shop"),
    
    # Contact
    path("contact/", views.contact, name="contact"),
    
    # Cart
    path("cart/", views.get_cart, name="cart_view"),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)