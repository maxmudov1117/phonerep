from django.db import models

from apps.base.models import BaseModel


class BaseDocumentItem(BaseModel):
    shop = models.ForeignKey(
        "shops.Shop", on_delete=models.CASCADE, blank=True, null=True)
    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE)

    currency = models.ForeignKey(
        "currencies.Currency", on_delete=models.CASCADE)
    currency_rate = models.DecimalField(max_digits=20, decimal_places=4)
    qty = models.DecimalField(max_digits=20, decimal_places=4)
    income_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0)
    outcome_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0)
    variant = models.ForeignKey(
        "products.Variant", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        abstract = True


class Document(BaseModel):
    class DocType(models.TextChoices):
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"

    shop = models.ForeignKey(
        "shops.Shop", related_name="documents", on_delete=models.CASCADE
    )
    doc_type = models.CharField(
        max_length=5,
        choices=DocType.choices,
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return f"Document {self.id} - {self.doc_type}"


class DocumentItem(BaseDocumentItem):
    pass


class BalanceItem(BaseDocumentItem):
    pass
