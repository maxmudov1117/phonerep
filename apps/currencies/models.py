from django.db import models
from apps.base.models import BaseModel
# Create your models here.


class Currency(BaseModel):
    shop = models.ForeignKey(
        "shops.Shop", related_name="currencies", on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=30, decimal_places=5,)
    created_by = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return str(f"{self.rate} uzs")
