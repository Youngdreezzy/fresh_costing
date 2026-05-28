from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'sales_price',
        'rate',
        'is_active',
    )

    search_fields = ('name',)