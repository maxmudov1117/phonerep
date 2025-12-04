from django.contrib import admin

from django.contrib import admin
from django.db.models import Count, Sum
from django.conf import settings
from .models import Shop

# --------- ShopAdmin ---------


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by",
                    "admins_count", "short_address")
    search_fields = ("name", "address",
                     "created_by__full_name", "created_by__phone_number")
    list_filter = ("admins",)  # handy to filter shops by an admin user
    filter_horizontal = ("admins",)  # nicer multi-select for many-to-many
    raw_id_fields = ("created_by",)
    ordering = ("name",)
    save_on_top = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # annotate number of admins (many-to-many)
        return qs.annotate(_admins_count=Count("admins", distinct=True))

    def admins_count(self, obj):
        return getattr(obj, "_admins_count", 0)
    admins_count.short_description = "Admins"
    admins_count.admin_order_field = "_admins_count"

    def short_address(self, obj):
        if not obj.address:
            return "-"
        return obj.address if len(obj.address) <= 60 else obj.address[:57] + "..."
    short_address.short_description = "Address"
