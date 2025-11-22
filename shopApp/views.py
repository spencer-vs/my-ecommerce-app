from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from .models import Product, Cart, CartItem, Transaction, generate_cart_code
from .serializers import DetailedProductSerializer, CartItemSerializer, UserSerializer,  ProductSerializer, SimpleCartSerializer, CartSerializer, SignupSerializer, UpdateProfileSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from decimal import Decimal
import uuid
from django.conf import settings
import requests
import traceback
from datetime import timedelta
import random
import string

BASE_URL = settings.REACT_BASE_URL

User = get_user_model()



@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Profile updated succesfully", "user": serializer.data})
    return Response(serializer.errors, status=400)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_username(request):
    user= request.user
    return Response({"username": request.user.username})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def test_token(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return Response({"error": "No Bearer token"}, status=400)
   
    token = auth.split(' ')[1]
    try:
        decoded = AccessToken(token)
        user = User.objects.get(id=decoded['user_id'])
        return Response({"valid": True, "user_id": user.id, "username": user.username})
    except Exception as e:
        return Response({"valid": False, "error": str(e)}, status=401)








    
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def create_cart(request):
#     user = request.user if request.user.is_authenticated else None
#     if user:
#         # Logged-in user: get or create their unpaid cart
#         cart, created = Cart.objects.get_or_create(user=user, paid=False)
#     else:
#         # Guest: create a cart without user
#         cart = Cart.objects.create()
#     # Always return cart_code
#     return Response({"cart_code": cart.cart_code}, status=201)

@api_view(['GET'])
@permission_classes([AllowAny])
def related_products(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        related = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        serializer = DetailedProductSerializer(related, many=True)
        return Response({
            'similar_products': serializer.data
        })
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)






@api_view(["GET"])
@permission_classes([AllowAny])
def products(request):
    # Fetch all product records
    products = Product.objects.all()
   
    # Serialize them
    serializer = ProductSerializer(products, many=True)
   
    # Return valid HTTP response
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = DetailedProductSerializer(product)
    return Response(serializer.data)
    
    
    
    
    
    # print(f"Fetching product with slug: {slug}")
    # product = get_object_or_404(Product, slug=slug)
   
    # data = {
    #     "id": product.id,
    #     "name": product.name,
    #     "slug": product.slug,
    #     "image": product.image.url if product.image else None,
    #     "price": float(product.price),
    #     "description": product.description,
    #     "in_cart": False  # Frontend will update this
    # }
   
    # return Response(data)
    
    


@api_view(["GET"])
@permission_classes([AllowAny])
def product_in_cart(request):
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")
    
    
    cart = Cart.objects.get(cart_code=cart_code)
    product = Product.objects.get(id=product_id)
    
    product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()
    
    return Response({"product_in_cart": product_exists_in_cart})
    
    # if not cart_code or not product_id:
    #     return Response({"error": "Missingparams"}, status=400)
    
    # try: 
    #     cart = Cart.objects.get(cart_code=cart_code, paid=False)
    #     product = Product.objects.get(id=product_id)
    #     item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    #     return Response({"in_cart": bool(item)})
    # except Cart.DoesNotExist:
    #     return Response({'in_cart': False})
    
  
    
    
    
@api_view(["GET"])
@permission_classes([AllowAny])
def get_cart_stat(request):
    cart_code = request.query_params.get("cart_code")
    
    if not cart_code:
        return Response({"num_of_items": 0})
    
    
    try:
       cart = Cart.objects.get(cart_code=cart_code, paid=False)
       count = cart.items.count()
       return Response({"num_of_items": count})
    #    serializer = SimpleCartSerializer(cart)
    
    except Cart.DoesNotExist:
        return Response({'num_of_items': 0})
    
    
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    cart_code = request.GET.get("cart_code")
    if request.user.is_authenticated:
        # Logged-in user always has at most ONE unpaid cart
        cart = Cart.objects.filter(user=request.user, paid=False).first()
        if not cart:
            cart = Cart.objects.create(
                user=request.user,
                cart_code=generate_cart_code()
            )
    else:
        # ----------- GUEST USER -----------
        if cart_code:
            # First: try to get the cart, paid or unpaid
            cart = Cart.objects.filter(cart_code=cart_code).first()
            # If it exists but is paid → create NEW cart
            if cart and cart.paid:
                cart = Cart.objects.create(cart_code=generate_cart_code())
            # If it does NOT exist → create it
            if not cart:
                cart = Cart.objects.create(cart_code=cart_code)
        else:
            # No cart_code provided → generate new cart
            cart = Cart.objects.create(cart_code=generate_cart_code())
    # Serialize items
    items = cart.items.all()
    serializer = CartItemSerializer(items, many=True)
    return Response({
        "cart_code": cart.cart_code,
        "items": serializer.data,
        "num_of_items": sum(item.quantity for item in items),
        "sum_total": sum(item.product.price * item.quantity for item in items),
    })



@api_view(["POST"])
@permission_classes([AllowAny])
def add_item(request):
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    cart_code = request.data.get("cart_code")
    # If no cart_code is sent → generate a new one
    if not cart_code:
        cart_code = generate_cart_code()
    # Try to fetch ANY cart with that cart_code
    cart = Cart.objects.filter(cart_code=cart_code).first()
    # If cart exists but is paid → create a NEW cart with a NEW code
    if cart and cart.paid:
        cart = Cart.objects.create(
            cart_code=generate_cart_code(),
            user=request.user if request.user.is_authenticated else None
        )
    # If the cart does not exist → create it
    if not cart:
        cart = Cart.objects.create(
            cart_code=cart_code,
            user=request.user if request.user.is_authenticated else None
        )
    # Add or update item
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()
    return Response({
        "cart_code": cart.cart_code,
        "message": "Item added"
    })






@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_quantity(request):
    try:
        cartitem_id = request.data.get("item_id")
        quantity = request.data.get("quantity")
        quantity = int(quantity)
        cartitem = CartItem.objects.get(id=cartitem_id)
        cartitem.quantity = quantity
        cartitem.save()
        serializer = CartItemSerializer(cartitem)
        return Response({"data":serializer.data, "message": "Cartitem updated succesfully!"})
    
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
    
@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_cartitem(request):
    cartitem_id = request.data.get("item_id")
    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.delete()
    return Response({"message:" "item deleted succesfully"}, status=status.HTTP_204_NO_CONTENT)





    
    
class CreateCartView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        cart_code = request.data.get('cart_code')
        return Response({
            "message": "Cart Created",
            "cart_code": cart_code,
            "user": user.username
        }, status=status.HTTP_201_CREATED)
        
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    cart_code = request.data.get("cart_code")
    if not cart_code:
        return Response({"error": "cart_code required"}, status=400)
    try:
        cart = Cart.objects.get(cart_code=cart_code, paid=False)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)
    # Calculate total
    total = sum(item.quantity * item.product.price for item in cart.items.all())
    tx_ref = f"shoppit-{generate_cart_code()}"
    # Handle authenticated users
    user = request.user if request.user.is_authenticated else None
    if user:
        Transaction.objects.create(
            ref=tx_ref,
            cart=cart,
            user=user,
            amount=total,
            currency="NGN",
            status="pending"
        )
    # Flutterwave payload
    payload = {
        "tx_ref": tx_ref,
        "amount": str(total),
        "currency": "NGN",
        "redirect_url": f"{settings.BASE_URL}/payment-status/",
        "customer": {
            "email": user.email if user else "guest@example.com",
            "name": user.username if user else "Guest"
        }
    }
    response = requests.post(
        "https://api.flutterwave.com/v3/payments",
        json=payload,
        headers={"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    )
    data = response.json()
    if data.get('status') == 'success':
        return Response({
            "link": data['data']['link'],
            "tx_ref": tx_ref
        })
    else:
        return Response(data, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # <--- FIXED
def payment_callback(request):
    status = request.GET.get("status")
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")
    print("CALLBACK DATA:", request.GET)
    if status not in ["success", "successful"]:
        return Response({"error": "Payment not successful"}, status=400)
    if not tx_ref or not transaction_id:
        return Response({"error": "Missing tx_ref or transaction_id"}, status=400)
    # Match your own DB record using tx_ref
    try:
        transaction = Transaction.objects.get(ref=tx_ref)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)
    # Verify with Flutterwave
    verify_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}
    resp = requests.get(verify_url, headers=headers).json()
    print("FLW VERIFY RESPONSE:", resp)
    if resp.get("status") == "success":
        data = resp.get("data", {})
        # Confirm amount and status
        if (
            float(data.get("amount", 0)) == float(transaction.amount)
            and data.get("status") in ["success", "successful"]
        ):
            transaction.status = "completed"
            transaction.save()
            cart = transaction.cart
            cart.paid = True
            cart.save()
            return Response({
                "message": "Payment successful!",
                "subMessage": "You have successfully made your payment."
            })
    return Response({"error": "Verification failed"}, status=400)

