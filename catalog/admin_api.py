import uuid
from decimal import Decimal
from django.urls import include, path
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone

from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import (
    BrandDifference, Category, Collection, DiamondCut, FeaturedProduct,
    FounderProfile, GiftGuide, HomeBanner, InstagramPost, InstagramProfile,
    JewelleryVideo, LatestInsight, NavigationFeature, Product, ProductMedia,
    Stone, StoreFAQ, Variant,
)
from orders.models import Order
from orders.serializer import OrderSerializer
from orders.notifications import send_order_email
from pricing.models import Coupon, MetalRate
from pricing.services import compute_variant_price, get_shipping_fee
from user.models import User


class AdminModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]


def register_model(router, route, model, label=None):
    meta = type('Meta', (), {
        'model': model,
        'fields': '__all__',
        'read_only_fields': ('id', 'created_at', 'updated_at'),
    })
    serializer = type(f'{model.__name__}AdminSerializer', (MongoModelSerializer,), {'Meta': meta})
    viewset = type(
        f'{model.__name__}AdminViewSet',
        (AdminModelViewSet,),
        {'queryset': model.objects.all(), 'serializer_class': serializer},
    )
    router.register(route, viewset, basename=label or route.replace('/', '-'))


router = DefaultRouter()
register_model(router, 'categories', Category)
register_model(router, 'collections', Collection)
register_model(router, 'products', Product)
register_model(router, 'product-images', ProductMedia)
register_model(router, 'variants', Variant)
register_model(router, 'stones', Stone)
register_model(router, 'banners', HomeBanner)
register_model(router, 'diamond-cuts', DiamondCut)
register_model(router, 'featured-products', FeaturedProduct)
register_model(router, 'gift-guides', GiftGuide)
register_model(router, 'videos', JewelleryVideo)
register_model(router, 'founder', FounderProfile)
register_model(router, 'insights', LatestInsight)
register_model(router, 'brand-differences', BrandDifference)
register_model(router, 'instagram-profile', InstagramProfile)
register_model(router, 'instagram-posts', InstagramPost)
register_model(router, 'faqs', StoreFAQ)
register_model(router, 'navigation-feature', NavigationFeature)


class CouponAdminSerializer(MongoModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'value', 'minimum_order', 'maximum_discount', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        discount_type = attrs.get('discount_type', getattr(self.instance, 'discount_type', Coupon.DiscountType.PERCENTAGE))
        value = attrs.get('value', getattr(self.instance, 'value', None))
        minimum = attrs.get('minimum_order', getattr(self.instance, 'minimum_order', 0))
        maximum = attrs.get('maximum_discount', getattr(self.instance, 'maximum_discount', None))
        if value is not None and value <= 0:
            raise serializers.ValidationError({'value': 'Discount value must be greater than zero.'})
        if discount_type == Coupon.DiscountType.PERCENTAGE and value is not None and value > 100:
            raise serializers.ValidationError({'value': 'Percentage discount cannot exceed 100.'})
        if minimum is not None and minimum < 0:
            raise serializers.ValidationError({'minimum_order': 'Minimum order cannot be negative.'})
        if maximum is not None and maximum <= 0:
            raise serializers.ValidationError({'maximum_discount': 'Maximum discount must be greater than zero.'})
        return attrs


class CouponAdminViewSet(AdminModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponAdminSerializer


router.register('coupons', CouponAdminViewSet, basename='admin-coupons')


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.all()
        return Response({
            'products': Product.objects.count(),
            'categories': Category.objects.count(),
            'orders': orders.count(),
            'pending_orders': orders.filter(status__in=['pending_payment', 'confirmed']).count(),
            'revenue': orders.filter(status__in=['confirmed', 'shipped', 'delivered']).aggregate(total=Sum('total'))['total'] or 0,
        })


class AdminMetalRatesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from pricing.serializer import MetalRateSerializer
        return Response(MetalRateSerializer(MetalRate.objects.all(), many=True).data)

    def post(self, request):
        from pricing.serializer import MetalRateSerializer
        purity = request.data.get('purity')
        instance = MetalRate.objects.filter(purity=purity).first()
        serializer = MetalRateSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED)


class AdminOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().select_related('user').order_by('-created_at')

    def get_serializer_class(self):
        class AdminOrderSerializer(OrderSerializer):
            customer_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
            customer_name = serializers.CharField(source='user.name', read_only=True, allow_null=True)

            class Meta(OrderSerializer.Meta):
                fields = OrderSerializer.Meta.fields + ['customer_email', 'customer_name']
                read_only_fields = fields
        return AdminOrderSerializer

    @action(detail=False, methods=['post'], url_path='draft', parser_classes=[JSONParser])
    def create_draft(self, request):
        """Create an unpaid staff-entered order using centrally priced variants."""
        customer_id = request.data.get('customer_id')
        customer = User.objects.filter(pk=customer_id).first() if customer_id else None
        if customer_id and not customer:
            return Response({'customer_id': ['Choose a registered customer.']}, status=status.HTTP_400_BAD_REQUEST)

        address = request.data.get('shipping_address')
        required_address = ('full_name', 'phone', 'line1', 'city', 'state', 'pincode')
        if not isinstance(address, dict) or any(not str(address.get(key, '')).strip() for key in required_address):
            return Response({'shipping_address': ['Enter the recipient, phone, street, city, state and PIN code.']}, status=status.HTTP_400_BAD_REQUEST)

        lines = request.data.get('items')
        if not isinstance(lines, list) or not lines:
            return Response({'items': ['Add at least one product.']}, status=status.HTTP_400_BAD_REQUEST)

        items = []
        subtotal = Decimal('0')
        for line in lines:
            variant_id = str(line.get('variant_id', '')).strip()
            try:
                quantity = int(line.get('quantity', 1))
            except (TypeError, ValueError):
                quantity = 0
            variant = Variant.objects.filter(pk=variant_id).first()
            if not variant or not variant.product.is_active:
                return Response({'items': [f'Product variant {variant_id or "(missing)"} is unavailable.']}, status=status.HTTP_400_BAD_REQUEST)
            if not variant.in_stock:
                return Response({'items': [f'{variant.sku} is currently out of stock.']}, status=status.HTTP_400_BAD_REQUEST)
            if quantity < 1 or quantity > 5:
                return Response({'items': ['Quantity must be between 1 and 5 per variant.']}, status=status.HTTP_400_BAD_REQUEST)

            price, _, _ = compute_variant_price(variant)
            subtotal += Decimal(str(price)) * quantity
            product = variant.product
            gallery_image = product.gallery.first()
            image = gallery_image.image.url if gallery_image else (product.images[0] if isinstance(product.images, list) and product.images else None)
            if image and not image.startswith(('http://', 'https://')):
                image = request.build_absolute_uri(image)
            items.append({
                'variant_id': str(variant.pk), 'sku': variant.sku,
                'product_slug': product.slug, 'category': product.category.slug,
                'name': product.name, 'image': image, 'metal': variant.metal,
                'purity': variant.purity, 'size': variant.size,
                'unit_price': int(price), 'quantity': quantity,
            })

        now = timezone.now()
        shipping = get_shipping_fee()
        order = Order.objects.create(
            user=customer,
            number=f"KW{now.strftime('%y%m%d')}{str(uuid.uuid4().int)[:4]}",
            status=Order.Status.PENDING_PAYMENT,
            source=Order.Source.DRAFT_ORDER,
            items=items,
            subtotal=int(subtotal),
            discount=0,
            shipping=shipping,
            total=int(subtotal + shipping),
            shipping_address=address,
            payment_method='manual',
            status_history=[{
                'status': Order.Status.PENDING_PAYMENT,
                'label': 'Draft order created',
                'changed_at': now.isoformat(),
                'changed_by': request.user.name or request.user.email or 'Store admin',
            }],
        )
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], parser_classes=[JSONParser])
    def status(self, request, pk=None):
        order = self.get_object()
        next_status = request.data.get('status')
        allowed = {choice for choice, _ in Order.Status.choices}
        if next_status not in allowed:
            return Response({'status': ['Choose a valid order status.']}, status=status.HTTP_400_BAD_REQUEST)
        previous_status = order.status
        transitions = {
            Order.Status.PENDING_PAYMENT: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
            Order.Status.CONFIRMED: {Order.Status.SHIPPED, Order.Status.CANCELLED},
            Order.Status.SHIPPED: {Order.Status.DELIVERED},
            Order.Status.DELIVERED: set(),
            Order.Status.CANCELLED: set(),
        }
        if next_status != previous_status and next_status not in transitions[previous_status]:
            return Response({'status': [f'Cannot move an order from {previous_status.replace("_", " ")} to {next_status.replace("_", " ")} .']}, status=status.HTTP_400_BAD_REQUEST)
        order.status = next_status
        if previous_status != next_status:
            order.status_history = [*(order.status_history or []), {
                'status': next_status,
                'label': dict(Order.Status.choices)[next_status],
                'changed_at': timezone.now().isoformat(),
                'changed_by': request.user.name or request.user.email or 'Store admin',
            }]
            order.save(update_fields=['status', 'status_history', 'updated_at'])
            send_order_email(order, event='status')
        return Response(self.get_serializer(order).data)


router.register('orders', AdminOrdersViewSet, basename='admin-orders')

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('metal-rates/', AdminMetalRatesView.as_view(), name='admin-metal-rates'),
    path('', include(router.urls)),
]
