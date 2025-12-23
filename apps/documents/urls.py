from django.urls import path
from .views import BuyDocumentView, SellDocumentView, DocumentItemListView

urlpatterns = [

    path('buy/', BuyDocumentView.as_view(), ),
    path('sell/', SellDocumentView.as_view(),),
    path('<int:pk>/items/', DocumentItemListView.as_view())
]
