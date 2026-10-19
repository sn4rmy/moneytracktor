from django.contrib import admin

from .models import TransactionImport


@admin.register(TransactionImport)
class TransactionImportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "imported_rows", "created_at", "finished_at")
    list_filter = ("status",)
    search_fields = ("user__username",)
    list_select_related = ("user",)
    readonly_fields = ("imported_rows", "errors", "created_at", "finished_at")
