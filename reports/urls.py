from django.urls import path

from .views import CategoryReportView, MonthlyReportView, SummaryReportView

urlpatterns = [
    path("reports/summary", SummaryReportView.as_view(), name="report-summary"),
    path("reports/by-category", CategoryReportView.as_view(), name="report-by-category"),
    path("reports/monthly", MonthlyReportView.as_view(), name="report-monthly"),
]
