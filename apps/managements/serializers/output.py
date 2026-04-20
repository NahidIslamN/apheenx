from rest_framework import serializers
from apps.managements.models import Image,Product,Orders,VideoMedia,Video,VideoView


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
     
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

class ProductViewSerialzierAdmin(serializers.ModelSerializer):
    
    product_images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]