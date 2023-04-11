from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from functools import wraps


def has_perm(perm_code, msg=None):
    """
    接口权限判断

    @has_perm('app_label.add_modelname')
    def post(self, request, *args, **kwargs):
        ...

    @has_perm('app_label.view_modelname', '您没有查看xxx的权限')
    def get(self, request, *args, **kwargs):
        ...

    :param perm_code: 权限code
    :param msg: 错误提示信息
    :return:
    """
    if not msg:
        msg = _('You do not have permission to perform this action.')

    def _decorator(view_func):
        @wraps(view_func)
        def _wrapper(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not isinstance(request, (Request, HttpRequest)):
                for arg in args:
                    if not isinstance(arg, (Request, HttpRequest)):
                        continue
                    user = arg.user
                    break

            if not user or not user.has_perm(perm_code):
                raise PermissionDenied(msg)
            return view_func(request, *args, **kwargs)
        return _wrapper
    return _decorator


