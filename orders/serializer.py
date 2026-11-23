from rest_framework import serializers
from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import Order


class OrderSerializer(MongoModelSerializer):
    subtotal = serializers.IntegerField()
    discount = serializers.IntegerField()
    shipping = serializers.IntegerField()
    total = serializers.IntegerField()

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'status', 'created_at', 'items',
            'subtotal', 'discount', 'shipping', 'total',
            'shipping_address', 'payment_method'
        ]
