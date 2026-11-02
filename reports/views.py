from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CategoryExpenseSerializer,
    MonthlyTotalSerializer,
    PeriodQuerySerializer,
    SummarySerializer,
    YearQuerySerializer,
)
from .services import get_expenses_by_category, get_monthly_report, get_summary


class SummaryReportView(APIView):
    def get(self, request):
        params = PeriodQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        summary = get_summary(request.user, **params.validated_data)
        return Response(SummarySerializer(summary).data)


class CategoryReportView(APIView):
    def get(self, request):
        params = PeriodQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        categories = get_expenses_by_category(request.user, **params.validated_data)
        return Response(CategoryExpenseSerializer(categories, many=True).data)


class MonthlyReportView(APIView):
    def get(self, request):
        params = YearQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        months = get_monthly_report(request.user, **params.validated_data)
        return Response(MonthlyTotalSerializer(months, many=True).data)
