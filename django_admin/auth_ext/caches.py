import pickle
from django_redis import get_redis_connection


class HashCache(object):
    """ Redis Hash类型缓存处理封装 """
    KEY_PROFIT = 'lms:auth'

    def __init__(self, alias='auth', write=True):
        self._client = get_redis_connection(alias, write)

    def get(self, key, field):
        cache_key = f'{self.KEY_PROFIT}:{key}'
        data = self._client.hget(cache_key, field)
        try:
            return pickle.loads(data)
        except:
            return data

    def set(self, key, field, value):
        cache_key = f'{self.KEY_PROFIT}:{key}'
        try:
            value = pickle.dumps(value)
        except:
            return
        # 注意：hash key不再设置失效时间，通常是登出时清空缓存
        self._client.hset(cache_key, field, value)

    def delete(self, key, field):
        cache_key = f'{self.KEY_PROFIT}:{key}'
        self._client.hdel(cache_key, field)

    def clear(self, key):
        """ 清空hash key """
        cache_key = f'{self.KEY_PROFIT}:{key}'
        fields = self._client.hkeys(cache_key)
        if fields:
            self._client.hdel(cache_key, *fields)


class UserCache(HashCache):
    """
    用户缓存信息选用hash类型，field可为:
        permissions -> set: 用户权限全集
        default_permissions -> set: 用户默认权限
        roles -> set: 用户角色全集
        default_roles -> set: 用户默认角色
        relationship -> dict: StarAccess用户数据
    """
    KEY_PROFIT = 'lms:auth:user'


class RoleCache(HashCache):
    """
    角色缓存信息选用hash类型，field可为:
         permissions -> set: 角色权限全集
         default_permissions -> set: 角色默认权限
    """
    KEY_PROFIT = 'lms:auth:role'
