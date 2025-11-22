from django.contrib import admin
from .models import Product, Cart, CartItem, Transaction


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_code', 'user', 'paid', 'created_at')
    inlines = [CartItemInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("ref", "user", "status", "amount", "created_at")
    readonly_fields = ("ordered_products",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category")
admin.site.register(CartItem)   # Optional


