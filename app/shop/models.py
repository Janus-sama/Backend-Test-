from django.db import IntegrityError, models, transaction
from django.core.validators import MinValueValidator
from django.conf import settings

from shop.exceptions import OutOfStocksException
# Create your models here.


class DateTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return f'Category: {self.name}'


class AvailableProductManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_available=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products")
    price = models.PositiveIntegerField(verbose_name="Price (NGN)")
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(editable=False)

    available = AvailableProductManager()
    objects = models.Manager()

    class Meta:
        ordering = ('name', 'description', 'price')

    def __str__(self):
        return f"Product: {self.name} (NGN {self.price})"

    def save(self, *args, **kwargs):
        self.check_product_inventory()
        super().save(*args, **kwargs)

    def check_product_inventory(self):
        self.is_available = self.stock > 0


class Order(DateTimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")

    class Meta:
        ordering = ("created_at", "updated_at")

    def __str__(self):
        return f"Order by {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # the smallest possible value to order is 1
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Ordered {self.quantity} of {self.product}"

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():  # transaction to avoid race conditions
                if not self.product.is_available:
                    raise OutOfStocksException(
                        f"The item {self.product.name} is out of stock")

                super().save(*args, **kwargs)
                self.product.stock -= self.quantity
                self.product.save()  # reduce the product stock
        except IntegrityError:
            raise OutOfStocksException

    def delete(self, *args, **kwargs):
        with transaction.atomic():  # transaction to avoid race conditions
            super().delete(*args, **kwargs)
            self.product.stock += self.quantity
            self.product.save()  # add the item back into the stock
