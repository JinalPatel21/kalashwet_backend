from rest_framework import serializers
from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import MetalRate, StoreShippingSettings


class MetalRateSerializer(MongoModelSerializer):
    rate_per_gram = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = MetalRate
        fields = ['purity', 'rate_per_gram', 'updated_at']


class StoreShippingSettingsSerializer(MongoModelSerializer):
    shipping_fee = serializers.IntegerField(min_value=0)

    class Meta:
        model = StoreShippingSettings
        fields = ['shipping_fee', 'updated_at']
