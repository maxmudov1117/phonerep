from django.db import models
from apps.base.models import BaseModel
from apps.shops.models import Shop


class Company(BaseModel):
    name = models.CharField(max_length=250)


class Product(BaseModel):
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="products")
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Variant(BaseModel):
    provider = models.ForeignKey(
        "providers.Provider", on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Provider",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants",
    )
    ram = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()
    history_status = models.CharField(max_length=20, blank=True)
    income_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0)
    outcome_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0)

    class Meta:
        unique_together = ("product", "ram", "storage")

    def __str__(self):
        return f"{self.product.title} — {self.ram}GB/{self.storage}GB"


class Imei(BaseModel):
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="imeis", blank=True, null=True, verbose_name="Variant"
    )
    is_activated = models.BooleanField(
        verbose_name="Activated", blank=True, null=True,
    )
    imei_code = models.CharField(
        max_length=20, unique=True, verbose_name="Imei Code")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True,
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Creator")

    def __str__(self):
        return self.imei_code
