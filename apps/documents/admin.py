
from django.contrib import admin
from django.db.models import Sum
from .models import Document, DocumentItem, BalanceItem


class DocumentItemInline(admin.TabularInline):
    model = DocumentItem
    extra = 0
    fields = (
        "variant",
        "qty",
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
        "qty",
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
        "total_qty",
    )
    list_filter = ("doc_type", "shop")
    search_fields = ("id", "shop__name")
    inlines = (DocumentItemInline, BalanceItemInline)
    ordering = ("-id",)
    readonly_fields = ("items_count", "total_qty")

    def items_count(self, obj):
        """Count of related DocumentItem + BalanceItem rows."""
        doc_items = DocumentItem.objects.filter(document=obj).count()
        bal_items = BalanceItem.objects.filter(document=obj).count()
        return doc_items + bal_items
    items_count.short_description = "Items"

    def total_qty(self, obj):
        """
        Sum qty across related DocumentItem and BalanceItem.
        Returns Decimal or None -> show 0 if None.
        """
        doc_sum = DocumentItem.objects.filter(
            document=obj).aggregate(total=Sum("qty"))["total"] or 0
        bal_sum = BalanceItem.objects.filter(
            document=obj).aggregate(total=Sum("qty"))["total"] or 0
        return doc_sum + bal_sum
    total_qty.short_description = "Total qty"


@admin.register(DocumentItem)
class DocumentItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "variant",
        "qty",
        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
    )
    list_filter = ("currency", "document__shop")
    search_fields = ("id", "variant__id", "document__id")
    ordering = ("-id",)
    list_editable = ("qty", "income_price", "outcome_price")


@admin.register(BalanceItem)
class BalanceItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "variant",
        "qty",
        "currency",
        "currency_rate",
        "income_price",
        "outcome_price",
    )
    list_filter = ("currency", "document__shop")
    search_fields = ("id", "variant__id", "document__id")
    ordering = ("-id",)
    list_editable = ("qty", "income_price", "outcome_price")
