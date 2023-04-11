"""
    Django Rest Framework的权限后端重写，如果一个view有多个权限后端，则必须所有权限后端都返回True，否则定义为无权限
"""
from rest_framework import permissions as drf_permissions
from auth_ext.mixins import CreatorMixin, OwnerMixin


class DefaultPermission(drf_permissions.BasePermission):
    """
    LMS默认基础权限认证
    api接口需要已认证用户，openapi接口需要外部系统用户认证
    """
    def has_permission(self, request, view):
        try:
            url_prefix = request.path.strip('/').split('/', 1)[0]
        except Exception as e:
            return False
        if url_prefix in ['api', 'docs']:
            return bool(request.user and request.user.is_authenticated)
        elif url_prefix in ['openapi', ]:
            return bool(request.user and getattr(request.user, 'external_user', None))
        elif url_prefix in ['open-docs', ]:
            return True
        return False


class IsExternalUser(drf_permissions.BasePermission):
    """
    Allows access only to external users.
    """
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'external_user', None))


class IsAuthenticatedOrExternalUser(drf_permissions.BasePermission):
    """
    web用户或者其他系统用户都可以访问
    """
    def has_permission(self, request, view):
        return bool(request.user and bool(request.user.is_authenticated or getattr(request.user, 'external_user', None)))


class IsCreator(drf_permissions.BasePermission):
    """
    实现了auth_ext.mixins.CreatorMixin的Model可以判断是否是创建者

    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, CreatorMixin):
            return True
        return bool(request.user and request.user == obj.get_creator())


class IsOwner(drf_permissions.BasePermission):
    """
    实现了auth_ext.mixins.OwnerMixin的Model可以判断是否是拥有者

    """
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, OwnerMixin):
            return True
        return bool(request.user and request.user == obj.get_owner())
