from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from core.pagination import CustomPagination
from apps.managements.serializers.input import (
    ProductCreateInputSerializerAdmin
)
from apps.managements.serializers.output import (
    ProductViewSerialzierAdmin

)
from core.responses import error_response, success_response
from rest_framework import status
from apps.managements.services.product_management_services import (
    create_prodcut_services,
    get_admin_products
)
import logging
from django.db import IntegrityError


logger = logging.getLogger(__name__)

#write your views

class ProductGetOrCreateAPIView(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPagination
  
    def get(self, request):
        search_keyword = request.GET.get('search')
        if search_keyword:
            products = get_admin_products(keyword=search_keyword)
        else:
            products = get_admin_products()
        paginator = self.pagination_class()
        paginated_colonies = paginator.paginate_queryset(products, request)
        serializer = ProductViewSerialzierAdmin(paginated_colonies, many=True)
        return paginator.get_paginated_response(serializer.data)



    def post(self, request):
        data = request.data.copy()
        uploaded_files = request.FILES.getlist("files")
        if uploaded_files:
            data.setlist("files", uploaded_files)

        serializer = ProductCreateInputSerializerAdmin(data=data)
        if not serializer.is_valid():
            return error_response(
                "Validation error.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        try:
            product = create_prodcut_services(serializer.validated_data)
            output_serializer = ProductViewSerialzierAdmin(product)
            return success_response(
                "Product has been created successfully.",
                status.HTTP_201_CREATED,
                data=output_serializer.data,
            )
        
        except IntegrityError as exc:
            # This catches unique constraint violations (e.g., duplicate product name)
            logger.warning(f"Integrity error: {exc}")
            return error_response(
                "A product with this name already exists.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Error creating product: {exc}", exc_info=True)
            return error_response(
                "Failed to create product.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
