from django.urls import path
from .views import StoreListView, DeleteStoreItemView

urlpatterns = [
    path('', StoreListView.as_view()),
    path('delete-item/<int:pk>/', DeleteStoreItemView.as_view(),
         name='delete-store-item'),
]
