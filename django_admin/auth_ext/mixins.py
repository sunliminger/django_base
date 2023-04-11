class CreatorMixin(object):
    def get_creator(self):
        return self.create_user


class OwnerMixin(object):
    def get_owner(self):
        return self.user


class PermMappableMixin(object):
    """
    实现权限映射的 Model 基类。
    """

    @classmethod
    def mapping_permission(cls, perm, obj=None):
        """
        根据当前的权限验证参数，获取映射后的权限验证参数。（此类方法仅为标记方法，子类应实现相应的方法）
        :param perm: 当前检测的权限。
        :param obj: 当前进行检测权限的对象。
        :return: 返回值包含两个参数：第一个参数为映射后的权限；第二个参数为对应映射后的对象，其应为映射后权限所对应的 Model 的实例。
        """
        raise NotImplementedError('`mapping_permission()` must be implemented!')
