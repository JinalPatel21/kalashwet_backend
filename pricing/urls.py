from django.urls import path
from .views import CouponValidationView, MetalRateListView, StoreShippingSettingsView

urlpatterns = [
    path('metal-rates/', MetalRateListView.as_view(), name='metal-rates'),
    path('shipping-settings/', StoreShippingSettingsView.as_view(), name='shipping-settings'),
    path('coupons/validate/', CouponValidationView.as_view(), name='coupon-validate'),
]
