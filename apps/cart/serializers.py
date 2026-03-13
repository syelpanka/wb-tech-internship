from rest_framework import serializers
from apps.products.serializers import ProductSerializer
from .models import CartItem
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'total_price')

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value

    def validate(self, data):
        product = Product.objects.get(pk=data['product_id'])
        if data['quantity'] > product.stock:
            raise serializers.ValidationError("Not enough stock")
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
