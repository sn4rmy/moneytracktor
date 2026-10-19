import pytest

from imports.models import ImportStatus
from tests.factories import TransactionImportFactory

pytestmark = pytest.mark.django_db


def test_new_import_is_pending_with_empty_report():
    transaction_import = TransactionImportFactory()

    assert transaction_import.status == ImportStatus.PENDING
    assert transaction_import.imported_rows == 0
    assert transaction_import.errors == []
    assert transaction_import.finished_at is None
