from django.urls import path
from .views.products_managements import (
    ProductGetOrCreateAPIView
)
from .views.video_managements import (
    ViewManagementViewAdmin,
)

urlpatterns = [
    path('products/', ProductGetOrCreateAPIView.as_view(), name="products-admin"),
    path('products/<int:product_id>/', ProductGetOrCreateAPIView.as_view(), name="products-admin-detail"),

    path('videos/', ViewManagementViewAdmin.as_view(), name="video-admin"),
    path('videos/<int:pk>/', ViewManagementViewAdmin.as_view(), name="video-admin-detail"),
]
