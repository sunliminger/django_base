from dataclasses import dataclass
from django.db import models, transaction
from django.apps import apps as default_apps
from auth_ext.mixins import PermMappableMixin
from core_ext.soft_delete import BaseSoftDeletableModel


def get_app_config(app_label, apps=default_apps):
    return apps.app_configs.get(app_label)


def get_model(app_label, model_name, apps=default_apps):
    try:
        return apps.get_model(app_label, model_name)
    except:
        return None


class Permission(BaseSoftDeletableModel, models.Model):
    code = models.CharField(max_length=255, unique=True, verbose_name='权限编码')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='权限名')
    desc = models.CharField(max_length=255, null=True, blank=True, verbose_name='描述')
    app_label = models.CharField(max_length=255, null=True, blank=True, verbose_name='app')
    model_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='模型名')
    STATUS_ENABLE = 1
    STATUS_DISABLE = 0
    CHOICES_PERM_TYPE = (
        (STATUS_ENABLE, '激活'),
        (STATUS_DISABLE, '禁用'),
    )
    status = models.IntegerField(choices=CHOICES_PERM_TYPE, default=STATUS_ENABLE, verbose_name='权限类型')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = 'nlms_permission'
        ordering = ('app_label', 'model_name', 'code')
        default_permissions = ('view', )

    @property
    def is_system_permission(self):
        """ 判断是否系统级权限 """
        return self.pk <= 10

    @property
    def disabled(self):
        """ 方便前端配置的标识位（是否禁止修改） """
        return getattr(self, '_disabled', False)

    @disabled.setter
    def disabled(self, value):
        self._disabled = bool(value)

    # 实现逻辑删除方法
    query_param = ~models.Q(status=STATUS_DISABLE)                  # 逻辑存在查询条件

    def is_soft_deleted(self):
        """ 判断是否已删除 """
        return self.status == self.STATUS_DISABLE

    def soft_delete(self, **kwargs):
        """ 逻辑删除方法 """
        self.status = self.STATUS_DISABLE
        self.save(update_fields=['status', ])

    def perform_restore(self, **kwargs):
        """ 恢复逻辑删除方法 """
        self.status = self.STATUS_ENABLE
        self.save(update_fields=['status', ])

    @classmethod
    @transaction.atomic
    def batch_soft_delete(cls, qs, deleted, **kwargs):
        """
        查询集操作
        :param qs: 需要搜索的查询集
        :param deleted: 是否删除
        :return:
        """
        qs.update(status=cls.STATUS_DISABLE if deleted else cls.STATUS_ENABLE)

    @classmethod
    def pretty(cls, queryset):
        """ 格式化Permission QuerySet """
        @dataclass
        class _Pretty:
            code: str
            name: str
            children: list

        # 获取权限层级字典 app -> model -> permission
        perm_dict = {}
        for p in queryset:
            perm_dict.setdefault(p.app_label, {}).setdefault(p.model_name, []).append(p)

        pretty_perms = []
        # 处理系统级权限
        system_perm_dict = perm_dict.pop(None, {})
        if system_perm_dict:
            pretty_perms.append(
                _Pretty(code=None, name='系统', children=[
                    _Pretty(code=None, name='系统', children=system_perm_dict.get(None))
                ])
            )

        # 按照app进行权限分层
        for app_label, model_perm_dict in perm_dict.items():
            app = get_app_config(app_label)
            app_name = app.verbose_name if app else app_label
            model_pretty = []
            for model_name, perms in model_perm_dict.items():
                model_class = get_model(app_label, model_name)
                model_label = model_class._meta.verbose_name if model_class else model_name
                model_pretty.append(_Pretty(code=model_name, name=model_label, children=perms))
            pretty_perms.append(_Pretty(code=app_label, name=app_name, children=model_pretty))

        return pretty_perms


SUDO_PERMISSION = 'lms.sudo'                            # 超级用户权限
STAFF_PERMISSION = 'lms.staff'                          # 后台管理员用户权限
AUTHENTICATED_PERMISSION = 'lms.is_authenticated'       # 登录用户才有的权限
ALLOW_ANY_PERMISSION = 'lms.allow_any'                  # 所有人都有的权限(不需要额外配置)


class PermissionDetector(object):
    """ 权限收集器 """

    # 系统级权限，通过fixture强制指定
    DEFAULT_PERMISSIONS = (
        SUDO_PERMISSION,
        STAFF_PERMISSION,
        AUTHENTICATED_PERMISSION,
        ALLOW_ANY_PERMISSION,
    )
    # 不收集权限的app
    NO_DETECT_APP = (
        'admin',
        'auth',
        'contenttypes',
        'django',
        'django_cas_ng',
        'elm',
        'menu',
        'sessions',
    )
    # 不收集权限的model
    NO_DETECT_MODEL = (
        # app_label, model_name
        ('auth_ext', 'user_groups'),
        ('auth_ext', 'user_user_permissions'),
    )
    ACTION_DESC = {
        'add': '添加',
        'change': '修改',
        'delete': '删除',
        'view': '查看',
        'submit': '提交',
        'audit': '审核',
        'revoke': '撤销',
        'reject': '驳回',
        'copy': '复制',
        'import': '导入'
    }

    def __init__(self, apps=None):
        if apps is None:
            apps = default_apps
        self.apps = apps

        _exists_permission = Permission.all_objects.all()
        self.exists_permissions = {p.code: p for p in _exists_permission}                   # 数据库存在的权限
        self.detect_codes = set(self.DEFAULT_PERMISSIONS)                                   # 探测到的权限code
        self.append_permissions = []                                                        # 待添加的权限obj
        self.update_permissions = []                                                        # 待更新的权限obj

    def _collect_permission(self, code, perm_name, model_meta):
        """ 收集到一个权限 """
        self.detect_codes.add(code)
        if code not in self.exists_permissions:
            # 新增权限
            self.append_permissions.append(Permission(**{
                'code': code,
                'name': perm_name,
                'app_label': model_meta.app_label,
                'model_name': model_meta.model_name,
            }))
        else:
            # 更新权限
            perm_obj = self.exists_permissions.get(code)
            perm_obj.name = perm_name
            perm_obj.app_label = model_meta.app_label
            perm_obj.model_name = model_meta.model_name
            perm_obj.status = Permission.STATUS_ENABLE      # 状态设为启用
            self.update_permissions.append(perm_obj)

    def _detect_model_permissions(self, model_class):
        """ 收集一个model的权限 """
        model_meta = model_class._meta
        if model_meta.permissions:
            # 优先收集显式定义的权限
            for perm_code, perm_name in model_meta.permissions:
                code = f'{model_meta.app_label}.{perm_code}'
                self._collect_permission(code, perm_name, model_meta)

        elif model_meta.default_permissions:
            # 无显示权限定义时收集默认权限
            for perm_code in model_meta.default_permissions:
                code = f'{model_meta.app_label}.{perm_code}_{model_meta.model_name}'
                perm_name = f'{self.ACTION_DESC.get(perm_code, perm_code)}{model_meta.verbose_name}'
                self._collect_permission(code, perm_name, model_meta)

    def auto_discover_permissions(self):
        """ 项目运行时自动收集权限 """
        for app_label, model_dict in self.apps.all_models.items():
            if app_label in self.NO_DETECT_APP:
                # 跳过不需要收集权限的app
                continue

            for model_name, model_class in model_dict.items():
                if issubclass(model_class, PermMappableMixin):
                    # 实现权限映射的model不收集权限
                    continue
                if (app_label, model_name) in self.NO_DETECT_MODEL:
                    # 跳过不需要收集权限的model
                    continue
                self._detect_model_permissions(model_class)

        delete_codes = set(self.exists_permissions.keys()) - self.detect_codes      # 待删除 = 数据库存在 - 最新检测到的
        delete_qs = Permission.objects.exclude(code__in=self.DEFAULT_PERMISSIONS).filter(code__in=delete_codes)
        delete_count = delete_qs.count()
        with transaction.atomic():
            delete_qs.delete()
            Permission.all_objects.bulk_create(self.append_permissions)
            Permission.all_objects.bulk_update(self.update_permissions, batch_size=500,
                                               fields=['name', 'app_label', 'model_name', 'status'])
        return {
            'detect': len(self.detect_codes), 'default': len(self.DEFAULT_PERMISSIONS),
            'create': len(self.append_permissions), 'update': len(self.update_permissions), 'delete': delete_count,
        }
