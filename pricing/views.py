from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal, InvalidOperation
from .models import MetalRate, StoreShippingSettings
from .serializer import MetalRateSerializer, StoreShippingSettingsSerializer
from .services import DEFAULT_RATES, evaluate_coupon


class MetalRateListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = MetalRate.objects.all()
    serializer_class = MetalRateSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        # If rates are not yet seeded in DB, seed them from defaults
        if not MetalRate.objects.exists():
            for purity, rate in DEFAULT_RATES.items():
                MetalRate.objects.get_or_create(purity=purity, defaults={'rate_per_gram': rate})
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StoreShippingSettingsView(generics.GenericAPIView):
    serializer_class = StoreShippingSettingsSerializer

    def get_permissions(self):
        return [AllowAny()] if self.request.method == 'GET' else [IsAdminUser()]

    def get_object(self):
        settings, _ = StoreShippingSettings.objects.get_or_create(key='default')
        return settings

    def get(self, request):
        return Response(self.get_serializer(self.get_object()).data)

    def patch(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CouponValidationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = str(request.data.get('code', '')).strip()
        if not code:
            return Response({'detail': 'Enter a coupon code.'}, status=400)
        try:
            subtotal = Decimal(str(request.data.get('subtotal', '')))
        except (InvalidOperation, TypeError, ValueError):
            return Response({'detail': 'Enter a valid order subtotal.'}, status=400)
        if not subtotal.is_finite() or subtotal < 0:
            return Response({'detail': 'Enter a valid order subtotal.'}, status=400)
        try:
            coupon, discount = evaluate_coupon(code, subtotal)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'coupon_code': coupon.code, 'discount': discount, 'message': f'Coupon {coupon.code} applied.'})
