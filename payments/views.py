import hashlib
import hmac

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order
from orders.serializer import OrderSerializer
from .models import Payment


class RazorpayVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')

        order = Order.objects.filter(pk=order_id, user=request.user).first()
        if not order:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.Status.PENDING_PAYMENT:
            return Response({'detail': 'Order is not awaiting payment.'}, status=status.HTTP_409_CONFLICT)
        if (not payment_id or not signature or not settings.RAZORPAY_KEY_SECRET
                or not razorpay_order_id or razorpay_order_id != order.razorpay_order_id):
            return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        message = f'{razorpay_order_id}|{payment_id}'.encode()
        expected = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), message, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = Order.Status.CONFIRMED
        order.razorpay_payment_id = payment_id
        order.save()

        Payment.objects.create(
            order=order,
            provider='razorpay',
            provider_order_id=razorpay_order_id,
            provider_payment_id=payment_id,
            status='success',
            amount=order.total,
            raw_response={'razorpay_order_id': razorpay_order_id, 'razorpay_payment_id': payment_id},
        )

        return Response(OrderSerializer(order).data)
