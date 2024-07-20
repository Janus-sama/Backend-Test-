from django.db import transaction
from rest_framework import serializers

from .models import Product, Category, Order, OrderItem


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Product
        fields = ['url', 'id', 'category', 'name', 'description',
                  'price', 'stock', 'is_available']
        read_only_fields = ['is_available']


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    products = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='product-detail')

    class Meta:
        model = Category
        fields = ['url', 'id', 'name', 'products']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),

    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.HyperlinkedModelSerializer):

    order_items = OrderItemSerializer(
        many=True, source='orderitem_set', required=False)

    class Meta:
        model = Order
        fields = ['url', 'id', 'user', 'order_items', 'created_at']
        read_only_fields = ['created_at', 'user']

    def create(self, validated_data):
        order_items_data = validated_data.pop('orderitem_set', [])
        print(order_items_data)
        with transaction.atomic():
            order, _ = Order.objects.get_or_create(**validated_data)
            for order_item_data in order_items_data:
                OrderItem.objects.create(order=order, **order_item_data)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('orderitem_set', [])
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            order_item_ids = [item['id']
                              for item in order_items_data if 'id' in item]
            instance.orderitem_set.exclude(id__in=order_item_ids).delete()

            for order_item_data in order_items_data:
                if 'id' in order_item_data:
                    order_item = instance.orderitem_set.get(
                        id=order_item_data['id'])
                    order_item.product = order_item_data.get(
                        'product', order_item.product)
                    order_item.quantity = order_item_data.get(
                        'quantity', order_item.quantity)
                    order_item.save()
                else:
                    OrderItem.objects.create(order=instance, **order_item_data)
        return instance
