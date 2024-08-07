# Generated by Django 4.0.1 on 2024-07-22 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_product_is_available'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('created_at', 'updated_at')},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ('order',)},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('name', 'description', 'price')},
        ),
        migrations.AddField(
            model_name='order',
            name='is_checked_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='shop.category'),
        ),
    ]
