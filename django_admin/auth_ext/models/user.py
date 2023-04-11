from django.contrib import auth
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from core_ext.mixins import OperateUpdateMixin
from .permission import Permission
from auth_ext.caches import UserCache


def _get_user_roles(user, obj=None):
    role_set = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_roles"):
            role_set.update(backend.get_all_roles(user, obj))
    return role_set


def _clean_user_auth_cache(username):
    """ 清除user的权限缓存，该用户权限变化后使用，不影响默认权限和角色 """
    cache = UserCache()
    cache.clear(username)


class User(OperateUpdateMixin, AbstractUser):
    lms_permissions = models.ManyToManyField(Permission, related_name='user_set',
                                             through='UserPermission', through_fields=('user', 'permission'))

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'user'
        default_permissions = ('change', )

    @property
    def role_ids(self):
        return [i.role_id for i in self.role_map.all()]

    def _set_role_ids(self, object_ids):
        if object_ids is None:
            # 为空不做处理，置空应传入[]
            return

        mapping_model = self.role_map.model
        related_query = self.role_map

        exists_ids = {i.role_id for i in related_query.all()}
        append_ids, delete_ids = set(object_ids) - exists_ids, exists_ids - set(object_ids)
        append_list = [mapping_model(role_id=i, user=self) for i in append_ids]
        mapping_model.objects.bulk_create(append_list)
        related_query.filter(role_id__in=delete_ids).delete()

    @property
    def permission_ids(self):
        return [i.permission_id for i in self.permission_map.all()]

    def _set_permission_ids(self, object_ids):
        if object_ids is None:
            # 为空不做处理，置空应传入[]
            return

        mapping_model = self.permission_map.model
        related_query = self.permission_map

        exists_ids = {i.permission_id for i in related_query.all()}
        append_ids, delete_ids = set(object_ids) - exists_ids, exists_ids - set(object_ids)
        append_list = [mapping_model(permission_id=i, user=self) for i in append_ids]
        mapping_model.objects.bulk_create(append_list)
        related_query.filter(permission_id__in=delete_ids).delete()

    # ================================= PermissionMixin方法拓展 ===============================
    def has_perm(self, perm, obj=None):
        """ 重写权限判定方法 """
        if not self.is_active:
            return False
        if self.is_staff and self.is_superuser:
            # 超级用户定义为is_staff and is_superuser
            return True

        # 逻辑来自django.contrib.auth.models._user_has_perm, User和AnonymousUser共用
        for backend in auth.get_backends():
            if not hasattr(backend, 'has_perm'):
                continue
            try:
                if backend.has_perm(self, perm, obj):
                    return True
            except PermissionDenied:
                return False
        return False

    def get_all_permission_objs(self, obj=None):
        perm_codes = self.get_all_permissions(obj)
        perm_objs = set(Permission.objects.filter(code__in=perm_codes))

        default_permissions = self.get_default_permissions(obj)
        for perm_obj in perm_objs:
            perm_obj.disabled = perm_obj.code in default_permissions
        return perm_objs

    def get_default_permissions(self, obj=None):
        from auth_ext.backends import PermBackend
        return PermBackend()._get_default_permissions(self, obj)

    def get_all_roles(self, obj=None):
        return _get_user_roles(self, obj)

    def get_all_role_objs(self, obj=None):
        from auth_ext.models.role import Role
        role_codes = self.get_all_roles(obj)
        role_objs = set(Role.objects.filter(code__in=role_codes))
        return role_objs

    # ==================================== 用户操作方法 =======================================
    default_log_fields = ['username', 'role_ids', 'permission_ids', ]

    def _update(self, **validated_data):
        # 重写update方法以自定义更新op_update方法
        permission_ids = validated_data.pop('permission_ids', None)
        role_ids = validated_data.pop('role_ids', None)

        with transaction.atomic():
            self._set_permission_ids(permission_ids)
            self._set_role_ids(role_ids)
            # 清除用户权限缓存
            _clean_user_auth_cache(self.username)
            self.refresh_from_db()


class UserPermission(models.Model):
    """ 用户和权限的多对多映射表 """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_map', verbose_name='关联用户')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, verbose_name='关联权限')

    class Meta:
        db_table = 'nlms_user_permission'
        default_permissions = ()


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    entity = models.CharField(max_length=64, default='', blank=True)
    limit = models.CharField(max_length=1000, default='', blank=True)

    def __str__(self):
        return str(self.user) + str(self.group)

    class Meta:
        db_table = 'membership'
        default_permissions = ()
