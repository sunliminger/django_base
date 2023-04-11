"""
    外部系统使用的认证model，OpenAPI使用
"""
import binascii
import os
import datetime
from django.db import models
from django.utils import timezone
from django.utils.cache import caches
from django.utils.translation import gettext_lazy as _
from core_ext.lock import RedisLock


class ExternalUser(models.Model):
    DEFAULT_EXPIRES = 60*60*24*30       # 默认超时时间（秒）
    username = models.CharField(max_length=40, unique=True, verbose_name='用户名称')
    refresh_token = models.CharField(max_length=100, unique=True, editable=False, verbose_name='刷新token')
    expire = models.PositiveIntegerField(default=DEFAULT_EXPIRES, verbose_name='token超时时间')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'nlms_external_user'
        verbose_name = '外部系统用户'
        verbose_name_plural = '外部系统用户'

    def save(self, *args, **kwargs):
        if not self.refresh_token:
            self.update_refresh_token()
        return super().save(*args, **kwargs)

    def update_refresh_token(self):
        self.refresh_token = binascii.hexlify(os.urandom(40)).decode()


class Token(models.Model):
    """
    OpenAPI使用的
    """
    key = models.CharField(_("Key"), max_length=40)
    user = models.OneToOneField(
        ExternalUser, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now=True)

    class Meta:
        db_table = 'nlms_auth_token'
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")
        default_permissions = ()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    @property
    def cache_key(self):
        return f'auth_token{self.key}'

    @property
    def cache(self):
        return caches['default']

    def _del_cache(self):
        """ 清除缓存 """
        self.cache.delete(self.cache_key)

    def _set_cache(self):
        """ 设置缓存 """
        setattr(self.user, 'expires_at', self.created + datetime.timedelta(seconds=self.user.expire))
        self.cache.set(self.cache_key, self.user, timeout=60*30)

    @classmethod
    @RedisLock(get_lock_name=lambda *args, **kwargs: str(args[1]) if len(args) > 1 else str(kwargs.get('user')))
    def op_refresh(cls, user):
        time_now = timezone.now()
        token, created = Token.objects.select_related('user').get_or_create(user=user)
        if created:
            return token

        if token.created + datetime.timedelta(seconds=user.expire) < time_now:
            # token已失效
            token.key = None
        token.save()
        token._set_cache()
        return token

    @classmethod
    def get_token(cls, key):
        cache = caches['default']
        cache_key = f'auth_token{key}'
        user = cache.get(cache_key)
        if user:
            return user

        try:
            token = cls.objects.select_related('user').get(key=key)
        except models.ObjectDoesNotExist:
            return None
        token._set_cache()
        return token.user
