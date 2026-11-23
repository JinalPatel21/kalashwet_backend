from django.urls import path
from .views import (
    HomeView, CategoryListView, CollectionListView,
    ProductListView, ProductDetailView, ServiceabilityView
)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('collections/', CollectionListView.as_view(), name='collection-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('serviceability/', ServiceabilityView.as_view(), name='serviceability'),
]
