from rest_framework import serializers

from .models import Account, Category, Transaction, Transfer


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = ["id", "name", "type", "balance"]


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
    # Transactions created by a transfer have no category.
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)

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
            "transfer",
        ]
        read_only_fields = ["transfer"]
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
        if self.instance is not None and self.instance.transfer_id is not None:
            raise serializers.ValidationError(
                "Transactions created by a transfer cannot be changed."
            )

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


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ["id", "from_account", "to_account", "amount", "date"]

    def validate_from_account(self, account):
        if account.user != self.context["request"].user:
            raise serializers.ValidationError("Account not found.")
        return account

    def validate_to_account(self, account):
        if account.user != self.context["request"].user:
            raise serializers.ValidationError("Account not found.")
        return account

    def validate(self, attrs):
        if attrs["from_account"] == attrs["to_account"]:
            raise serializers.ValidationError(
                {"to_account": "Cannot transfer money to the same account."}
            )
        return attrs
