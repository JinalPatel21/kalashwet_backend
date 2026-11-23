from django.db import models
from user.models import TimeStampedModel


class Category(TimeStampedModel):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    image = models.CharField(max_length=500, blank=True, null=True)
    image_file = models.ImageField(upload_to='categories/', blank=True, null=True)

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
    image_file = models.ImageField(upload_to='collections/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class HomeBanner(TimeStampedModel):
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=300, blank=True, default='')
    cta = models.CharField(max_length=60, blank=True, default='Shop now')
    link = models.CharField(max_length=500, blank=True, default='/jewellery')
    image = models.ImageField(upload_to='banners/')
    show_on_home = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Home banner'
        verbose_name_plural = 'Home banners'

    def __str__(self):
        return self.title


class DiamondCut(TimeStampedModel):
    name = models.CharField(max_length=80)
    image = models.ImageField(upload_to='diamond-cuts/')
    show_on_home = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

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
    height_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    width_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    depth_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    package_contents = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductMedia(TimeStampedModel):
    class Kind(models.TextChoices):
        PRODUCT = 'product', 'Product image'
        LIFESTYLE = 'lifestyle', 'Lifestyle image'
        DIMENSIONS = 'dimensions', 'Dimensions image'
        PACKAGING = 'packaging', 'Packaging image'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/', max_length=255)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.PRODUCT)
    alt_text = models.CharField(max_length=160, blank=True, default='')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'created_at']
        verbose_name = 'Product gallery image'
        verbose_name_plural = 'Product gallery images'

    def __str__(self):
        return f'{self.product.name} - {self.get_kind_display()}'


class FeaturedProduct(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='home_featured_entries')
    image = models.ImageField(upload_to='featured-products/')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f'Featured: {self.product.name}'


class GiftGuide(TimeStampedModel):
    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to='gift-guides/')
    cta = models.CharField(max_length=60, default='Shop now')
    link = models.CharField(max_length=500, default='/jewellery')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'title']

    def __str__(self):
        return self.title


class JewelleryVideo(TimeStampedModel):
    title = models.CharField(max_length=120)
    video = models.FileField(upload_to='jewellery-videos/', max_length=255)
    thumbnail = models.ImageField(upload_to='jewellery-video-thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'title']
        verbose_name = 'Jewellery video'
        verbose_name_plural = 'Jewellery videos'

    def __str__(self):
        return self.title


class FounderProfile(TimeStampedModel):
    name = models.CharField(max_length=120, default='Dixit Vithani')
    role = models.CharField(max_length=80, default='Founder')
    quote = models.CharField(max_length=255, blank=True, default='')
    story = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='founder/', max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Founder profile'
        verbose_name_plural = 'Founder profile'

    def __str__(self):
        return self.name


class LatestInsight(TimeStampedModel):
    title = models.CharField(max_length=160)
    excerpt = models.CharField(max_length=300, blank=True, default='')
    image = models.ImageField(upload_to='insights/', max_length=255)
    link = models.CharField(max_length=500, blank=True, default='/jewellery')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title


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
