from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CreateCartView

urlpatterns = [
    path("products/", views.products, name="products"),
    path("product_detail/<slug:slug>/", views.product_detail, name="product_detail"),
    path('products/<str:slug>/related/', views.related_products),
    path("related_products", views.related_products, name="related_products"),
    path("add_item/", views.add_item, name="add_item"),
    path("product_in_cart", views.product_in_cart, name="product_in_cart"),
    path("get_cart_stat", views.get_cart_stat, name="get_cart_stat"),
    path("get_cart", views.get_cart, name="get_cart"),
    path('delete_cartitem/', views.delete_cartitem),
    path('update_quantity/', views.update_quantity), 
    path("get_username", views.get_username, name="get_username"),
    path("user_info", views.user_info, name="user_info"),
    path('shop/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('shop/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('create_cart/', CreateCartView.as_view(), name='create_cart'),
    path('initiate_payment/', views.initiate_payment, name="initiate_payment"),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('signup/', views.signup, name="signup/"),
    path('update_profile/', views.update_profile, name="update_profile")
]

# fetching all_products: http://127.0.0.1:8001/shop/products/

