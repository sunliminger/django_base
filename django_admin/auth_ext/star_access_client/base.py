import logging
from .access_config import ROLE_MAPPING
from .exception import AccessError
from .http import make_request
from auth_ext.caches import UserCache


logger = logging.getLogger(__name__)


def get_user_relationship(username):
    perm_cache = UserCache()
    data = None
    try:
        data = perm_cache.get(username, 'relationship')
        if not data:
            data = make_request('api/users/' + username + '/relationship')
            perm_cache.set(username, 'relationship', data)
    except AccessError as e:
        logger.error(e.message)
    return data


def get_relationship_values(relationship, key):
    """
    返回某类用户关系信息
    :param relationship: 用户关系
    :param key: 关系类型
    :return:
    """
    if not relationship:
        # StarAccess系统不存在的用户relationship为空，但仍可以满足配置为空的角色
        return set()
    result = {i.get('name') for i in relationship.get(key, []) if 'name' in i}
    return result


def check_relation(config, relationship):
    """
    验证用户关系是否满足某种角色配置，配置内所有条件都需要满足才能通过
    :param config: 角色配置
    :param relationship: 用户关系
    :return:
    """
    for key, values in config.items():
        if not isinstance(values, (set, list, tuple)):
            values = {values}
        relation_values = get_relationship_values(relationship, key)
        if not set(values).intersection(relation_values):
            return False
    return True


def check_role_config(role_code, relationship):
    """
    验证用户关系是否满足某种角色，验证角色配置，任意一种配置满足条件即通过
    :param role_code: 角色code
    :param relationship: 用户关系
    :return:
    """
    configs = ROLE_MAPPING.get(role_code, None)
    if configs is None:
        # 没配置的验证不通过
        return False
    for config in configs:
        if check_relation(config, relationship):
            return True
    return False


def get_user_relationship_roles(username):
    relation_data = get_user_relationship(username)
    role_set = set()
    # 遍历角色映射表，获取用户关系映射的lms角色
    for role_code in ROLE_MAPPING.keys():
        if check_role_config(role_code, relation_data):
            role_set.add(role_code)
    return role_set
