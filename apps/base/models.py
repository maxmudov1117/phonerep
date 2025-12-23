from django.db import models
from django.utils import timezone

from apps.base.managers import SoftDeleteManager

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    actives = SoftDeleteManager()
    objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        """Soft delete by default"""
        self.soft_delete()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object"""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
