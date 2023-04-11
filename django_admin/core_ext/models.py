from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """ 用户操作基类，用于需要记录用户操作的基础信息表 """
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='+', verbose_name='创建人')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='+', verbose_name='最后更新人')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        abstract = True
