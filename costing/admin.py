from django.contrib import admin
from .models import DailyCosting, Outlet


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):

    list_display = ('name',)


@admin.register(DailyCosting)
class DailyCostingAdmin(admin.ModelAdmin):

    list_display = (
        'date',
        'outlet',
        'product',
        'opening_stock',
        'requisition',
        'complimentary',
        'closing_stock',
    )

    list_filter = (
        'date',
        'outlet',
    )

    search_fields = (
        'product__name',
        'outlet__name',
    )