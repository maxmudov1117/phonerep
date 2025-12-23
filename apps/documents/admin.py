
from django.contrib import admin
from django.db.models import Sum
from .models import Document, DocumentItem, BalanceItem, Imei


class DocumentItemInline(admin.TabularInline):
    model = DocumentItem
    extra = 0
    fields = (
        "variant",
        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
    )
    show_change_link = True


class BalanceItemInline(admin.TabularInline):
    model = BalanceItem
    extra = 0
    fields = (
        "variant",
        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
    )
    show_change_link = True


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shop",
        "doc_type",
        "items_count",

    )
    list_filter = ("doc_type", "shop")
    search_fields = ("id", "shop__name")
    inlines = (DocumentItemInline, BalanceItemInline)
    ordering = ("-id",)
    readonly_fields = ("items_count", )

    def items_count(self, obj):
        """Count of related DocumentItem + BalanceItem rows."""
        doc_items = DocumentItem.actives.filter(document=obj).count()
        bal_items = BalanceItem.actives.filter(document=obj).count()
        return doc_items + bal_items
    items_count.short_description = "Items"


@admin.register(DocumentItem)
class DocumentItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "variant",

        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
        "provider"
    )
    list_filter = ("currency", "document__shop")
    search_fields = ("id", "variant__id", "document__id", "provider__name")
    ordering = ("-id",)
    list_editable = ("income_price", "outcome_price")


@admin.register(BalanceItem)
class BalanceItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "variant",

        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
        "provider"
    )
    list_filter = ("currency", "document__shop")
    search_fields = ("id", "variant__id", "document__id",   "provider__name")
    ordering = ("-id",)
    list_editable = ("income_price", "outcome_price")


@admin.register(Imei)
class ImeiAdmin(admin.ModelAdmin):
    list_display = (
        "id", "imei_code", "is_activated"
    )
