from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TransactionFilter
from .models import Category, Transaction
from .serializers import (
    AccountSerializer,
    CategorySerializer,
    TransactionSerializer,
    TransferSerializer,
)
from .services import (
    create_transfer,
    delete_account,
    delete_category,
    delete_transaction,
    get_accounts_with_balance,
)


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer

    def get_queryset(self):
        return get_accounts_with_balance(self.request.user)

    def perform_create(self, serializer):
        account = serializer.save(user=self.request.user)
        # A new account has no transactions yet.
        account.balance = Decimal("0")

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

    def perform_destroy(self, instance):
        delete_transaction(instance)


class TransferView(APIView):
    def post(self, request):
        serializer = TransferSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        transfer = create_transfer(user=request.user, **serializer.validated_data)
        return Response(TransferSerializer(transfer).data, status=status.HTTP_201_CREATED)
