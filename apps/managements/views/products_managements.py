from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from core.pagination import CustomPagination
from apps.managements.serializers.input import (
    ProductCreateInputSerializerAdmin,
)
from apps.managements.serializers.output import (
    ProductViewSerialzierAdmin,
)

from core.responses import error_response, success_response
from rest_framework import status
from apps.managements.services.product_management_services import (
    create_prodcut_services,
    delete_product_services,
    get_admin_product_by_id,
    get_admin_products,
    ProductNotFoundError,
    update_product_services,
)
import logging
from django.db import IntegrityError


logger = logging.getLogger(__name__)

#write your views

class ProductGetOrCreateAPIView(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPagination

    def get(self, request, product_id=None):
        if product_id is not None:
            try:
                product = get_admin_product_by_id(product_id)
                serializer = ProductViewSerialzierAdmin(product)
                return success_response(
                    "Product retrieved successfully.",
                    status.HTTP_200_OK,
                    data=serializer.data,
                )
            except ProductNotFoundError:
                return error_response(
                    "The requested product could not be found.",
                    status.HTTP_404_NOT_FOUND,
                )
            except Exception as exc:
                logger.error(f"Error retrieving product {product_id}: {exc}", exc_info=True)
                return error_response(
                    "Unable to retrieve the product at this time.",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        search_keyword = request.GET.get("search")
        if search_keyword:
            products = get_admin_products(keyword=search_keyword)
        else:
            products = get_admin_products()

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductViewSerialzierAdmin(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, product_id=None):
        if product_id is not None:
            return error_response(
                "Method not allowed on product detail endpoint.",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        data = request.data.copy()
        uploaded_files = request.FILES.getlist("files")
        if uploaded_files:
            data.setlist("files", uploaded_files)

        serializer = ProductCreateInputSerializerAdmin(data=data)
        if not serializer.is_valid():
            return error_response(
                "Product data validation failed.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        try:
            product = create_prodcut_services(serializer.validated_data)
            output_serializer = ProductViewSerialzierAdmin(product)
            return success_response(
                "Product created successfully.",
                status.HTTP_201_CREATED,
                data=output_serializer.data,
            )

        except IntegrityError as exc:
            logger.warning(f"Integrity error: {exc}")
            return error_response(
                "A product with the same unique attributes already exists.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Error creating product: {exc}", exc_info=True)
            return error_response(
                "Unable to create the product at this time.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, product_id=None):
        if product_id is None:
            return error_response(
                "Product ID is required for update operations.",
                status.HTTP_400_BAD_REQUEST,
            )

        return self._update_product(request, product_id=product_id, partial=False)

    def patch(self, request, product_id=None):
        if product_id is None:
            return error_response(
                "Product ID is required for update operations.",
                status.HTTP_400_BAD_REQUEST,
            )

        return self._update_product(request, product_id=product_id, partial=True)

    def delete(self, request, product_id=None):
        if product_id is None:
            return error_response(
                "Product ID is required for delete operations.",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            delete_product_services(product_id)
            return success_response(
                "Product deleted successfully.",
                status.HTTP_200_OK,
            )
        except ProductNotFoundError:
            return error_response(
                "The requested product could not be found.",
                status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            logger.error(f"Error deleting product {product_id}: {exc}", exc_info=True)
            return error_response(
                "Unable to delete the product at this time.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update_product(self, request, product_id: int, partial: bool):
        data = request.data.copy()
        uploaded_files = request.FILES.getlist("files")
        if uploaded_files:
            data.setlist("files", uploaded_files)

        serializer = ProductCreateInputSerializerAdmin(data=data, partial=partial)
        if not serializer.is_valid():
            return error_response(
                "Product data validation failed.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        try:
            product = update_product_services(product_id=product_id, validated_data=serializer.validated_data)
            output_serializer = ProductViewSerialzierAdmin(product)
            return success_response(
                "Product updated successfully.",
                status.HTTP_200_OK,
                data=output_serializer.data,
            )
        except ProductNotFoundError:
            return error_response(
                "The requested product could not be found.",
                status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError as exc:
            logger.warning(f"Integrity error while updating product {product_id}: {exc}")
            return error_response(
                "A product with the same unique attributes already exists.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Error updating product {product_id}: {exc}", exc_info=True)
            return error_response(
                "Unable to update the product at this time.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
