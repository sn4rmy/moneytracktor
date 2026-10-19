from django.contrib import admin

from .models import Account, Category, Transaction, Transfer


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "type", "currency", "created_at")
    list_filter = ("type", "currency")
    search_fields = ("name", "user__username")
    list_select_related = ("user",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user")
    list_filter = ("type",)
    search_fields = ("name", "user__username")
    list_select_related = ("user",)


class TransferTransactionInline(admin.TabularInline):
    model = Transaction
    fields = ("account", "type", "amount", "date", "note")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "rate", "created_at")
    search_fields = ("user__username",)
    list_select_related = ("user",)
    inlines = (TransferTransactionInline,)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "account", "type", "category", "amount")
    list_filter = ("type", "account__currency")
    search_fields = ("note", "user__username")
    date_hierarchy = "date"
    list_select_related = ("user", "account", "category")
    raw_id_fields = ("user", "account", "category", "transfer")
