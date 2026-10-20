from django.contrib import admin

from .models import Account, Category, Transaction, Transfer


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user")
    list_filter = ("type",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user")
    list_filter = ("type",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "amount", "account", "category", "user")
    list_filter = ("type",)
    search_fields = ("note",)
    list_select_related = ("account", "category", "user")


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "from_account", "to_account", "user")
