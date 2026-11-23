from rest_framework import serializers
from kalashwet_backend.setting.serializer import MongoModelSerializer
from pricing.services import compute_variant_price
from .models import Category, Collection, Product, Variant, Stone


class CategorySerializer(MongoModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'image', 'product_count']


class CollectionSerializer(MongoModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'slug', 'name', 'tagline', 'image']


class StoneSerializer(MongoModelSerializer):
    type = serializers.CharField(source='stone_type')

    class Meta:
        model = Stone
        fields = ['type', 'count', 'carat', 'clarity', 'color', 'shape']


class VariantSerializer(MongoModelSerializer):
    price = serializers.SerializerMethodField()
    mrp = serializers.SerializerMethodField()
    price_breakup = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = [
            'id', 'sku', 'metal', 'purity', 'size',
            'gross_weight', 'net_weight', 'price', 'mrp',
            'price_breakup', 'in_stock'
        ]

    def _get_price_data(self, obj):
        if not hasattr(obj, '_cached_pricing'):
            obj._cached_pricing = compute_variant_price(obj)
        return obj._cached_pricing

    def get_price(self, obj):
        return self._get_price_data(obj)[0]

    def get_mrp(self, obj):
        return self._get_price_data(obj)[1]

    def get_price_breakup(self, obj):
        return self._get_price_data(obj)[2]


class ProductSummarySerializer(MongoModelSerializer):
    category = serializers.CharField(source='category.slug')
    price = serializers.SerializerMethodField()
    mrp = serializers.SerializerMethodField()
    metal = serializers.SerializerMethodField()
    purity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'category', 'images',
            'price', 'mrp', 'metal', 'purity',
            'rating', 'review_count', 'badge', 'has_diamonds', 'gender'
        ]

    def _get_cheapest_variant(self, obj):
        if not hasattr(obj, '_cheapest_variant'):
            variants = list(obj.variants.filter(in_stock=True)) or list(obj.variants.all())
            cheapest = None
            lowest_price = float('inf')
            for v in variants:
                price, mrp, _ = compute_variant_price(v)
                v._computed_price = price
                v._computed_mrp = mrp
                if price < lowest_price:
                    lowest_price = price
                    cheapest = v
            obj._cheapest_variant = cheapest
        return obj._cheapest_variant

    def get_price(self, obj):
        v = self._get_cheapest_variant(obj)
        return getattr(v, '_computed_price', 0) if v else 0

    def get_mrp(self, obj):
        v = self._get_cheapest_variant(obj)
        return getattr(v, '_computed_mrp', 0) if v else 0

    def get_metal(self, obj):
        v = self._get_cheapest_variant(obj)
        return v.metal if v else 'gold'

    def get_purity(self, obj):
        v = self._get_cheapest_variant(obj)
        return v.purity if v else '22K'


class ProductDetailSerializer(ProductSummarySerializer):
    collection = serializers.CharField(source='collection.slug', allow_null=True)
    variants = VariantSerializer(many=True, read_only=True)
    stones = StoneSerializer(many=True, read_only=True)

    class Meta(ProductSummarySerializer.Meta):
        fields = ProductSummarySerializer.Meta.fields + [
            'description', 'collection', 'variants', 'stones',
            'certifications', 'sizes_available'
        ]
