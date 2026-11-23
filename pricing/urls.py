from django.urls import path
from .views import MetalRateListView

urlpatterns = [
    path('metal-rates/', MetalRateListView.as_view(), name='metal-rates'),
]
