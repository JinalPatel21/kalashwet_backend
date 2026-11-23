from rest_framework import serializers
from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import MetalRate


class MetalRateSerializer(MongoModelSerializer):
    rate_per_gram = serializers.IntegerField()

    class Meta:
        model = MetalRate
        fields = ['purity', 'rate_per_gram', 'updated_at']
