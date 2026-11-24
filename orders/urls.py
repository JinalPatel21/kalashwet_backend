from django.urls import path
from .views import OrderListCreateView, OrderDetailView, CancelOrderView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<str:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
    path('orders/<str:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
