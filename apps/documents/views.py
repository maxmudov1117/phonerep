
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from rest_framework.request import Request
from apps.currencies.models import Currency
from apps.documents.models import BalanceItem, Document, DocumentItem
from apps.documents.serializers import BuySerializer, SellSerializer, DocumentSerializer
from apps.products.models import Variant, Imei, Product


class DocumentBaseView(GenericAPIView):
    serializer_class = None
    permission_classes = [AllowAny,]
    queryset = Document.objects.all()


class BuyDocumentView(DocumentBaseView):
    serializer_class = BuySerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request: Request):
        items = request.data.get("items", [])
        print("Received items for buy document:", items)
        try:
            with transaction.atomic():
                if request.user.is_anonymous:
                    return Response({"error": "Authentication required"}, status=401)
                items = request.data.get("items", [])

                variant_id = items[0]
                if not variant_id:
                    return Response({"error": "No items provided"}, status=400)
                variant = Variant.objects.filter(
                    id=variant_id.get("id")).first()
                if not variant:
                    return Response({"error": "Invalid variant ID"}, status=400)
                product = variant.product

                document = Document.objects.create(
                    doc_type=Document.DocType.BUY, created_by=request.user, shop=product.shop
                )
                if not items:
                    return Response({"error": "No items provided"}, status=400)
                for item in items:
                    variant = Variant.objects.filter(
                        id=item.get("id")).first()

                    imies = item.get("imei_codes", [])
                    if imies:
                        parent_imei = None
                        for index, imei_code in enumerate(imies):
                            # The first IMEI becomes parent
                            if index == 0:
                                parent_imei = Imei.objects.create(
                                    variant=variant,
                                    imei_code=imei_code.get("code"),
                                    created_by=request.user,
                                    is_activated=imei_code.get("is_activated")

                                )
                            else:
                                # others use first one as parent
                                Imei.objects.create(
                                    variant=variant,
                                    imei_code=imei_code.get("code"),
                                    parent=parent_imei,
                                    created_by=request.user,
                                    is_activated=imei_code.get("is_activated")
                                )

                    latest_currency = Currency.objects.filter(
                        shop=product.shop, deleted_at=None).order_by("-created_at").first()

                    document_item = DocumentItem.objects.create(
                        document=document,
                        variant=variant,
                        currency_rate=latest_currency.rate,
                        currency=latest_currency,
                        qty=item.get("quantity", 1),
                        income_price=item.get("income_price"),
                        created_by=request.user,
                    )
                    balance_item = BalanceItem.objects.create(
                        document=document,
                        variant=variant,

                        currency_rate=latest_currency.rate if latest_currency else 0,
                        currency=latest_currency,
                        qty=item.get("quantity", 1),
                        income_price=item.get("income_price"),
                        created_by=request.user,
                    )

            return Response({"message": "Buy document processed", "data": "New Products Added"}, status=201)
        except Exception as e:
            print("Error processing buy document:", e)
            return Response(
                {"error": str(e)}, status=500
            )


class SellDocumentView(DocumentBaseView):
    serializer_class = SellSerializer

    def post(self, request):
        variant_id = request.data.get("items")[0]
        try:
            with transaction.atomic():
                if not variant_id:
                    return Response({"error": "No items provided"}, status=400)
                variant = Variant.objects.filter(
                    id=variant_id.get("variant_id")).first()
                if not variant:
                    return Response({"error": "Invalid variant ID"}, status=400)
                product = variant.product

                document = Document.objects.create(
                    doc_type=Document.DocType.SELL, created_by=request.user, shop=product.shop
                )
                for item in request.data.get("items", []):
                    variant = Variant.objects.filter(
                        id=item.get("variant_id")).first()
                    latest_currency = None
                    deleted_count, _ = variant.imeis.all().delete()
                    print("[+] Deleted IMEIs count:", deleted_count)

                    if variant.currency_type == "usd":
                        latest_currency = Currency.objects.filter(
                            shop=product.shop, deleted_at=None).order_by("-created_at").first()

                    document_item = DocumentItem.objects.create(
                        document=document,
                        variant=variant,

                        currency_rate=latest_currency.rate if latest_currency else 0,
                        currency=latest_currency,
                        qty=item.get("qty", 1),
                        income_price=variant.income_price,
                        outcome_price=variant.outcome_price,
                        created_by=request.user,
                    )
                    balance_item: BalanceItem = BalanceItem.objects.filter(
                        variant=variant
                    ).first()
                    if balance_item:
                        balance_item.qty -= item.get("qty", 1)
                        balance_item.save()
                    if balance_item.qty < 0:
                        balance_item.hard_delete()
                return Response({"message": "Sell document processed"}, status=201)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=500
            )
