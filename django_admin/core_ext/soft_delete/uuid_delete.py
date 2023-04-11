from django.db import models, transaction
import uuid

from .base import BaseSoftDeletableModel


class Model(BaseSoftDeletableModel):
    deleted = models.UUIDField(null=True, editable=False, default=None)
    query_param = models.Q(deleted__isnull=True)

    def is_soft_deleted(self):
        return self.deleted is not None

    def soft_delete(self, **kwargs):
        self.deleted = uuid.uuid4()
        self.save()

    def perform_restore(self, **kwargs):
        self.deleted = None
        self.save()

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        if not deleted:
            qs.update(deleted=None)
            return
        for item in qs:
            item.deleted = uuid.uuid4()
            item.save()

    class Meta:
        abstract = True
