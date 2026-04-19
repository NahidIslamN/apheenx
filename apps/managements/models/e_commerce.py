from django.conf import settings
from django.db import models
from decimal import Decimal
User = settings.AUTH_USER_MODEL

# write your models here

class Image(models.Model):
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('accessories', "Accessories"),
        ('fashion', "Fashion"),
    )

    STATUS_CHOICES = (
        ('active', "Active"),
        ('inactive', "Inactive"),
        ('draft', "Draft"),
    )

    product_name = models.CharField(max_length=250, unique=True)
    product_description = models.TextField()

    price = models.DecimalField(
        max_digits=9,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=True,
        blank=True
    )

    stock_quantity = models.PositiveIntegerField(default=0)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='fashion'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    product_images = models.ManyToManyField(
        Image,
        related_name="products",
        blank=True
    )
    
    sales_count = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} - {self.price}"
    


class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='orders')
    is_paid = models.BooleanField(default=False)
    order_total = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    # Shipping Address
    email = models.EmailField()
    phone = models.CharField(max_length=250)
    address = models.TextField()
    city = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=250)
    country = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_order_total(self):
        total = sum(product.price for product in self.products.all())
        self.order_total = Decimal(total)
        self.save(update_fields=["order_total"])
        return self.order_total
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_order_total()
