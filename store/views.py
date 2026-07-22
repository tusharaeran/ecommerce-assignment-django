from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Order, OrderItem
from .serializers import (
    SignupSerializer, ProductSerializer, OrderSerializer, CheckoutSerializer,
)


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'detail': 'Username already taken.'}, status=400)
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=401)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CheckoutView(APIView):
    """
    Accepts shipping address + cart items, creates an Order (COD) with
    OrderItems, and returns a confirmation payload.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        items_data = data.pop('items')
        product_ids = [item['product_id'] for item in items_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        missing = [pid for pid in product_ids if pid not in products]
        if missing:
            return Response(
                {'detail': f'Product(s) not found: {missing}'}, status=400
            )

        total = Decimal('0.00')
        for item in items_data:
            product = products[item['product_id']]
            total += product.price * item['quantity']

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.username,
            address_line=data['address'],
            payment_method='COD',
            status='placed',
            total_amount=total,
        )

        for item in items_data:
            product = products[item['product_id']]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item['quantity'],
            )

        return Response(
            {
                'message': 'Order placed successfully! You will pay via Cash on Delivery.',
                'order': OrderSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
