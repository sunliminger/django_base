from dataclasses import dataclass
from django.db import models, transaction
from django.conf import settings
from core_ext.mixins import OperateCreateUpdateDeleteViewMixin
from core_ext.soft_delete import BaseSoftDeletableModel
from core_ext.exceptions import ProcessError
from utils import gen_random_name
from auth_ext.caches import RoleCache


def get_role_permissions(role_code):
    role_cache = RoleCache()
    perm_codes = role_cache.get(role_code, 'permissions')
    if perm_codes is None:
        role_obj = Role.objects.filter(code=role_code).prefetch_related('permissions').first()
        if role_obj:
            perm_codes = {p.code for p in role_obj.permissions.all()}
            role_cache.set(role_code, 'permissions', perm_codes)
    return perm_codes


def _clean_role_permissions_cache(role_code):
    """ 清除角色缓存信息，在角色权限信息修改后使用 """
    RoleCache().clear(role_code)


class Role(OperateCreateUpdateDeleteViewMixin, BaseSoftDeletableModel, models.Model):
    code = models.CharField(max_length=100, editable=False, default=gen_random_name, verbose_name='编码')
    name = models.CharField(max_length=100, verbose_name='名称')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='lms_roles', through='UserRoleMapping',
                                   through_fields=('role', 'user'), verbose_name='角色')
    permissions = models.ManyToManyField('Permission', through='RolePermissionMapping',
                                         through_fields=('role', 'permission'), verbose_name='权限')
    CHOICES_OF_ROLE_KIND = (
        (0, '自定义'),
        (1, '销售'),
        (2, '客服'),
        (3, '仓储'),
        (4, '物流'),
        (5, '财务'),
        (6, '研发'),
    )
    kind = models.IntegerField(default=0, choices=CHOICES_OF_ROLE_KIND, verbose_name='角色类型')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'nlms_role'

    @property
    def is_system_role(self):
        """ 判断是否系统级角色 """
        return self.pk <= 100

    @property
    def user_ids(self):
        return [i.user_id for i in self.user_map.all()]

    def _set_user_ids(self, object_ids):
        if object_ids is None:
            # 为空不做处理，置空应传入[]
            return

        mapping_model = UserRoleMapping
        related_query = self.user_map

        exists_ids = {i.user_id for i in related_query.all()}
        append_ids, delete_ids = set(object_ids) - exists_ids, exists_ids - set(object_ids)
        append_list = [mapping_model(user_id=i, role=self) for i in append_ids]
        mapping_model.objects.bulk_create(append_list)
        related_query.filter(user_id__in=delete_ids).delete()

    @property
    def permission_ids(self):
        return [i.permission_id for i in self.permission_map.all()]

    def _set_permission_ids(self, object_ids):
        if object_ids is None:
            # 为空不做处理，置空应传入[]
            return

        mapping_model = RolePermissionMapping
        related_query = self.permission_map

        exists_ids = {i.permission_id for i in related_query.all()}
        append_ids, delete_ids = set(object_ids) - exists_ids, exists_ids - set(object_ids)
        append_list = [mapping_model(permission_id=i, role=self) for i in append_ids]
        mapping_model.objects.bulk_create(append_list)
        related_query.filter(permission_id__in=delete_ids).delete()

        # 修改后清除权限缓存
        _clean_role_permissions_cache(self.code)

    # ==================================== 逻辑删除实现 =====================================
    FLAG_DELETED = 1
    FLAG_EXISTS = 0
    CHOICES_DELETE_TYPE = (
        (FLAG_DELETED, '删除'),
        (FLAG_EXISTS, '可用'),
    )
    is_deleted = models.IntegerField(choices=CHOICES_DELETE_TYPE, default=FLAG_EXISTS, verbose_name='删除标记')

    query_param = models.Q(is_deleted=FLAG_EXISTS)                  # 逻辑存在查询条件

    def is_soft_deleted(self):
        """ 判断是否已删除 """
        return self.is_deleted == self.FLAG_DELETED

    def soft_delete(self, **kwargs):
        """ 逻辑删除方法 """
        if self.is_system_role:
            raise ProcessError('系统默认角色无法删除')
        self.is_deleted = self.FLAG_DELETED
        self.save(update_fields=['is_deleted', ])

    def perform_restore(self, **kwargs):
        """ 恢复逻辑删除方法 """
        self.is_deleted = self.FLAG_EXISTS
        self.save(update_fields=['is_deleted', ])

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        """
        查询集操作
        :param qs: 需要搜索的查询集
        :param deleted: 是否删除
        :return:
        """
        qs.update(is_deleted=cls.FLAG_DELETED if deleted else cls.FLAG_EXISTS)

    # ==================================== 用户操作方法 =======================================
    default_log_fields = ['code', 'name', 'user_ids', 'permission_ids', ]

    @classmethod
    def _create(cls, **validated_data):
        user_ids = validated_data.pop('user_ids', None)
        permission_ids = validated_data.pop('permission_ids', None)
        role_obj = cls(**validated_data)

        with transaction.atomic():
            role_obj.save()
            role_obj._set_user_ids(user_ids)
            role_obj._set_permission_ids(permission_ids)
            role_obj.refresh_from_db()

        return role_obj

    def _update(self, **validated_data):
        user_ids = validated_data.pop('user_ids', None)
        permission_ids = validated_data.pop('permission_ids', None)
        if not self.is_system_role:
            # 系统角色不可修改基础信息
            for k, v in validated_data.items():
                if hasattr(self, k):
                    setattr(self, k, v)

        with transaction.atomic():
            self.save()
            self._set_user_ids(user_ids)
            self._set_permission_ids(permission_ids)
            self.refresh_from_db()
        return self

    @classmethod
    def pretty(cls, queryset):
        """ 格式化Role QuerySet """
        @dataclass
        class _Pretty:
            kind: int
            kind_name: str
            roles: list

        data_dict = {k: {'kind': k, 'kind_name': kn, 'roles': []} for k, kn in cls.CHOICES_OF_ROLE_KIND}
        for item in queryset:
            data_dict.get(item.kind, data_dict[0])['roles'].append(item)
        return [_Pretty(**d) for d in data_dict.values()]


class UserRoleMapping(models.Model):
    """ 用户和角色的多对多映射表 """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='role_map',
                             verbose_name='关联用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_map', verbose_name='关联角色')

    class Meta:
        db_table = 'nlms_user_role'
        default_permissions = ()


class RolePermissionMapping(models.Model):
    """ 角色和权限的多对多映射表 """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permission_map', verbose_name='关联角色')
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE, verbose_name='关联权限')

    class Meta:
        db_table = 'nlms_role_permission'
        default_permissions = ()
