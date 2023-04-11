from dataclasses import dataclass, field
from typing import List, Dict
from .config import MENU_CONFIG


@dataclass
class MenuItem:
    path: str = ''
    name: str = ''
    component: str = ''
    visible: Dict[str, List[str]] or List[str] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    children: List = field(default_factory=list)

    def __post_init__(self):
        if self.children:
            self.children = [self.__class__(**d) for d in self.children]


def _validate_visible(user, visible_dict):
    result = []
    for k, permissions in visible_dict.items():
        has_perm = any(map(lambda p: user.has_perm(p), permissions)) if permissions else True
        if has_perm:
            result.append(k)
    return result


def _get_menu_for_user(user, menu_tree):
    result = []

    for menu_item in menu_tree:
        # 1. 验证子孙节点权限
        has_children = bool(menu_item.children)     # 是否有配置子孙节点
        if has_children:
            menu_item.children = get_menu_for_user(user, menu_item.children)

        # 2. 判断当前节点是否有权限: 用户拥有节点的任意一种权限，则用户拥有当前节点的权限，节点没配置权限时视为有权限
        permissions = menu_item.permissions
        has_perm = any(map(lambda p: user.has_perm(p), permissions)) if permissions else True

        # 验证按钮是否可见
        menu_item.visible = _validate_visible(user, menu_item.visible)

        # 3. 确认当前节点是否可见
        if menu_item.permissions:
            if has_perm or bool(menu_item.children):
                result.append(menu_item)
        else:
            if not has_children or bool(menu_item.children):
                result.append(menu_item)

    return result


def get_menu_for_user(user, menu_tree=None):
    if menu_tree is None:
        menu_tree = [MenuItem(**d) for d in MENU_CONFIG]
    return _get_menu_for_user(user, menu_tree)
