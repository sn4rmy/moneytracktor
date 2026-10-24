from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination

from .filters import TransactionFilter
from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer
from .services import delete_account, delete_category


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_account(instance)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_category(instance)


class TransactionPagination(PageNumberPagination):
    page_size = 20


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ["note"]
    ordering_fields = ["date", "amount"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related(
            "account", "category"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
