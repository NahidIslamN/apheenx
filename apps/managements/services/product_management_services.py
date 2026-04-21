from django.db import transaction
from apps.managements.models import Image, Product
from django.db.models import Q


class ProductNotFoundError(Exception):
    pass


def _create_product_images(files):
    return [Image.objects.create(image=file_obj) for file_obj in files]



def create_prodcut_services(validated_data:dict) -> Product:
    files = validated_data.pop("files", [])
    with transaction.atomic():
        product = Product.objects.create(**validated_data)

        if files:
            product_images = _create_product_images(files)
            product.product_images.set(product_images)
        

        return Product.objects.prefetch_related("product_images").get(pk=product.pk)
    


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


def get_admin_product_by_id(product_id: int) -> Product:
    product = Product.objects.prefetch_related("product_images").filter(pk=product_id).first()
    if not product:
        raise ProductNotFoundError(f"Product with id {product_id} does not exist.")
    return product


def update_product_services(product_id: int, validated_data: dict) -> Product:
    files = validated_data.pop("files", None)

    with transaction.atomic():
        product = Product.objects.select_for_update().filter(pk=product_id).first()
        if not product:
            raise ProductNotFoundError(f"Product with id {product_id} does not exist.")

        for field, value in validated_data.items():
            setattr(product, field, value)
        product.save()

        if files is not None:
            product_images = _create_product_images(files)
            product.product_images.set(product_images)

        return Product.objects.prefetch_related("product_images").get(pk=product.pk)


def delete_product_services(product_id: int) -> None:
    with transaction.atomic():
        product = Product.objects.select_for_update().filter(pk=product_id).first()
        if not product:
            raise ProductNotFoundError(f"Product with id {product_id} does not exist.")

        image_ids = list(product.product_images.values_list("id", flat=True))
        product.delete()

        if image_ids:
            Image.objects.filter(id__in=image_ids, products__isnull=True).delete()



