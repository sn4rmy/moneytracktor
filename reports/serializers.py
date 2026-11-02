from rest_framework import serializers


class PeriodQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class YearQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=2100)


class SummarySerializer(serializers.Serializer):
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class CategoryExpenseSerializer(serializers.Serializer):
    category = serializers.IntegerField()
    category_name = serializers.CharField(source="category__name")
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class MonthlyTotalSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expense = serializers.DecimalField(max_digits=12, decimal_places=2)
