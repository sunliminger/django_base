from django.db import models, transaction

from .base import BaseSoftDeletableModel


class Model(BaseSoftDeletableModel):
    is_deleted = models.BooleanField(default=False, editable=False)
    query_param = models.Q(enable=True)

    def is_soft_deleted(self):
        return self.is_deleted

    def soft_delete(self, **kwargs):
        self.is_deleted = True
        self.save()

    def perform_restore(self, **kwargs):
        self.is_deleted = False
        self.save()

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        qs.update(is_deleted=deleted)

    class Meta:
        abstract = True
