from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import MetalRate
from .serializer import MetalRateSerializer
from .services import DEFAULT_RATES


class MetalRateListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = MetalRate.objects.all()
    serializer_class = MetalRateSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        # If rates are not yet seeded in DB, seed them from defaults
        if not MetalRate.objects.exists():
            for purity, rate in DEFAULT_RATES.items():
                MetalRate.objects.get_or_create(purity=purity, defaults={'rate_per_gram': rate})
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
