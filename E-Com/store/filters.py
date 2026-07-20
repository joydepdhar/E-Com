import django_filters
from rest_framework.filters import OrderingFilter

from .models import Order, Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category_id')
    is_active = django_filters.BooleanFilter()
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = []


class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='iexact')
    is_paid = django_filters.BooleanFilter()
    customer = django_filters.NumberFilter(field_name='user_id')

    class Meta:
        model = Order
        fields = []


class UserFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()
    is_staff = django_filters.BooleanFilter()


class AliasOrderingFilter(OrderingFilter):
    """Allow public ordering aliases while validating database field names."""

    def get_ordering(self, request, queryset, view):
        params = request.query_params.get(self.ordering_param)
        if not params:
            return self.get_default_ordering(view)

        ordering = [term.strip() for term in params.split(',')]
        aliases = getattr(view, 'ordering_field_aliases', {})
        ordering = tuple(
            f"{'-' if field.startswith('-') else ''}{aliases.get(field.lstrip('-'), field.lstrip('-'))}"
            for field in ordering
        )
        ordering = self.remove_invalid_fields(queryset, ordering, view, request)
        return ordering or self.get_default_ordering(view)
