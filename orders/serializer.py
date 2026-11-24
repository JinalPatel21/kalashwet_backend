from rest_framework import serializers
from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import Order


class OrderSerializer(MongoModelSerializer):
    subtotal = serializers.IntegerField()
    discount = serializers.IntegerField()
    shipping = serializers.IntegerField()
    total = serializers.IntegerField()
    can_cancel = serializers.SerializerMethodField()

    def get_can_cancel(self, obj):
        return obj.status in (Order.Status.PENDING_PAYMENT, Order.Status.CONFIRMED) and not obj.razorpay_payment_id

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'status', 'source', 'status_history', 'created_at', 'updated_at', 'items',
            'subtotal', 'discount', 'coupon_code', 'shipping', 'total',
            'shipping_address', 'payment_method', 'can_cancel'
        ]
