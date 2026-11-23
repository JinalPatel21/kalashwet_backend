import re
from rest_framework import generics, pagination, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Collection, Product
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
                'id': 'banner-1',
                'title': 'The Royal Noorani Collection',
                'subtitle': 'Handcrafted temple jewellery in 22K pure hallmarked gold with uncut polki diamonds.',
                'cta': 'Explore Noorani',
                'link': '/jewellery?collection=royal-heritage',
                'image': None,
            },
            {
                'id': 'banner-2',
                'title': 'Timeless Solitaires',
                'subtitle': 'Certified natural diamond engagement rings, made to shine forever.',
                'cta': 'Shop Solitaires',
                'link': '/jewellery/rings',
                'image': None,
            },
        ]
        collections = Collection.objects.all()[:4]
        bestsellers = Product.objects.filter(is_active=True, badge='Bestseller')[:8]
        if not bestsellers.exists():
            bestsellers = Product.objects.filter(is_active=True)[:8]
        new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

        return Response({
            'banners': banners,
            'featured_collections': CollectionSerializer(collections, many=True).data,
            'bestsellers': ProductSummarySerializer(bestsellers, many=True).data,
            'new_arrivals': ProductSummarySerializer(new_arrivals, many=True).data,
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
        qs = Product.objects.filter(is_active=True).prefetch_related('variants', 'category')
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

        # Ordering
        ordering = params.get('ordering', '-created_at')
        if ordering == '-created_at':
            qs = qs.order_by('-created_at')
        elif ordering == '-popularity':
            qs = qs.order_by('-review_count', '-rating')

        return qs


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True).prefetch_related('variants', 'stones', 'category', 'collection')
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
