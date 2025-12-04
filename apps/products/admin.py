from django.contrib import admin
from django.contrib import admin
from django.db.models import Count

from .models import Product, Company, Variant, Imei


class VariantInline(admin.TabularInline):
    model = Variant
    fields = ("ram", "storage", )
    extra = 1
    min_num = 0
    show_change_link = True
    verbose_name = "Variant (RAM/Storage)"
    verbose_name_plural = "Variants"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "shop",
        "variant_count",
        "created_at" if hasattr(Product, "created_at") else None,
    )
    # filter out any None from list_display if created_at doesn't exist
    list_display = tuple(x for x in list_display if x is not None)

    list_select_related = ("company", "shop")
    search_fields = ("title", "company__name")
    list_filter = ("company", "shop")
    inlines = [VariantInline]
    raw_id_fields = ("company", "shop")
    ordering = ("-id",)
    save_on_top = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate with variant count and total stock for list display
        qs = qs.annotate(
            _variant_count=Count("variants", distinct=True),
        ).select_related("company", "shop")
        return qs

    def variant_count(self, obj):
        return getattr(obj, "_variant_count", 0)
    variant_count.short_description = "Variants"
    variant_count.admin_order_field = "_variant_count"


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "ram", "storage", )
    list_select_related = ("product",)
    search_fields = ("product__title",)
    list_filter = ("ram", "storage")
    raw_id_fields = ("product",)
    ordering = ("product__title", "ram", "storage")


@admin.register(Imei)
class ImeiAdmin(admin.ModelAdmin):
    list_display = (
        "id", "imei_code", "is_activated", "variant", "created_by"
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", )
    search_fields = ("name",)
    # list_filter = ("shop",)
    # raw_id_fields = ("shop",)
    ordering = ("name",)
