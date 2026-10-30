from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import AccountViewSet, CategoryViewSet, TransactionViewSet, TransferView

router = SimpleRouter(trailing_slash=False)
router.register("accounts", AccountViewSet, basename="account")
router.register("categories", CategoryViewSet, basename="category")
router.register("transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("transfers", TransferView.as_view(), name="transfer-create"),
]
urlpatterns += router.urls
