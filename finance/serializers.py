from rest_framework import serializers

from .models import Account, Category, Transaction


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "type"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type"]

    def validate_type(self, value):
        if self.instance is not None and value != self.instance.type:
            raise serializers.ValidationError("The type of an existing category cannot be changed.")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "type",
            "amount",
            "date",
            "account",
            "account_name",
            "category",
            "category_name",
            "note",
        ]
        extra_kwargs = {"category": {"required": True, "allow_null": False}}

    def validate_account(self, account):
        if account.user != self.context["request"].user:
            raise serializers.ValidationError("Account not found.")
        return account

    def validate_category(self, category):
        if category.user != self.context["request"].user:
            raise serializers.ValidationError("Category not found.")
        return category

    def validate(self, attrs):
        # PATCH may send only some fields, so the rest come from the saved transaction.
        if self.instance is not None:
            transaction_type = attrs.get("type", self.instance.type)
            category = attrs.get("category", self.instance.category)
        else:
            transaction_type = attrs["type"]
            category = attrs["category"]

        if category.type != transaction_type:
            raise serializers.ValidationError(
                {"category": "Category type must match the transaction type."}
            )
        return attrs
