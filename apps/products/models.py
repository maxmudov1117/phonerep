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
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants",
    )
    ram = models.PositiveIntegerField()
    storage = models.PositiveIntegerField()

    class Meta:
        unique_together = ("product", "ram", "storage")

    def __str__(self):
        return f"{self.product.title} — {self.ram}GB/{self.storage}GB"
