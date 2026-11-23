from django.contrib import admin
from .models import Category, Collection, DiamondCut, FeaturedProduct, FounderProfile, GiftGuide, HomeBanner, JewelleryVideo, LatestInsight, Product, ProductMedia, Stone, Variant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_upload')
    search_fields = ('name', 'slug')
    fields = ('name', 'slug', 'image', 'image_file')

    @admin.display(description='Uploaded image')
    def image_upload(self, obj):
        return bool(obj.image_file)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'collection', 'gender', 'badge', 'is_active')
    list_filter = ('category', 'gender', 'is_active')
    search_fields = ('name', 'slug')
    fields = ('name', 'slug', 'category', 'collection', 'description', 'gender', 'badge', 'has_diamonds', 'sizes_available', 'certifications', 'images', 'height_mm', 'width_mm', 'depth_mm', 'package_contents', 'is_active')


@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'kind', 'alt_text', 'sort_order')
    list_filter = ('kind',)
    list_editable = ('sort_order',)
    search_fields = ('product__name', 'alt_text')
    ordering = ('product', 'sort_order')


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'metal', 'purity', 'size', 'in_stock')
    list_filter = ('metal', 'purity', 'in_stock')
    search_fields = ('sku', 'product__name')


@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    list_display = ('product', 'stone_type', 'count', 'carat', 'shape')
    list_filter = ('stone_type', 'shape')
    search_fields = ('product__name', 'stone_type')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_upload')
    search_fields = ('name', 'slug')
    fields = ('name', 'slug', 'tagline', 'image', 'image_file')

    @admin.display(description='Uploaded image')
    def image_upload(self, obj):
        return bool(obj.image_file)


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_on_home', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('show_on_home', 'is_active')
    list_editable = ('show_on_home', 'is_active', 'sort_order')
    search_fields = ('title', 'subtitle')
    ordering = ('sort_order', '-created_at')


@admin.register(DiamondCut)
class DiamondCutAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_on_home', 'is_active', 'sort_order')
    list_filter = ('show_on_home', 'is_active')
    list_editable = ('show_on_home', 'is_active', 'sort_order')
    search_fields = ('name',)
    ordering = ('sort_order', 'name')


@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('product__name', 'product__slug')
    ordering = ('sort_order', '-created_at')


@admin.register(GiftGuide)
class GiftGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'cta', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('title',)
    ordering = ('sort_order', 'title')


@admin.register(JewelleryVideo)
class JewelleryVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('title',)
    ordering = ('sort_order', 'title')


@admin.register(FounderProfile)
class FounderProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(LatestInsight)
class LatestInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('title', 'excerpt')
    ordering = ('sort_order', '-created_at')
