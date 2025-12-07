from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import Cart, CartItem
from django.shortcuts import get_object_or_404
from .serializers import (
    CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer
)
from .services import ProductService
import logging

logger = logging.getLogger(__name__)


class IsAuthenticatedCustom:
    """Check whether the user is set by middleware or not."""

    def has_permission(self, request, view):
        return (
            hasattr(request, 'user_id') and request.user_id is not None
        )


class CartView(generics.RetrieveAPIView):
    """Obtaining the cart for the user."""

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedCustom]

    def get_object(self):
        logger.info(
            f"Getting cart for user {self.request.user_id}"
        )
        cart, created = Cart.objects.get_or_create(
            user_id=self.request.user_id
        )

        if created:
            logger.info(
                f"Cart created for user {self.request.user_id}"
            )
        return cart


@api_view(['POST'])
@permission_classes([IsAuthenticatedCustom])
def add_to_cart(request):
    """Adding a product to the cart."""

    logger.info(
        f"Adding product to cart for user {request.user_id}: {request.data}"
    )

    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        """Obtaining the cart for the user."""
        cart, created = Cart.objects.get_or_create(
            user_id=request.user_id
        )
        logger.info(
            f"Cart obtained for user {request.user_id}: {'created' if created else 'found'}"
        )

        """Checking if the product is already in the cart."""
        if not ProductService.check_availability(product_id, quantity):
            logger.warning(
                f"Product {product_id} is not available in the requested quantity - {quantity}"
            )
            return Response(
                {"error": "Product is not available is requested quantity"},
                status=status.HTTP_400_BAD_REQUEST)
        
        """Getting the product details."""
        product_data = ProductService.get_product(product_id)
        if not product_data:
            logger.warning(
                f"Product {product_id} not found"
            )
            return Response(
                {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND)
        
        """Adding or updating the product in the cart."""
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id,
            defaults={
                "quantity": quantity, 
                "price": product_data["price"],
                "product_name": product_data["name"] 
            }
        )

        if not created:
            """If the product is already in the cart, updating the quantity."""

            new_quantity = cart_item.quantity + quantity
            if not ProductService.check_availability(product_id, new_quantity):
                return Response({
                    "error": "Product is not available in the requested quantity"
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()
            logger.info(
                f"Updated cart item {cart_item.id} quantity to {new_quantity}"
            )
        else:
            logger.info(
                f"Created new cart item {cart_item.id} to cart {cart.id}"
            )

        return Response(
            {
                "message": "Product added to cart successfully",
                "cart_item": CartItemSerializer(cart_item).data
            }, status=status.HTTP_201_CREATED)
    
    logger.error(
        f"Invalid data: {serializer.errors}"
    )
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticatedCustom])
def update_cart_item(request, item_id):
    """Updating the quantity of a product in the cart."""
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user_id=request.user_id
    )

    serializer = UpdateCartItemSerializer(data=request.data)
    if serializer.is_valid():
        new_quantity = serializer.validated_data['quantity']

        """Checking if the product is available in the requested quantity."""
        if not ProductService.check_availability(
            cart_item.product_id, new_quantity
        ):
            return Response(
                {
                    "error": "Product is not available in the requested quantity"
                }, status=status.HTTP_400_BAD_REQUEST
            )  
        
        cart_item.quantity = new_quantity
        cart_item.save()

        return Response(
            {
                "message": "Cart item updated successfully",
                "cart_item": CartItemSerializer(cart_item).data
            }
        )
    
    return Response(
        serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedCustom])
def remove_cart_item(request, item_id):
    """Removing a product from the cart."""
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user_id=request.user_id
    )
    cart_item.delete()
    return Response(
        {
            "message": "Product removed from cart successfully"
        }, status=status.HTTP_204_NO_CONTENT
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedCustom])
def clear_cart(request):
    """Clearing the cart."""
    try:
        cart = Cart.objects.get(user_id=request.user_id)
        cart.clear()

        return Response(
            {
                "message": "Cart cleared successfully"
            }, status=status.HTTP_204_NO_CONTENT
        )
    except Cart.DoesNotExist:
        return Response(
            {
                "message": "Cart is already empty"
            }, status=status.HTTP_204_NO_CONTENT
        )
    

@api_view(['GET'])
@permission_classes([IsAuthenticatedCustom])
def cart_summary(request):
    """Crafting a summary of the cart."""
    try:
        cart = Cart.objects.get(user_id=request.user_id)
        return Response(
            {
                "total_items": cart.total_items,
                "total_amount": cart.total_amount,
                "items_count": cart.items_count(),
            }
        )
    except Cart.DoesNotExist:
        return Response(
            {
                "total_items": 0,
                "total_amount": 0,
                "items_count": 0,
            })