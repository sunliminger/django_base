"""
    Django认证和权限后端
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from cas import CASClient
from django.apps import apps
from django.conf import settings
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django_cas_ng.signals import cas_user_authenticated

from auth_ext.models import Role, Permission, get_role_permissions
from auth_ext.models.permission import SUDO_PERMISSION, STAFF_PERMISSION, AUTHENTICATED_PERMISSION, ALLOW_ANY_PERMISSION
from auth_ext.mixins import PermMappableMixin
from auth_ext.star_access_client import get_user_relationship_roles
from auth_ext.caches import UserCache

__all__ = ['CASBackend', 'AuthOnlyModelBackend', 'PermBackend', 'PermMappingBackend']


class CASBackend(ModelBackend):
    """CAS authentication backend"""

    def authenticate(self, request, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""
        client = self.get_cas_client(service_url=service, request=request)
        username, attributes, pgtiou = client.verify_ticket(ticket)
        if attributes and request:
            request.session['attributes'] = attributes

        if not username:
            return None
        user = None
        username = self.clean_username(username)

        if attributes:
            reject = self.bad_attributes_reject(request, username, attributes)
            if reject:
                return None

            # If we can, we rename the attributes as described in the settings file
            # Existing attributes will be overwritten
            for cas_attr_name, req_attr_name in settings.CAS_RENAME_ATTRIBUTES.items():
                if cas_attr_name in attributes:
                    attributes[req_attr_name] = attributes[cas_attr_name]
                    attributes.pop(cas_attr_name)

        UserModel = get_user_model()

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if settings.CAS_CREATE_USER:
            user_kwargs = {
                UserModel.USERNAME_FIELD: username
            }
            if settings.CAS_CREATE_USER_WITH_ID:
                user_kwargs['id'] = self.get_user_id(attributes)

            user, created = UserModel._default_manager.get_or_create(**user_kwargs)
            if created:
                user = self.configure_user(user)
        else:
            created = False
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                pass

        if not self.user_can_authenticate(user):
            return None

        if pgtiou and settings.CAS_PROXY_CALLBACK and request:
            request.session['pgtiou'] = pgtiou

        if settings.CAS_APPLY_ATTRIBUTES_TO_USER and attributes:
            # If we are receiving None for any values which cannot be NULL
            # in the User model, set them to an empty string instead.
            # Possibly it would be desirable to let these throw an error
            # and push the responsibility to the CAS provider or remove
            # them from the dictionary entirely instead. Handling these
            # is a little ambiguous.
            user_model_fields = UserModel._meta.fields
            for field in user_model_fields:
                # Handle null -> '' conversions mentioned above
                if not field.null:
                    try:
                        if attributes[field.name] is None:
                            attributes[field.name] = ''
                    except KeyError:
                        continue
                # Coerce boolean strings into true booleans
                if field.get_internal_type() == 'BooleanField':
                    try:
                        boolean_value = attributes[field.name] == 'True'
                        attributes[field.name] = boolean_value
                    except KeyError:
                        continue

            user.__dict__.update(attributes)

            # If we are keeping a local copy of the user model we
            # should save these attributes which have a corresponding
            # instance in the DB.
            if settings.CAS_CREATE_USER:
                user.save()

        # send the `cas_user_authenticated` signal
        cas_user_authenticated.send(
            sender=self,
            user=user,
            created=created,
            attributes=attributes,
            ticket=ticket,
            service=service,
            request=request
        )
        return user

    # ModelBackend has a `user_can_authenticate` method starting from Django
    # 1.10, that only allows active user to log in. For consistency,
    # django-cas-ng will have the same behavior as Django's ModelBackend.
    if not hasattr(ModelBackend, 'user_can_authenticate'):
        def user_can_authenticate(self, user):
            return True

    def get_user_id(self, attributes):
        """
        For use when CAS_CREATE_USER_WITH_ID is True. Will raise ImproperlyConfigured
        exceptions when a user_id cannot be accessed. This is important because we
        shouldn't create Users with automatically assigned ids if we are trying to
        keep User primary key's in sync.
        """
        if not attributes:
            raise ImproperlyConfigured("CAS_CREATE_USER_WITH_ID is True, but "
                                       "no attributes were provided")

        user_id = attributes.get('id')

        if not user_id:
            raise ImproperlyConfigured("CAS_CREATE_USER_WITH_ID is True, but "
                                       "`'id'` is not part of attributes.")

        return user_id

    def clean_username(self, username):
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, changes the username case according to
        `settings.CAS_FORCE_CHANGE_USERNAME_CASE`.
        """
        username_case = settings.CAS_FORCE_CHANGE_USERNAME_CASE
        if username_case == 'lower':
            username = username.lower()
        elif username_case == 'upper':
            username = username.upper()
        elif username_case is not None:
            raise ImproperlyConfigured(
                "Invalid value for the CAS_FORCE_CHANGE_USERNAME_CASE setting. "
                "Valid values are `'lower'`, `'upper'`, and `None`.")
        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        return user

    def bad_attributes_reject(self, request, username, attributes):
        return False

    def get_cas_client(self, service_url=None, request=None):
        """
        initializes the CASClient according to
        the CAS_* settigs
        """
        # Handle CAS_SERVER_URL without protocol and hostname
        server_url = django_settings.IDC_CAS_SERVER_URL
        if server_url and request and server_url.startswith('/'):
            scheme = request.META.get("X-Forwarded-Proto", request.scheme)
            server_url = scheme + "://" + request.META['HTTP_HOST'] + server_url
        # assert server_url.startswith('http'), "settings.CAS_SERVER_URL invalid"
        return CASClient(
            service_url=service_url,
            version=django_settings.CAS_VERSION,
            server_url=server_url,
            extra_login_params=django_settings.CAS_EXTRA_LOGIN_PARAMS,
            renew=django_settings.CAS_RENEW,
            username_attribute=django_settings.CAS_USERNAME_ATTRIBUTE,
            proxy_callback=django_settings.CAS_PROXY_CALLBACK
        )

    def has_perm(self, user_obj, perm, obj=None):
        # 不做权限处理
        return False

    def get_all_permissions(self, user_obj, obj=None):
        # 覆盖父类获取权限方法，不做任何权限处理
        return set()


class AuthOnlyModelBackend(ModelBackend):
    """ 只做认证不做权限验证的ModelBackend后端 """
    def has_perm(self, user_obj, perm, obj=None):
        # 不做任何权限验证操作
        return False

    def get_all_permissions(self, user_obj, obj=None):
        # 覆盖父类获取权限方法，不做任何权限处理
        return set()


class PermBackend(object):
    """ 权限验证后端 """
    perm_cache = caches['auth']

    def authenticate(self, username=None, password=None, **kwargs):
        # 不做认证处理
        return None

    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_active and perm in self.get_all_permissions(user_obj, obj)

    def get_all_permissions(self, user_obj, obj=None):
        """ 获取用户所有权限 """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        cache = UserCache()
        perm_codes = cache.get(user_obj.username, 'permissions')
        if perm_codes:
            # 用户权限缓存命中
            return perm_codes

        perm_codes = {
            *self._get_default_permissions(user_obj, obj),
            *self._get_user_permissions(user_obj, obj),
        }
        cache.set(user_obj.username, 'permissions', perm_codes)

        return perm_codes

    def _get_default_permissions(self, user_obj, obj=None):
        """ 获取系统级别权限 """
        cache = UserCache()
        default_permissions = cache.get(user_obj.username, 'default_permissions')
        if default_permissions:
            return default_permissions

        perms = {ALLOW_ANY_PERMISSION}
        if user_obj.is_authenticated:
            perms.add(AUTHENTICATED_PERMISSION)
            if user_obj.is_staff:
                perms.add(STAFF_PERMISSION)
                if user_obj.is_superuser:
                    perms.add(SUDO_PERMISSION)

                    # 超级管理员拥有所有权限
                    all_perm_codes = set(Permission.objects.all().values_list('code', flat=True))
                    cache.set(user_obj.username, 'default_permissions', all_perm_codes)
                    return all_perm_codes

        default_permissions = {
            *perms,
            *self._get_role_permissions(user_obj, obj),
        }
        cache.set(user_obj.username, 'default_permissions', default_permissions)

        return default_permissions

    def _get_user_permissions(self, user_obj, obj=None):
        """ 获取数据库中配置的用户权限 """
        if not hasattr(user_obj, '_lms_db_perm_cache'):
            user_obj._lms_db_perm_cache = {p.code for p in user_obj.lms_permissions.all()}
        return user_obj._lms_db_perm_cache

    def _get_role_permissions(self, user_obj, obj=None):
        """ 获取用户角色拥有的权限 """
        role_codes = self.get_all_roles(user_obj, obj)
        perm_set = set()
        for role_code in role_codes:
            perm_set.update(get_role_permissions(role_code))
        return perm_set

    def get_all_roles(self, user_obj, obj=None):
        """ 获取用户所有角色 """
        cache = UserCache()
        roles = cache.get(user_obj.username, 'roles')
        if roles:
            # 用户角色缓存命中
            return roles

        roles = {
            *self._get_default_roles(user_obj, obj),
            *self._get_user_roles(user_obj, obj),
        }
        cache.set(user_obj.username, 'roles', roles)
        return roles

    def _get_default_roles(self, user_obj, obj=None):
        """ 获取系统默认用户角色code """
        cache = UserCache()
        default_roles = cache.get(user_obj.username, 'default_roles')
        if default_roles:
            return default_roles

        default_roles = get_user_relationship_roles(user_obj.username)
        cache.set(user_obj.username, 'default_roles',  default_roles)
        return default_roles

    def _get_user_roles(self, user_obj, obj=None):
        """ 获取数据库中配置的用户所有角色 """
        role_codes = {r.code for r in user_obj.lms_roles.all()}
        return role_codes


class PermMappingBackend(object):
    """ 权限映射model的权限后端 """
    def authenticate(self, username=None, password=None, **kwargs):
        # 不做认证处理
        return None

    def has_perm(self, user_obj, perm, obj=None):
        try:
            app_label, rest = perm.split('.')
            model_name = rest.split('_', 1)[-1]
            model_class = apps.get_model(app_label, model_name)
        except:
            return False

        if issubclass(model_class, PermMappableMixin):
            # 处理做过权限映射的model
            mapped_perm, mapped_obj = model_class.mapping_permission(perm, obj=obj)
            if mapped_perm:
                # 验证用户是否拥有上级权限
                return user_obj.has_perm(mapped_perm, obj=mapped_obj)
        return False
