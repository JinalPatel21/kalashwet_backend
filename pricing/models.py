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
