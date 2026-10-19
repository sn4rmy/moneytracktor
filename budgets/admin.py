from django.contrib import admin

from .models import Budget, BudgetNotification


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("category", "user", "monthly_limit", "created_at")
    search_fields = ("category__name", "user__username")
    list_select_related = ("category", "user")
    raw_id_fields = ("user", "category")


@admin.register(BudgetNotification)
class BudgetNotificationAdmin(admin.ModelAdmin):
    list_display = ("budget", "month", "threshold", "sent_at")
    list_filter = ("threshold",)
    list_select_related = ("budget__category",)
    raw_id_fields = ("budget",)
