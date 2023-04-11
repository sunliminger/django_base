from django.db import models, transaction
from django.utils import timezone

from .base import BaseSoftDeletableModel


class Model(BaseSoftDeletableModel):
    delete_at = models.DateTimeField(null=True, editable=False, default=None)
    query_param = models.Q(delete_at__isnull=True)

    def is_soft_deleted(self):
        return self.delete_at is not None

    def soft_delete(self, **kwargs):
        self.delete_at = timezone.now()
        self.save()

    def perform_restore(self, **kwargs):
        self.delete_at = None
        self.save()

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        if deleted:
            qs.update(delete_at=timezone.now())
        else:
            qs.update(delete_at=None)

    class Meta:
        abstract = True
