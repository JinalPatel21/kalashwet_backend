from django.db import models
from user.models import TimeStampedModel


class Category(TimeStampedModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Collection(TimeStampedModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=255, blank=True, default='')
    image = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    class Gender(models.TextChoices):
        WOMEN = 'women', 'Women'
        MEN = 'men', 'Men'
        KIDS = 'kids', 'Kids'
        UNISEX = 'unisex', 'Unisex'

    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True, default='')
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.WOMEN)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.8)
    review_count = models.IntegerField(default=12)
    badge = models.CharField(max_length=50, blank=True, null=True)  # "Bestseller", "New", etc.
    has_diamonds = models.BooleanField(default=False)
    sizes_available = models.BooleanField(default=True)
    images = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)  # ["BIS Hallmark", "IGI"]
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Variant(TimeStampedModel):
    class Metal(models.TextChoices):
        GOLD = 'gold', 'Gold'
        WHITE_GOLD = 'white_gold', 'White Gold'
        ROSE_GOLD = 'rose_gold', 'Rose Gold'
        PLATINUM = 'platinum', 'Platinum'
        SILVER = 'silver', 'Silver'

    class Purity(models.TextChoices):
        P24K = '24K', '24K'
        P22K = '22K', '22K'
        P18K = '18K', '18K'
        P14K = '14K', '14K'
        PT950 = 'PT950', 'PT950'
        S925 = 'S925', 'S925'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    metal = models.CharField(max_length=30, choices=Metal.choices, default=Metal.GOLD)
    purity = models.CharField(max_length=10, choices=Purity.choices, default=Purity.P22K)
    size = models.CharField(max_length=20, blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=8, decimal_places=3)
    net_weight = models.DecimalField(max_digits=8, decimal_places=3)
    making_pct = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    in_stock = models.BooleanField(default=True)

    class Meta:
        ordering = ['purity', 'size']

    def __str__(self):
        return f'{self.sku} ({self.purity} {self.metal})'


class Stone(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stones')
    stone_type = models.CharField(max_length=50, default='Diamond')
    count = models.IntegerField(default=1)
    carat = models.DecimalField(max_digits=6, decimal_places=3, default=0.0)
    clarity = models.CharField(max_length=20, blank=True, default='SI')
    color = models.CharField(max_length=20, blank=True, default='G-H')
    shape = models.CharField(max_length=30, blank=True, default='Round')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f'{self.stone_type} ({self.carat} ct) on {self.product.name}'
