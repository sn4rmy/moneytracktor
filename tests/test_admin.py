import pytest
from django.urls import reverse

from tests import factories

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "factory",
    [
        factories.UserFactory,
        factories.AccountFactory,
        factories.CategoryFactory,
        factories.TransferFactory,
        factories.TransactionFactory,
        factories.ExchangeRateFactory,
        factories.BudgetFactory,
        factories.BudgetNotificationFactory,
        factories.TransactionImportFactory,
    ],
)
def test_admin_pages_open(admin_client, factory):
    obj = factory()
    url_prefix = f"admin:{obj._meta.app_label}_{obj._meta.model_name}"

    changelist = admin_client.get(reverse(f"{url_prefix}_changelist"))
    change = admin_client.get(reverse(f"{url_prefix}_change", args=[obj.pk]))
    add = admin_client.get(reverse(f"{url_prefix}_add"))

    assert changelist.status_code == 200
    assert change.status_code == 200
    assert add.status_code == 200
