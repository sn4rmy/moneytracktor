from rest_framework.routers import SimpleRouter

from .views import AccountViewSet, CategoryViewSet, TransactionViewSet

router = SimpleRouter(trailing_slash=False)
router.register("accounts", AccountViewSet, basename="account")
router.register("categories", CategoryViewSet, basename="category")
router.register("transactions", TransactionViewSet, basename="transaction")

urlpatterns = router.urls
