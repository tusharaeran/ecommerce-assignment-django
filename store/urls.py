from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.MyOrdersView.as_view(), name='my-orders'),
]
