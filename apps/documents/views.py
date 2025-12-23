
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from rest_framework.request import Request
from apps.currencies.models import Currency
from apps.documents.models import BalanceItem, Document, DocumentItem, Imei
from apps.documents.serializers import BuySerializer, SellSerializer, DocumentItemSerializer
from apps.products.models import Variant
from apps.providers.models import Provider


class DocumentBaseView(GenericAPIView):
    serializer_class = None
    permission_classes = [AllowAny,]
    queryset = Document.actives.all()


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

                variant_data = items[0]
                if not variant_data:
                    return Response({"error": "No items provided"}, status=400)
                variant = Variant.actives.filter(
                    id=variant_data.get("id")).first()
                if not variant:
                    return Response({"error": "Invalid variant ID"}, status=400)
                product = variant.product

                document = Document.objects.create(
                    doc_type=Document.DocType.BUY, created_by=request.user, shop=product.shop
                )
                if not items:
                    return Response({"error": "No items provided"}, status=400)
                for item in items:
                    variant = Variant.actives.filter(
                        id=item.get("id")).first()

                    latest_currency = Currency.objects.filter(
                        shop=product.shop, deleted_at=None).order_by("-created_at").first()

                    provider = Provider.objects.filter(
                        id=item.get("provider_id")
                    ).first()

                    document_item = DocumentItem.objects.create(
                        history_status=item.get("history_status", ""),
                        provider=provider,
                        document=document,
                        shop=product.shop,
                        variant=variant,
                        currency_rate=latest_currency.rate,
                        currency=latest_currency,
                        income_price=item.get("income_price"),
                        created_by=request.user,
                    )

                    imies = item.get("imei_codes", [])
                    for index, imei_code in enumerate(imies):
                        imei = Imei.objects.create(
                            imei_code=imei_code.get("code"),
                            created_by=request.user,
                            is_activated=imei_code.get("is_activated")
                        )
                        document_item.imeis.add(imei)

                    balance_item = BalanceItem.objects.create(
                        history_status=item.get("history_status", ""),
                        document=document,
                        document_item=document_item,
                        variant=variant,
                        shop=product.shop,
                        provider=provider,
                        currency_rate=latest_currency.rate if latest_currency else 0,
                        currency=latest_currency,
                        income_price=item.get("income_price"),
                        created_by=request.user,
                    )
                    balance_item.imeis.set(document_item.imeis.all())

            return Response({"message": "Buy document processed", "data": "New Products Added"}, status=201)
        except Exception as e:
            print("Error processing buy document:", e)
            return Response(
                {"error": str(e)}, status=500
            )


class SellDocumentView(DocumentBaseView):
    serializer_class = SellSerializer

    def post(self, request):
        print("Received data for sell document:", request.data)
        try:
            with transaction.atomic():

                items = request.data
                balance_item_instance = BalanceItem.actives.filter(
                    id=items[0].get("balance_id")).first()
                document = Document.actives.create(
                    doc_type=Document.DocType.SELL, created_by=request.user, shop=balance_item_instance.variant.product.shop
                )

                for item in items:
                    latest_currency = Currency.actives.filter(
                        shop=document.shop, deleted_at=None).order_by("-created_at").first()

                    balance_item: BalanceItem = BalanceItem.actives.filter(
                        id=item.get("balance_id")
                    ).first()

                    document_item = DocumentItem.actives.create(
                        document=document,
                        shop=document.shop,
                        provider=balance_item.provider,
                        variant=balance_item.variant,
                        currency_rate=latest_currency.rate if latest_currency else 0,
                        currency=latest_currency,
                        income_price=balance_item.income_price,
                        outcome_price=item.get("sale_price"),
                        created_by=request.user,
                        history_status=balance_item.history_status,
                    )
                    # ✅ attach IMEIs
                    document_item.imeis.set(balance_item.imeis.all())
                    balance_item.hard_delete()

                return Response({"message": "Sell document processed"}, status=201)
        except Exception as e:
            print("Error processing sell document:", e)
            return Response(
                {"error": str(e)}, status=500
            )


class DocumentItemListView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DocumentItemSerializer
    queryset = DocumentItem.actives.all()

    def get(self, request, pk):
        document_items = self.queryset.filter(document_id=pk)
        serializer = self.get_serializer(document_items, many=True)
        return Response(serializer.data)
