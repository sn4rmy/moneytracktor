from django.conf import settings
from django.db import models


class ImportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    DONE = "done", "Done"
    FAILED = "failed", "Failed"


class TransactionImport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transaction_imports"
    )
    file = models.FileField(upload_to="imports/")
    status = models.CharField(max_length=10, choices=ImportStatus, default=ImportStatus.PENDING)
    imported_rows = models.PositiveIntegerField(default=0)
    # List of {"row": <line number>, "errors": {<field>: [<message>, ...]}}.
    errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Import #{self.pk} ({self.status})"
