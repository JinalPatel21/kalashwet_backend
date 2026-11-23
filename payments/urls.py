from django.urls import path
from .views import RazorpayVerifyView

urlpatterns = [
    path('payments/razorpay/verify/', RazorpayVerifyView.as_view(), name='razorpay-verify'),
]
