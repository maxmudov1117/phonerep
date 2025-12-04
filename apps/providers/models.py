from django.db import models
from apps.base.models import BaseModel


class Provider(BaseModel):
    shop = models.ForeignKey(
        "shops.Shop", verbose_name="Provider",
        related_name="providers", on_delete=models.SET_NULL, blank=True, null=True
    )
    created_by = models.ForeignKey(
        "users.User", verbose_name="Creator", on_delete=models.SET_NULL, blank=True, null=True
    )
    name = models.CharField(
        max_length=250, verbose_name="Provider Name",
    )

    def __str__(self):
        return str(self.name)
