from rest_framework import serializers
from apps.managements.models import Image,Product,Orders,VideoMedia,Video,VideoView

#write your serializers here..


class ProductCreateInputSerializerAdmin(serializers.Serializer):
    product_name = serializers.CharField()
    product_description = serializers.CharField()
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    discount_price = serializers.DecimalField(max_digits=9, decimal_places=2)
    stock_quantity = serializers.IntegerField()
    category = serializers.CharField()
    status = serializers.CharField()
    files = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
    )

    sales_count = serializers.IntegerField()
    is_featured = serializers.BooleanField()
    is_active = serializers.BooleanField()

    

