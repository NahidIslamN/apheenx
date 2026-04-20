from django.urls import path
from .views.products_managements import (
    ProductGetOrCreateAPIView
)

urlpatterns = [
    path('products/', ProductGetOrCreateAPIView.as_view(), name="products-admin"),

    
]
