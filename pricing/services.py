from decimal import Decimal, ROUND_HALF_UP

GST_RATE = Decimal('0.03')  # 3% GST on jewellery in India

DEFAULT_RATES = {
    '24K': Decimal('12800'),
    '22K': Decimal('11730'),
    '18K': Decimal('9600'),
    '14K': Decimal('7470'),
    'PT950': Decimal('4200'),
    'S925': Decimal('110'),
}


def get_metal_rate(purity: str) -> Decimal:
    from .models import MetalRate
    rate_obj = MetalRate.objects.filter(purity=purity).first()
    if rate_obj:
        return Decimal(rate_obj.rate_per_gram)
    return DEFAULT_RATES.get(purity, Decimal('10000'))


def compute_variant_price(variant):
    """Computes exact rupee price and transparent breakup for a jewellery variant."""
    rate = get_metal_rate(variant.purity)
    net_weight = Decimal(str(variant.net_weight))
    metal_value = (rate * net_weight).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    making_pct = Decimal(str(getattr(variant, 'making_pct', 15.0))) / Decimal('100')
    making_charges = (metal_value * making_pct).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    # Stone value
    stone_val = Decimal('0')
    if hasattr(variant, 'product') and hasattr(variant.product, 'stones'):
        for s in variant.product.stones.all():
            stone_val += Decimal(str(s.price))

    discount = Decimal(str(getattr(variant, 'discount', 0)))

    taxable = metal_value + making_charges + stone_val - discount
    gst = (taxable * GST_RATE).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    total = int(taxable + gst)

    taxable_mrp = metal_value + making_charges + stone_val
    gst_mrp = (taxable_mrp * GST_RATE).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    mrp = int(taxable_mrp + gst_mrp)

    breakup = {
        'metal_rate_per_gram': int(rate),
        'net_weight': float(net_weight),
        'metal_value': int(metal_value),
        'making_charges': int(making_charges),
        'stone_value': int(stone_val),
        'discount': int(discount),
        'gst_percent': 3,
        'gst': int(gst),
        'total': total,
    }

    return total, mrp, breakup
