from decimal import Decimal
from django.db import models
from user.models import TimeStampedModel


class MetalRate(TimeStampedModel):
    class Purity(models.TextChoices):
        P24K = '24K', '24K'
        P22K = '22K', '22K'
        P18K = '18K', '18K'
        P14K = '14K', '14K'
        PT950 = 'PT950', 'PT950'
        S925 = 'S925', 'S925'

    purity = models.CharField(max_length=10, choices=Purity.choices, unique=True)
    rate_per_gram = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['purity']

    def __str__(self):
        return f'{self.purity}: ₹{self.rate_per_gram}/g'


class StoreShippingSettings(TimeStampedModel):
    """One centrally managed delivery charge applied to every store order."""
    key = models.CharField(max_length=20, unique=True, default='default')
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Store shipping settings'
        verbose_name_plural = 'Store shipping settings'

    def __str__(self):
        return f'Shipping fee: ₹{self.shipping_fee}'


class Coupon(TimeStampedModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage'
        FIXED = 'fixed', 'Fixed amount'

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code
