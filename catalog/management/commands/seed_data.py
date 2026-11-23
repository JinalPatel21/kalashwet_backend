import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from pricing.models import MetalRate
from pricing.services import DEFAULT_RATES
from catalog.models import Category, Collection, Product, Variant, Stone


class Command(BaseCommand):
    help = 'Seeds initial fine jewellery catalogue data for Kalashwet'

    def handle(self, *args, **options):
        self.stdout.write('Seeding metal rates...')
        for purity, rate in DEFAULT_RATES.items():
            MetalRate.objects.update_or_create(
                purity=purity,
                defaults={'rate_per_gram': rate}
            )

        self.stdout.write('Seeding categories...')
        categories_data = [
            ('rings', 'Rings'),
            ('earrings', 'Earrings'),
            ('necklaces', 'Necklaces'),
            ('pendants', 'Pendants'),
            ('bangles', 'Bangles'),
            ('bracelets', 'Bracelets'),
            ('mangalsutra', 'Mangalsutra'),
            ('nose-pins', 'Nose Pins'),
            ('chains', 'Chains'),
        ]
        cat_objs = {}
        for slug, name in categories_data:
            cat, _ = Category.objects.update_or_create(slug=slug, defaults={'name': name})
            cat_objs[slug] = cat

        self.stdout.write('Seeding collections...')
        collections_data = [
            ('kalash', 'The Kalash Edit', 'Temple motifs, reimagined for everyday'),
            ('solitaire', 'Solitaire Stories', 'One stone. Forever.'),
            ('bridal', 'Vivaah Bridal', 'Heirlooms for your big day'),
            ('office-wear', 'Everyday Minimal', 'Light pieces under 5 grams'),
        ]
        col_objs = {}
        for slug, name, tagline in collections_data:
            col, _ = Collection.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'tagline': tagline}
            )
            col_objs[slug] = col

        self.stdout.write('Seeding sample products...')
        catalog_sample = [
            {
                'name': 'Mira Solitaire Diamond Ring',
                'slug': 'mira-solitaire-diamond-ring',
                'category': 'rings',
                'collection': 'solitaire',
                'description': 'A brilliant-cut natural solitaire diamond set in pure 18K gold. Graceful, timeless, and certified by IGI.',
                'gender': 'women',
                'rating': Decimal('4.9'),
                'review_count': 38,
                'badge': 'Bestseller',
                'has_diamonds': True,
                'sizes_available': True,
                'certifications': ['BIS Hallmark', 'IGI Certified'],
                'images': [],
                'variants': [
                    {'sku': 'KW-MIRA-18K-10', 'metal': 'gold', 'purity': '18K', 'size': '10', 'gross': '3.2', 'net': '3.1', 'making': '14.0', 'discount': '500'},
                    {'sku': 'KW-MIRA-18K-12', 'metal': 'gold', 'purity': '18K', 'size': '12', 'gross': '3.4', 'net': '3.3', 'making': '14.0', 'discount': '500'},
                    {'sku': 'KW-MIRA-14K-10', 'metal': 'gold', 'purity': '14K', 'size': '10', 'gross': '3.0', 'net': '2.9', 'making': '14.0', 'discount': '400'},
                ],
                'stones': [
                    {'stone_type': 'Natural Diamond', 'count': 1, 'carat': '0.35', 'clarity': 'VVS1', 'color': 'F-G', 'shape': 'Round Brilliant', 'price': '28000'}
                ]
            },
            {
                'name': 'Aarohi Floral Stud Earrings',
                'slug': 'aarohi-floral-stud-earrings',
                'category': 'earrings',
                'collection': 'office-wear',
                'description': 'Delicate floral studs in 18K rose gold encrusted with pavé natural diamonds.',
                'gender': 'women',
                'rating': Decimal('4.8'),
                'review_count': 24,
                'badge': 'Trending',
                'has_diamonds': True,
                'sizes_available': False,
                'certifications': ['BIS Hallmark', 'IGI Certified'],
                'images': [],
                'variants': [
                    {'sku': 'KW-AAROHI-18K-RG', 'metal': 'rose_gold', 'purity': '18K', 'size': None, 'gross': '2.8', 'net': '2.7', 'making': '15.0', 'discount': '300'},
                    {'sku': 'KW-AAROHI-14K-RG', 'metal': 'rose_gold', 'purity': '14K', 'size': None, 'gross': '2.6', 'net': '2.5', 'making': '15.0', 'discount': '250'},
                ],
                'stones': [
                    {'stone_type': 'Natural Diamond', 'count': 12, 'carat': '0.18', 'clarity': 'SI', 'color': 'G-H', 'shape': 'Round', 'price': '14200'}
                ]
            },
            {
                'name': 'Royal Temple Kasu Necklace',
                'slug': 'royal-temple-kasu-necklace',
                'category': 'necklaces',
                'collection': 'bridal',
                'description': 'Traditional South Indian temple Lakshmi Kasu necklace handcrafted in solid 22K yellow gold.',
                'gender': 'women',
                'rating': Decimal('5.0'),
                'review_count': 19,
                'badge': 'Bestseller',
                'has_diamonds': False,
                'sizes_available': False,
                'certifications': ['BIS Hallmark'],
                'images': [],
                'variants': [
                    {'sku': 'KW-KASU-22K', 'metal': 'gold', 'purity': '22K', 'size': None, 'gross': '28.5', 'net': '28.5', 'making': '12.0', 'discount': '2500'},
                ],
                'stones': []
            },
            {
                'name': 'Twisted Infinity Platinum Band',
                'slug': 'twisted-infinity-platinum-band',
                'category': 'rings',
                'collection': 'solitaire',
                'description': 'Sleek twisted infinity band crafted in 95% pure PT950 platinum with a minimalist aesthetic.',
                'gender': 'unisex',
                'rating': Decimal('4.7'),
                'review_count': 15,
                'badge': 'New',
                'has_diamonds': False,
                'sizes_available': True,
                'certifications': ['PGI Certified'],
                'images': [],
                'variants': [
                    {'sku': 'KW-INF-PT950-14', 'metal': 'platinum', 'purity': 'PT950', 'size': '14', 'gross': '4.5', 'net': '4.5', 'making': '16.0', 'discount': '600'},
                    {'sku': 'KW-INF-PT950-16', 'metal': 'platinum', 'purity': 'PT950', 'size': '16', 'gross': '4.8', 'net': '4.8', 'making': '16.0', 'discount': '600'},
                ],
                'stones': []
            },
            {
                'name': 'Gauri Diamond Mangalsutra',
                'slug': 'gauri-diamond-mangalsutra',
                'category': 'mangalsutra',
                'collection': 'bridal',
                'description': 'An auspicious blend of black beads and an exquisite 18K yellow gold pendant set with certified diamonds.',
                'gender': 'women',
                'rating': Decimal('4.9'),
                'review_count': 31,
                'badge': 'Bestseller',
                'has_diamonds': True,
                'sizes_available': False,
                'certifications': ['BIS Hallmark', 'IGI Certified'],
                'images': [],
                'variants': [
                    {'sku': 'KW-GAURI-18K', 'metal': 'gold', 'purity': '18K', 'size': None, 'gross': '7.2', 'net': '6.4', 'making': '14.0', 'discount': '1200'},
                ],
                'stones': [
                    {'stone_type': 'Natural Diamond', 'count': 9, 'carat': '0.22', 'clarity': 'VVS-VS', 'color': 'G-H', 'shape': 'Round', 'price': '18500'}
                ]
            },
        ]

        for item in catalog_sample:
            prod, _ = Product.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'name': item['name'],
                    'category': cat_objs[item['category']],
                    'collection': col_objs.get(item['collection']),
                    'description': item['description'],
                    'gender': item['gender'],
                    'rating': item['rating'],
                    'review_count': item['review_count'],
                    'badge': item['badge'],
                    'has_diamonds': item['has_diamonds'],
                    'sizes_available': item['sizes_available'],
                    'certifications': item['certifications'],
                    'images': item['images'],
                }
            )

            for v in item['variants']:
                Variant.objects.update_or_create(
                    sku=v['sku'],
                    defaults={
                        'product': prod,
                        'metal': v['metal'],
                        'purity': v['purity'],
                        'size': v['size'],
                        'gross_weight': Decimal(v['gross']),
                        'net_weight': Decimal(v['net']),
                        'making_pct': Decimal(v['making']),
                        'discount': Decimal(v['discount']),
                        'in_stock': True,
                    }
                )

            for s in item['stones']:
                Stone.objects.update_or_create(
                    product=prod,
                    stone_type=s['stone_type'],
                    defaults={
                        'count': s['count'],
                        'carat': Decimal(s['carat']),
                        'clarity': s['clarity'],
                        'color': s['color'],
                        'shape': s['shape'],
                        'price': Decimal(s['price']),
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Kalashwet catalogue data.'))
