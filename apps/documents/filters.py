
import django_filters as filters

from apps.documents.models import DocumentItem


class DocumentItemFilter(filters.FilterSet):
    variant__product__name = filters.CharFilter(
        field_name='variant__product__name', lookup_expr='icontains')
    variant__sku = filters.CharFilter(
        field_name='variant__sku', lookup_expr='icontains')

    class Meta:
        model = DocumentItem
        fields = ['variant__product__name', 'variant__sku']


class DocumentSearchFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()
    doc_type = filters.CharFilter(field_name='doc_type', lookup_expr='iexact')

    class Meta:
        model = DocumentItem
        fields = ['created_at', 'doc_type']
