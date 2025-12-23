from django.db import models

from apps.base.models import BaseModel


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

    def get_total_price(self):
        if self.doc_type == 'SELL':
            total_price = sum(
                balance.outcome_price for balance in self.document_items.all())
            return total_price
        else:
            total_price = sum(
                balance.income_price for balance in self.document_items.all())
            return total_price


class BaseDocumentItem(BaseModel):
    shop = models.ForeignKey(
        "shops.Shop", on_delete=models.CASCADE, blank=True, null=True
    )
    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE
    )
    currency = models.ForeignKey(
        "currencies.Currency", on_delete=models.CASCADE)
    currency_rate = models.DecimalField(max_digits=20, decimal_places=4)
    income_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0
    )
    outcome_price = models.DecimalField(
        max_digits=20, decimal_places=4, default=0
    )
    variant = models.ForeignKey(
        "products.Variant", on_delete=models.CASCADE
    )
    provider = models.ForeignKey(
        "providers.Provider",
        on_delete=models.CASCADE, blank=True, null=True,
        verbose_name="Provider",
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE,
        blank=True, null=True
    )
    history_status = models.CharField(
        max_length=250, blank=True, null=True
    )

    imeis = models.ManyToManyField(
        "Imei",
        # will become documentitem_items / balanceitem_items
        related_name="%(class)s_items",
        blank=True,
    )

    class Meta:
        abstract = True


class DocumentItem(BaseDocumentItem):
    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE, related_name="document_items"
    )


class BalanceItem(BaseDocumentItem):
    document = models.ForeignKey(
        "documents.Document", on_delete=models.CASCADE, related_name="balances"
    )
    document_item = models.OneToOneField(
        DocumentItem, on_delete=models.CASCADE, verbose_name="Document Item", blank=True, null=True
    )


class Imei(BaseModel):

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
