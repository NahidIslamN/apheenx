from django.db import transaction
from apps.managements.models import Image, Product
from django.db.models import Q



def create_prodcut_services(validated_data:dict) -> Product:
    files = validated_data.pop("files", [])
    with transaction.atomic():
        product = Product.objects.create(**validated_data)

        if files:
            product_image = [Image.objects.create(image=file_obj) for file_obj in files]
            product.product_images.set(product_image)
        

        return product
    


def get_admin_products(keyword=None):
    queryset = Product.objects.all().order_by('-created_at')

    if keyword:
        queryset = queryset.filter(
            Q(product_name__icontains=keyword) |
            Q(product_description__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(status__icontains=keyword)
        )

    return queryset



