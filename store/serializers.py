from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Order, OrderItem


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image_url']


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'full_name', 'phone', 'address_line', 'city', 'state',
            'pincode', 'payment_method', 'status', 'total_amount',
            'created_at', 'items',
        ]
        read_only_fields = ['status', 'total_amount', 'created_at']


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=500)
    items = OrderItemInputSerializer(many=True)
