from django.core import exceptions


class OperateCreateMixin(object):
    """
    创建操作。
    """
    @classmethod
    def op_create(cls, user, **validated_data):
        if hasattr(cls, '_create') and callable(cls._create):
            if not user.has_perm('%s.add_%s' % (cls._meta.app_label, cls._meta.model_name)):
                raise exceptions.PermissionDenied()
            # 自定义方法默认不检测对象级权限
            obj = cls._create(**validated_data)
            return obj

        obj = cls(**validated_data)
        if not user.has_perm('%s.add_%s' % (cls._meta.app_label, cls._meta.model_name), obj=obj):
            raise exceptions.PermissionDenied()

        obj.save()
        return obj


class OperateUpdateMixin(object):
    """
    更新操作。
    """
    def op_update(self, user, **validated_data):
        if not user.has_perm('%s.change_%s' % (self._meta.app_label, self._meta.model_name), obj=self):
            raise exceptions.PermissionDenied()

        if hasattr(self, '_update') and callable(self._update):
            self._update(**validated_data)
        else:
            for key, val in validated_data.items():
                setattr(self, key, val)
            self.save(update_fields=validated_data.keys())
        return self


class OperateDeleteMixin(object):
    """
    销毁操作。
    """
    def op_delete(self, user):
        if not user.has_perm('%s.delete_%s' % (self._meta.app_label, self._meta.model_name), obj=self):
            raise exceptions.PermissionDenied()

        self.delete()
        return self


class OperateViewMixin(object):
    """
    读数据操作。
    """
    def op_view(self, user):
        if not user.has_perm('%s.view_%s' % (self._meta.app_label, self._meta.model_name), obj=self):
            raise exceptions.PermissionDenied()

        return self


class OperateCreateUpdateDeleteMixin(OperateCreateMixin,
                                     OperateUpdateMixin,
                                     OperateDeleteMixin):
    pass


class OperateCreateUpdateDeleteViewMixin(OperateCreateMixin,
                                         OperateUpdateMixin,
                                         OperateDeleteMixin,
                                         OperateViewMixin):
    pass


class UserQueryMixin(object):
    """ 根据用户进行筛选的方法实现mixin """
    user_query_method_name = 'query_by_user'

    @classmethod
    def query_by_user(cls, queryset=None, user=None):
        """
        前置处理
            if queryset is None:
                queryset = cls.objects.all()
            if user is None:
                queryset = queryset.none()
            ...
            return queryset
        """
        raise NotImplementedError('`query_by_user()` must be implemented!')
