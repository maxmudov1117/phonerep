from django.urls import path
from .views import BuyDocumentView, SellDocumentView

urlpatterns = [

    path('buy/', BuyDocumentView.as_view(), ),
    path('sell/', SellDocumentView.as_view(),),
]
