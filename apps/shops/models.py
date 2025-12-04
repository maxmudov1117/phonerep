from django.db import models
from django.conf import settings

from apps.base.models import BaseModel


class Shop(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField()

    # who created this shop (owner)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_shops",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # additional admins / managers of the shop
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="managed_shops",
        blank=True,
        help_text="Users who can manage this shop (in addition to the creator)."
    )

    def __str__(self):
        return self.name
