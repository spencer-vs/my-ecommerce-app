from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import uuid
import random
import string
import requests

# Create your models here.

# def generate_cart_code():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=11))  

def generate_cart_code(length=20):
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not Cart.objects.filter(cart_code=code).exists():
            return code
        


class Product(models.Model):
    CATEGORY = (
        ("Electronics", "ELECTRONICS"),
        ("Groceries", "GROCERIES"),
        ("Clothing", "CLOTHING")
    )
    
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    image = models.ImageField(upload_to="img")
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=15, choices=CATEGORY, blank=True, null=True)
    
    
    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        
        
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug 
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
            
        
        # if self.image and not self.image.name.startswith('http'):
        #     old_image = self.image
        #     self.image = old_image    
            
            
        super().save(*args, **kwargs)
        
        def __str__(self):
         return self.name


class Cart(models.Model):
    cart_code = models.CharField(max_length=20, unique=True, default=generate_cart_code)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    def __str__(self):
        return self.cart_code
    
    
  


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # ← Fixed: added )
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"
    

class Transaction(models.Model):
    ref = models.CharField(max_length=255, unique=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="NGN")
    status = models.CharField(max_length=20, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
   
    
    def __str__(self):
        return f"Transaction {self.ref} - {self.status}"
    
   
    
    
    @property
    def ordered_products(self):
        return ", ".join(
        f"{item.quantity} × {item.product.name}"
        for item in self.cart.items.all()
        )
    
    
    
    
