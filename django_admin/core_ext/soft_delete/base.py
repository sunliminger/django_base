from django.db import models, transaction
from django.conf import settings
from .signals import *


class BaseExistQuerySet(models.QuerySet):
    def delete(self, soft=None):
        """
        逻辑删除接口
        :param soft: True表示逻辑删除，False表示物理删除
        :return:
        """
        if soft is None:
            soft = self.model._soft_delete_flag
        if not soft:
            super().delete()
        self.soft_delete()

    @transaction.atomic
    def soft_delete(self):
        """ 逻辑删除 """
        self.model.batch_soft_delete(qs=self, deleted=True)


class BaseTrashQuerySet(models.QuerySet):
    def delete(self, soft=None):
        """
        逻辑删除
        :param soft: True表示从该QuerySet删除，即恢复逻辑存在，False表示物理删除
        :return:
        """
        if soft is None:
            soft = self.model._soft_delete_flag
        if not soft:
            super().delete()
        self.restore()

    @transaction.atomic
    def restore(self):
        """ 将已被逻辑删除的对象恢复 """
        self.model.queryset_logical_delete(qs=self, deleted=False)


class ExistManager(models.Manager):
    def get_queryset(self):
        return self.model._exist_queryset(**{
            'model': self.model,
            'using': self._db,
        }).filter(self.model.get_query_param())


class TrashManager(models.Manager):
    def get_queryset(self):
        return self.model._trash_queryset(**{
            'model': self.model,
            'using': self._db,
        }).exclude(self.model.get_query_param())


class BaseSoftDeletableModel(models.Model):
    """
    逻辑删除Model基类
    query_param/get_query_param：
        通过重写query_param或get_query_param来实现各类逻辑存在条件的判断（布尔值，
        删除时间，uuid等）
    _soft_delete:
        Model层面上控制默认调用delete是否为逻辑删除，即delete方法中soft参数的默认值
    querysets:
        QuerySet提供两种默认的查询集，可自定义实现
    必须实现的方法：
        * is_soft_deleted(): 判断是否逻辑删除
        * soft_delete(): 实现逻辑删除的方法
        * perform_restore(): 恢复逻辑删除的方法
        * batch_soft_delete(): 针对查询集的逻辑删除操作
    """
    query_param = models.Q()                    # 逻辑存在查询条件
    _soft_delete_flag = True                    # 是否逻辑删除

    _exist_queryset = BaseExistQuerySet         # 逻辑存在查询集
    _trash_queryset = BaseTrashQuerySet         # 逻辑删除查询集

    objects = ExistManager()                    # 逻辑存在
    trashes = TrashManager()                    # 逻辑删除
    all_objects = models.Manager()              # 物理存在

    @classmethod
    def get_query_param(cls):
        """ 通过重写该方法实现逻辑关系映射，自定义删除条件等功能 """
        return cls.query_param

    @transaction.atomic
    def delete(self, soft=None, using=None, keep_parents=False):
        """ 自定义删除信号要将django删除信号包裹在内 """
        if soft is None:
            soft = self._soft_delete_flag
        if not soft:
            pre_hard_delete.send(
                sender=self.__class__,
                instance=self,
                using=using
            )
            related_data = super(BaseSoftDeletableModel, self).delete(using=using, keep_parents=keep_parents)
            post_hard_delete.send(
                sender=self.__class__,
                instance=self,
                using=using
            )
            return related_data

        pre_soft_delete.send(
            sender=self.__class__,
            instance=self,
            using=using
        )
        models.signals.pre_delete.send(
            sender=self.__class__,
            instance=self,
            using=using
        )
        self.soft_delete(using=using, keep_parents=keep_parents)
        models.signals.post_delete.send(
            sender=self.__class__,
            instance=self,
            using=using
        )
        post_soft_delete.send(
            sender=self.__class__,
            instance=self,
            using=using
        )

    @transaction.atomic
    def restore(self, **kwargs):
        using = kwargs.get('using', settings.DATABASES['default'])
        pre_restore.send(
            sender=self.__class__,
            instance=self,
            using=using
        )
        self.perform_restore(**kwargs)
        post_restore.send(
            sender=self.__class__,
            instance=self,
            using=using
        )

    def is_soft_deleted(self):
        """ 判断是否已删除 """
        raise NotImplementedError

    def soft_delete(self, **kwargs):
        """ 逻辑删除方法 """
        raise NotImplementedError

    def perform_restore(self, **kwargs):
        """ 恢复逻辑删除方法 """
        raise NotImplementedError

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        """
        查询集操作
        :param qs: 需要搜索的查询集
        :param deleted: 是否删除
        :return:
        """
        raise NotImplementedError

    class Meta:
        abstract = True
