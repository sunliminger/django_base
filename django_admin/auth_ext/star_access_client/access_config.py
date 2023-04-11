"""
    星商员工关系与物流系统角色的映射， 格式为 {role_code: configs}
    configs之间为或关系，config内各关系类型间为与关系
    config内同一个key值的列表内关系为或关系
    eg.
    "service:member": [
        {
            "roles": ["客服"],
            "levels": ["专员", "助理"],
        },
        {
            "positions": ["客服专员"]
        },
    ],
    表示service:member(销售专员)这个角色有两种config，用户关系数据满足任意一种即拥有“销售专员”角色。
    以下情况中用户关系会判定为True:
    1. 用户拥有roles 客服 且 levels 专员
    2. 用户拥有positions 客服专员

"""
from utils.collections_ext import ReadOnlyDict

_ROLE_MAPPING = {
    "system:user": [
        {},     # 所有人都是
    ],
    "logistic:user": [
        {
            "departments": ['物流部'],
        }
    ],
    "system:director": [
        {
            "levels": ["副总监", "总监", "总经理"],
        },
    ],
    "seller:member": [
        {
            "roles": ["运营"],
            "levels": ["专员", "助理"],
        },
    ],
    "seller:leader": [
        {
            "roles": ["运营"],
            "levels": ["组长"],
        },
    ],
    "seller:head": [
        {
            "roles": ["运营"],
            "levels": ["副主管", "主管"],
        },
    ],
    "seller:manager": [
        {
            "roles": ["运营"],
            "levels": ["副经理", "经理"],
        },
    ],
    "service:member": [
        {
            "roles": ["客服"],
            "levels": ["专员", "助理"],
        },
        {
            "positions": ["客服专员"]
        },
    ],
    "service:leader": [
        {
            "roles": ["客服"],
            "levels": ["组长"],
        },
        {
            "positions": ["客服组长"]
        },
    ],
    "service:head": [
        {
            "roles": ["客服"],
            "levels": ["副主管", "主管"],
        },
        {
            "positions": ["客服副主管", "客服主管"]
        },
    ],
    "service:manager": [
        {
            "roles": ["客服"],
            "levels": ["副经理", "经理"],
        },
    ],
    "warehouse:member": [
        {
            "departments": ["仓储部"],
            "levels": ["专员", "助理"],
        },
    ],
    "warehouse:leader": [
        {
            "departments": ["仓储部"],
            "levels": ["组长"],
        },
    ],
    "warehouse:head": [
        {
            "departments": ["仓储部"],
            "levels": ["副主管", "主管"],
        },
    ],
    "warehouse:manager": [
        {
            "departments": ["仓储部", "供应链管理中心"],
            "levels": ["副经理", "经理"],
        },
    ],
    "logistic:member": [
        {
            "roles": ["物流"],
            # "levels": ["专员", "助理"],
        },
        {
            "departments": ["物流一部", "物流二部"],
        },
    ],

    # 目前物流权限只设置物流专员
    # "logistic:leader": [
    #     {
    #         "departments": ["物流一部", "物流二部"],
    #         "levels": ["组长"],
    #     },
    # ],
    # "logistic:head": [
    #     {
    #         "departments": ["物流一部", "物流二部"],
    #         "levels": ["副主管", "主管"],
    #     },
    # ],
    # "logistic:manager": [
    #     {
    #         "departments": ["物流一部", "物流二部", "供应链管理中心"],
    #         "levels": ["副经理", "经理"],
    #     },
    # ],
    "finance:member": [
        {
            "departments": ["财务部"],
            "levels": ["专员", "助理"],
        },
    ],
    "finance:leader": [
        {
            "departments": ["财务部"],
            "levels": ["组长"],
        },
    ],
    "finance:head": [
        {
            "departments": ["财务部"],
            "levels": ["副主管", "主管"],
        },
    ],
    "finance:manager": [
        {
            "departments": ["财务部"],
            "levels": ["副经理", "经理"],
        },
    ],
    "develop:user": [
        {
            "departments": ["研发与流程管理部"],
        },
    ],
}


ROLE_MAPPING = ReadOnlyDict(_ROLE_MAPPING)      # 对外只读
