import re
from decimal import Decimal, InvalidOperation
from rest_framework import generics, pagination, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from pricing.services import compute_variant_price
from .models import Category, Collection, DiamondCut, FeaturedProduct, FounderProfile, GiftGuide, HomeBanner, JewelleryVideo, LatestInsight, Product
from .serializer import (
    CategorySerializer, CollectionSerializer,
    ProductSummarySerializer, ProductDetailSerializer
)


class CatalogPagination(pagination.PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'
    max_page_size = 100


class HomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banners = [
            {
                'id': str(banner.pk),
                'title': banner.title,
                'subtitle': banner.subtitle,
                'cta': banner.cta,
                'link': banner.link,
                'image': request.build_absolute_uri(banner.image.url) if banner.image else None,
            }
            for banner in HomeBanner.objects.filter(show_on_home=True, is_active=True)
            if banner.image
        ]
        diamond_cuts = [
            {
                'id': str(cut.pk),
                'name': cut.name,
                'image': request.build_absolute_uri(cut.image.url),
            }
            for cut in DiamondCut.objects.filter(show_on_home=True, is_active=True)
        ]
        collections = Collection.objects.all()[:8]
        bestsellers = Product.objects.filter(is_active=True, badge='Bestseller').prefetch_related('variants', 'stones', 'gallery')[:8]
        if not bestsellers.exists():
            bestsellers = Product.objects.filter(is_active=True).prefetch_related('variants', 'stones', 'gallery')[:8]
        new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at').prefetch_related('variants', 'stones', 'gallery')[:8]
        featured_products = []
        for item in FeaturedProduct.objects.filter(is_active=True, product__is_active=True).select_related('product').prefetch_related('product__variants', 'product__stones', 'product__gallery')[:8]:
            product_data = ProductSummarySerializer(item.product, context={'request': request}).data
            product_data['images'] = [request.build_absolute_uri(item.image.url)]
            featured_products.append(product_data)
        gift_guides = [
            {'id': str(item.pk), 'title': item.title, 'image': request.build_absolute_uri(item.image.url), 'cta': item.cta, 'link': item.link}
            for item in GiftGuide.objects.filter(is_active=True)
        ]
        jewellery_videos = [
            {
                'id': str(item.pk),
                'title': item.title,
                'video': request.build_absolute_uri(item.video.url),
                'thumbnail': request.build_absolute_uri(item.thumbnail.url) if item.thumbnail else None,
            }
            for item in JewelleryVideo.objects.filter(is_active=True)
        ]
        founder = FounderProfile.objects.filter(is_active=True).first()
        founder_data = None
        if founder:
            founder_data = {
                'name': founder.name,
                'role': founder.role,
                'quote': founder.quote,
                'story': founder.story,
                'image': request.build_absolute_uri(founder.image.url),
            }
        latest_insights = [
            {
                'id': str(item.pk),
                'title': item.title,
                'excerpt': item.excerpt,
                'image': request.build_absolute_uri(item.image.url),
                'link': item.link,
            }
            for item in LatestInsight.objects.filter(is_active=True)[:8]
        ]

        return Response({
            'banners': banners,
            'diamond_cuts': diamond_cuts,
            'featured_collections': CollectionSerializer(collections, many=True).data,
            'featured_products': featured_products,
            'gift_guides': gift_guides,
            'jewellery_videos': jewellery_videos,
            'founder': founder_data,
            'latest_insights': latest_insights,
            'bestsellers': ProductSummarySerializer(bestsellers, many=True, context={'request': request}).data,
            'new_arrivals': ProductSummarySerializer(new_arrivals, many=True, context={'request': request}).data,
        })


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class CollectionListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    pagination_class = None


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSummarySerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).prefetch_related('variants', 'category', 'stones', 'gallery')
        params = self.request.query_params

        # Category filter
        category_slug = params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # Collection filter
        collection_slug = params.get('collection')
        if collection_slug:
            qs = qs.filter(collection__slug=collection_slug)

        # Gender filter (comma separated, unisex matches all)
        gender = params.get('gender')
        if gender:
            genders = [g.strip() for g in gender.split(',') if g.strip()]
            if 'unisex' not in genders:
                genders.append('unisex')
            qs = qs.filter(gender__in=genders)

        # Metal filter (matches any variant)
        metal = params.get('metal')
        if metal:
            metals = [m.strip() for m in metal.split(',') if m.strip()]
            qs = qs.filter(variants__metal__in=metals).distinct()

        # Purity filter (matches any variant)
        purity = params.get('purity')
        if purity:
            purities = [p.strip() for p in purity.split(',') if p.strip()]
            qs = qs.filter(variants__purity__in=purities).distinct()

        # Search filter
        search = params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        # Variant prices are computed dynamically from current metal rates,
        # so filter the matching products by their displayed cheapest price.
        min_raw = params.get('min_price')
        max_raw = params.get('max_price')
        if min_raw is not None or max_raw is not None:
            try:
                min_price = Decimal(min_raw) if min_raw is not None else None
                max_price = Decimal(max_raw) if max_raw is not None else None
                if (min_price is not None and min_price < 0) or (max_price is not None and max_price < 0):
                    raise InvalidOperation
            except InvalidOperation:
                raise ValidationError({'price': 'Enter a valid non-negative price.'})

            matching_ids = []
            for product in qs.prefetch_related('stones'):
                variants = list(product.variants.all())
                available = [variant for variant in variants if variant.in_stock] or variants
                price = min((compute_variant_price(variant)[0] for variant in available), default=0)
                if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                    matching_ids.append(product.pk)
            qs = Product.objects.filter(pk__in=matching_ids)

        # Ordering
        ordering = params.get('ordering', '-created_at')
        if ordering == '-created_at':
            qs = qs.order_by('-created_at')
        elif ordering == '-popularity':
            qs = qs.order_by('-review_count', '-rating')

        return qs


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True).prefetch_related('variants', 'stones', 'category', 'collection', 'gallery')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


class ServiceabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        pincode = request.query_params.get('pincode', '').strip()
        if not re.match(r'^[1-8]\d{5}$', pincode):
            return Response({
                'pincode': pincode,
                'deliverable': False,
                'estimated_days': None,
                'cod_available': False,
            })
        first_digit = int(pincode[0])
        return Response({
            'pincode': pincode,
            'deliverable': True,
            'estimated_days': 3 + (first_digit % 4),
            'cod_available': first_digit < 7,
        })
