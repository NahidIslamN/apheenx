from rest_framework import serializers
from apps.managements.models import Image, Product, Orders, VideoMedia, Video, VideoView

#write your serializers here..


class ProductCreateInputSerializerAdmin(serializers.Serializer):
    product_name = serializers.CharField(max_length=250)
    product_description = serializers.CharField()
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    discount_price = serializers.DecimalField(max_digits=9, decimal_places=2, required=False, allow_null=True)
    stock_quantity = serializers.IntegerField(min_value=0)
    category = serializers.ChoiceField(choices=Product.CATEGORY_CHOICES)
    status = serializers.ChoiceField(choices=Product.STATUS_CHOICES)
    files = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
    )

    sales_count = serializers.IntegerField(min_value=0)
    is_featured = serializers.BooleanField()
    is_active = serializers.BooleanField()

    def validate(self, attrs):
        price = attrs.get("price")
        discount_price = attrs.get("discount_price")

        if discount_price is not None and price is not None and discount_price > price:
            raise serializers.ValidationError(
                {"discount_price": "Discount price must be less than or equal to the base price."}
            )

        return attrs



class VideoCreateInputSerializerAdmin(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    description = serializers.CharField()

    price = serializers.DecimalField(max_digits=9, decimal_places=2)

    category = serializers.ChoiceField(choices=Video.CATEGORY_CHOICES)
    status = serializers.ChoiceField(choices=Video.STATUS_CHOICES)

    trailers = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )

    videos = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )

    thumbnail = serializers.ImageField(required=False, allow_null=True)

    is_featured = serializers.BooleanField()
    is_active = serializers.BooleanField()

    def validate_title(self, value):
        # When updating, allow the same title for the same object (context['video_id']).
        video_id = self.context.get("video_id") if hasattr(self, "context") else None
        qs = Video.objects.filter(title=value)
        if video_id:
            qs = qs.exclude(pk=video_id)
        if qs.exists():
            raise serializers.ValidationError("Video with this title already exists.")
        return value

    def validate(self, attrs):
        return attrs

    

