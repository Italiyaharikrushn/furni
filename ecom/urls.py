from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('shop/', views.shop_view, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about_view, name='about_view'),
    path('view/', views.cart_view, name='cart_view'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
