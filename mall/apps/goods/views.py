from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from goods.models import SKU
from goods.serializers import HotSKUListSerializer


class HomeView(APIView):
    pass

from rest_framework.generics import ListAPIView
class HotSKUListAPIView(ListAPIView):

    # queryset = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]
    # queryset = SKU.objects.all()
    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]



    serializer_class = HotSKUListSerializer