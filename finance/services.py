from rest_framework.exceptions import ValidationError


def delete_account(account):
    if account.transactions.exists():
        raise ValidationError({"detail": "Cannot delete an account that has transactions."})
    account.delete()


def delete_category(category):
    if category.transactions.exists():
        raise ValidationError({"detail": "Cannot delete a category that has transactions."})
    category.delete()
