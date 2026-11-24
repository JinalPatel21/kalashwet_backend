import uuid
import requests
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from catalog.models import Variant
from pricing.services import compute_variant_price, evaluate_coupon, get_shipping_fee
from .models import Order
from .notifications import send_order_email
from .serializer import OrderSerializer


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        data = request.data
        items_payload = data.get('items', [])
        if not items_payload or not isinstance(items_payload, list):
            return Response({'items': ['At least one item is required.']}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = data.get('shipping_address')
        if not shipping_address or not isinstance(shipping_address, dict):
            return Response({'shipping_address': ['A valid shipping address is required.']}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = data.get('payment_method', 'razorpay')
        if payment_method not in ('razorpay', 'cod'):
            return Response({'payment_method': ['Unsupported payment method.']}, status=status.HTTP_400_BAD_REQUEST)
        coupon_code = str(data.get('coupon_code', '')).strip().upper()

        # Re-price on the server from variant ids; NEVER trust client prices
        order_items = []
        subtotal = 0

        for item in items_payload:
            variant_id = str(item.get('variant_id', ''))
            quantity = max(1, min(5, int(item.get('quantity', 1))))

            variant = Variant.objects.filter(pk=variant_id).first()
            if not variant:
                return Response({'detail': f'Variant {variant_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            if not variant.in_stock:
                return Response({'detail': f'Variant {variant.sku} is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

            price, _, _ = compute_variant_price(variant)
            subtotal += price * quantity

            product = variant.product
            gallery_image = product.gallery.first()
            images = product.images if isinstance(product.images, list) and product.images else []
            order_image = gallery_image.image.url if gallery_image else (images[0] if images else None)
            if order_image and not order_image.startswith(('http://', 'https://')):
                order_image = request.build_absolute_uri(order_image)

            order_items.append({
                'variant_id': str(variant.pk),
                'product_slug': product.slug,
                'category': product.category.slug,
                'name': product.name,
                'image': order_image,
                'metal': variant.metal,
                'purity': variant.purity,
                'size': variant.size,
                'unit_price': price,
                'quantity': quantity,
            })

        discount = 0
        applied_coupon = ''
        if coupon_code:
            try:
                coupon, discount = evaluate_coupon(coupon_code, subtotal)
                applied_coupon = coupon.code
            except ValueError as exc:
                return Response({'coupon_code': [str(exc)]}, status=status.HTTP_400_BAD_REQUEST)

        shipping = get_shipping_fee()
        total = subtotal - discount + shipping

        # Reject COD above 50,000 INR
        if payment_method == 'cod' and total > 50000:
            return Response({'detail': 'Cash on Delivery is only available for orders up to ₹50,000.'}, status=status.HTTP_400_BAD_REQUEST)

        order_status = Order.Status.CONFIRMED if payment_method == 'cod' else Order.Status.PENDING_PAYMENT
        order_number = f"KW{timezone.now().strftime('%y%m%d')}{str(uuid.uuid4().int)[:4]}"
        razorpay_order_id = ''
        if payment_method == 'razorpay':
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                return Response({'detail': 'Online payments are not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            try:
                gateway_response = requests.post(
                    'https://api.razorpay.com/v1/orders',
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                    json={
                        'amount': int(total * 100),
                        'currency': 'INR',
                        'receipt': f"KW{timezone.now().strftime('%y%m%d')}{str(uuid.uuid4().int)[:8]}",
                    },
                    timeout=10,
                )
                gateway_response.raise_for_status()
                razorpay_order_id = gateway_response.json()['id']
            except (requests.RequestException, KeyError, ValueError):
                return Response({'detail': 'Could not start online payment. Please try again.'}, status=status.HTTP_502_BAD_GATEWAY)

        order = Order.objects.create(
            user=request.user,
            number=order_number,
            status=order_status,
            source=Order.Source.ONLINE_STORE,
            items=order_items,
            subtotal=subtotal,
            discount=discount,
            coupon_code=applied_coupon,
            shipping=shipping,
            total=total,
            shipping_address=shipping_address,
            payment_method=payment_method,
            razorpay_order_id=razorpay_order_id,
            status_history=[{
                'status': order_status,
                'label': order_status.replace('_', ' ').title(),
                'changed_at': timezone.now().isoformat(),
                'changed_by': request.user.name or request.user.email or 'Customer',
            }],
        )
        send_order_email(order, event='placed')

        res_data = OrderSerializer(order).data
        if razorpay_order_id:
            res_data['razorpay_order_id'] = razorpay_order_id
            res_data['razorpay_key_id'] = settings.RAZORPAY_KEY_ID

        return Response(res_data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class CancelOrderView(APIView):
    """Cancel the signed-in customer's order before fulfilment begins."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(pk=pk, user=request.user).first()
            if not order:
                return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
            if order.status not in (Order.Status.PENDING_PAYMENT, Order.Status.CONFIRMED):
                return Response({'detail': 'This order can no longer be cancelled online because fulfilment has progressed.'}, status=status.HTTP_409_CONFLICT)
            if order.razorpay_payment_id:
                return Response({'detail': 'Payment has already been captured. Please contact support to request cancellation and a refund.'}, status=status.HTTP_409_CONFLICT)

            order.status = Order.Status.CANCELLED
            order.status_history = [*(order.status_history or []), {
                'status': Order.Status.CANCELLED,
                'label': 'Cancelled by customer',
                'changed_at': timezone.now().isoformat(),
                'changed_by': request.user.name or request.user.email or 'Customer',
            }]
            order.save(update_fields=['status', 'status_history', 'updated_at'])
            transaction.on_commit(lambda: send_order_email(order, event='status'))
        return Response(OrderSerializer(order).data)
