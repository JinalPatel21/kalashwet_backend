from django.db import models
from user.models import TimeStampedModel


class Payment(TimeStampedModel):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='razorpay')
    provider_order_id = models.CharField(max_length=100, blank=True, default='')
    provider_payment_id = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=30, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    raw_response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.provider} Payment ({self.status}) for Order {self.order.number}'
