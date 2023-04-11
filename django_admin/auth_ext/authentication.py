import json
import time
import logging
from rest_framework import authentication as drf_authentication, exceptions
from django.conf import settings
from django.apps import apps
from django_redis import get_redis_connection
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from rest_framework_jwt import authentication as jwt_authentication
from .models import Token
from auth_ext.caches import UserCache


_TOKEN_CACHE_KEY = 'NEW_LMS_TOKEN_CACHE'        # 缓存的token白名单


def get_token_by_user(user):
    """ 缓存中获取token """
    client = get_redis_connection('default')
    token = client.hget(_TOKEN_CACHE_KEY, user.pk)
    return token


def set_token(user, token):
    """ 缓存token """
    client = get_redis_connection('default')
    client.hset(_TOKEN_CACHE_KEY, user.pk, token)
    UserCache().clear(user.username)    # 用户重新登录时清空权限缓存


def validate_token(user, token):
    """ 验证token """
    exist_token = get_token_by_user(user)
    return exist_token and exist_token == token


def delete_token(user):
    """ 删除token """
    client = get_redis_connection('default')
    client.hdel(_TOKEN_CACHE_KEY, user.pk)


def add_access_log(name, sid, uri):
    access_logger = logging.getLogger('access_log')
    try:
        data = {
            "name": name,
            "sid": sid,
            "action_time": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
            "uri": uri,
            "system": "new_lms"
        }
        access_logger.info(msg=json.dumps(data))
    except Exception as e:
        pass


class JSONWebTokenAuthentication(jwt_authentication.JSONWebTokenAuthentication):
    def authenticate(self, request):
        """ 重写jwt认证方法从缓存token白名单中验证 """
        auth = super().authenticate(request)
        if auth and not validate_token(*auth):
            raise exceptions.AuthenticationFailed('认证失效，请重新登录')

        # 添加访问日志
        if auth:
            add_access_log(str(auth[0]), auth[1], request.path)

        return auth


class TokenAuthentication(drf_authentication.TokenAuthentication):
    """ 外部用户token认证后端 """
    keyword = 'Bearer'
    model = Token

    def authenticate_credentials(self, key):
        external_user = Token.get_token(key)
        if external_user is None:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        if external_user.expire > 0 and timezone.now() > external_user.expires_at:
            raise exceptions.AuthenticationFailed(_("Token has expired."))

        user = AnonymousUser()
        setattr(user, 'is_external_user', True)
        setattr(user, 'external_user', external_user)

        return user, key

    def authenticate(self, request):
        auth = super().authenticate(request)

        # 添加访问日志
        if auth:
            add_access_log(str(auth[0].external_user), auth[1], request.path)

        return auth


# ============================================= 认证后门 ==============================================
class TestUserTokenAuthentication(drf_authentication.TokenAuthentication):
    """
    django-rest-framework的认证是按照REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']先后顺序认证的，
    故该认证后端需要放在最前
    """
    def authenticate_credentials(self, key):
        TEST_TOKEN_USER_MAPPING = getattr(settings, 'TEST_TOKEN_USER_MAPPING', {})
        username = TEST_TOKEN_USER_MAPPING.get(key, None)
        if not username:
            return None

        user_model = apps.get_model(settings.AUTH_USER_MODEL)
        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        return user, key

    def authenticate(self, request):
        auth = super().authenticate(request)

        # 添加访问日志
        if auth:
            add_access_log(str(auth[0]), auth[1], request.path)

        return auth

