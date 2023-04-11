"""
    菜单配置, 用户能看到一个菜单节点，需要满足以下任意一个条件
    * 节点permissions有配置的场合:
        * 用户拥有permissions中的至少一个权限
        * 用户能够看到至少一个children节点
    * 节点permissions为空列表的场合:
        * 当前节点没有children
        * 用户能够看到至少一个children节点
"""
MENU_CONFIG = [
    {
        'path': '/login',
        'name': '',
        'component': '/views/login/index',
        'visible': {},
        'permissions': ['lms.allow_any'],
        'children': [],
    },
    {
        'path': '/404',
        'name': '404',
        'component': '/views/404',
        'visible': {},
        'permissions': ['lms.allow_any'],
        'children': [],
    },
    {
        'path': '/unfiy_login',
        'name': '',
        'component': '/views/unfiy_login/index',
        'visible': {},
        'permissions': ['lms.allow_any'],
        'children': [],
    },
    {
        'path': '/',
        'name': '首页',
        'visible': {},
        'permissions': [],
        'children': [
            {
                'path': 'dashboard',
                'name': 'dashboard',
                'component': '/views/dashboard/index',
                'visible': {
                    "view_part": ["lms.allow_any"],
                    "view_all": ["generics.view_all_import_record"],
                },
                'permissions': ['lms.allow_any'],
                'children': [],
            }
        ],
    },
    {
        'path': '/LogisticsManagement',
        'name': 'LogisticsManagement',
        'permissions': [],
        'children': [
            {
                'path': 'list',
                'name': '物流匹配规则',
                'component': '/views/logistics/logistics_rule_matching',
                'visible': {
                    'add': ['logistic_rule.add_rule'],  # 新增规则
                    'change': ['logistic_rule.change_rule'],  # 单个启用/禁用，批量启用/禁用
                    'delete': ['logistic_rule.delete_rule'],  # 单个删除规则，批量删除规则
                    'edit': ['logistic_rule.change_rule'],  # 修改规则
                    'copy': ['logistic_rule.change_rule'],  # 复制规则
                    'export': ['logistic_rule.view_rule'],  # 导出规则
                },
                'permissions': ['logistic_rule.view_rule', 'logistic_rule.delete_rule'],
                'children': [],
            },
            {
                'path': 'create_rules',
                'name': '创建规则',
                'component': '/views/logistics/create_rules',
                'visible': {},
                'permissions': ['logistic_rule.add_rule'],
                'children': [],
            },
            {
                'path': 'edit_rules',
                'name': '修改规则',
                'component': '/views/logistics/create_rules',
                'visible': {},
                'permissions': ['logistic_rule.change_rule'],
                'children': [],
            },
            {
                'path': 'logistics_tracking',
                'name': '物流跟踪',
                'component': '/views/logistics/logistics_tracking',
                'visible': {
                    'view': ['tracking_info.view_tracking_info'],  # 查看详情
                    'export': ['tracking_info.view_tracking_info'],  # 导出物流跟踪数据
                },
                'permissions': ['tracking_info.view_tracking_info'],
                'children': [],
            },
            {
                'path': 'return_management',
                'name': '退货管理',
                'component': '/views/logistics/return_management',
                'visible': {
                    'retry': ['refund_management.change_refundmanagement'],  # 重发
                    'refund': ['refund_management.change_refundmanagement'],  # 退款
                    'message': ['refund_management.change_refundmanagement'],  # 发送留言
                    'sign': ['refund_management.change_refundmanagement'],  # 标记完成
                    'delete': ['refund_management.delete_refundmanagement'],  # 删除
                    'import': ['refund_management.add_refundmanagement', 'refund_management.change_refundmanagement'],
                    # 导入数据
                    'export': ['refund_management.view_refundmanagement',
                               'refund_management.view_all_refundmanagement'],  # 导出退货数据
                },
                'permissions': ["refund_management.add_refundmanagement", "refund_management.change_refundmanagement",
                                "refund_management.delete_refundmanagement", "refund_management.view_refundmanagement",
                                'refund_management.view_all_refundmanagement'],
                'children': [],
            },
            {
                'path': 'timeliness',
                'name': '物流时效',
                'component': '/views/logistics/timeliness',
                'visible': {
                    'view': ['tracking_info.view_tracking_info', 'tracking_info.view_all_tracking_info'],  # 查看详情
                    'export': ['tracking_info.view_tracking_info', 'tracking_info.view_all_tracking_info'],  # 导出物流时效数据
                },
                'permissions': ['tracking_info.view_tracking_info', 'tracking_info.view_all_tracking_info'],
                'children': [],
            },
            {
                'path': 'recruitment',
                'name': '物流查询',
                'component': '/views/logistics/recruitment',
                'visible': {
                    'view': ['tracking_info.view_tracking_info'],  # 查看详情
                },
                'permissions': ['tracking_info.view_tracking_info'],
                'children': [],
            },
            {
                'path': 'logistics_reconciliation',
                'name': '物流对账',
                'component': '/views/logistics/logistic_reconciliation',
                'visible': {
                    'view': ['logistic_reconciliation.view_logistics_reconciliation'],  # 查看详情
                    'edit': ['logistic_reconciliation.change_logistics_reconciliation'],  # 编辑
                    'export': ['logistic_reconciliation.view_logistics_reconciliation'],  # 导出
                    'import': ['logistic_reconciliation.change_logistics_reconciliation'],  # 导入
                    'delete': ['logistic_reconciliation.delete_logistics_reconciliation'],  # 删除
                    'audit': ['logistic_reconciliation.change_logistics_reconciliation'],  # 审核
                    'create_audit_rule': ['logistic_reconciliation.change_logistics_reconciliation'],  # 跳转审核规则
                    'generate_payment': ['logistic_reconciliation.change_logistics_reconciliation'],  # 跳转请款单
                },
                'permissions': ['logistic_reconciliation.view_logistics_reconciliation'],
                'children': [],
            },
            {
                'path': 'logistic_audit_rule',
                'name': '物流审核规则管理',
                'component': '/views/logistics/logistic_audit_rule',
                'visible': {
                    'view': ['logistic_reconciliation.view_logistics_reconciliation'],  # 查看
                    'edit': ['logistic_reconciliation.change_logistics_reconciliation'],  # 编辑
                    'add': ['logistic_reconciliation.change_logistics_reconciliation'],  # 新增
                    'delete': ['logistics.delete_auditrule'],  # 删除 # 新加物流审核规则权限 之前配置暂不修改
                },
                'permissions': ['logistic_reconciliation.view_logistics_reconciliation'],
                'children': [],
            },
        ],
    },
    {
        'path': '/BasicConfigurationLogistics',
        'name': 'BasicConfigurationLogistics',
        'permissions': [],
        'children': [
            {
                'path': 'regionalized_list',
                'name': '分区管理',
                'component': '/views/base_configuration_logistics/regionalized_management',
                'visible': {
                    # 新增分区
                    'large_add': ["supplier.add_largecargopartition"],
                    'small_add': ["supplier.add_logisticsarea"],
                    # 修改分区
                    'large_edit': ["supplier.change_largecargopartition"],
                    'small_edit': ["supplier.change_logisticsarea"],
                    # 复制分区
                    'large_copy': ["supplier.change_largecargopartition"],
                    'small_copy': ["supplier.change_logisticsarea"],
                    # 删除分区、批量删除分区
                    'large_delete': ["supplier.delete_largecargopartition"],
                    'small_delete': ["supplier.delete_logisticsarea"],
                    # 导入文件
                    'large_import': ["supplier.add_largecargopartition"],
                    'small_import': ["supplier.add_logisticsarea"],
                    # 下载分区模板
                    'large_download': ["supplier.add_largecargopartition"],
                    'small_download': ["supplier.add_logisticsarea"],
                },
                'permissions': [
                    "supplier.add_largecargopartition", "supplier.change_largecargopartition",
                    "supplier.delete_largecargopartition", "supplier.view_largecargopartition",
                    "supplier.add_logisticsarea", "supplier.change_logisticsarea",
                    "supplier.delete_logisticsarea", "supplier.view_logisticsarea",
                ],
                'children': [],

            },
            {
                'path': 'billing_logic_configuration',
                'name': '计费逻辑配置',
                'component': '/views/base_configuration_logistics/billing_logic_configuration',
                'visible': {
                    'add': ["logistic_config.add_chargematch"],  # 新增计费逻辑
                    'edit': ["logistic_config.change_chargematch"],  # 修改计费逻辑
                    'copy': ["logistic_config.change_chargematch"],  # 复制计费逻辑
                    'change': ["logistic_config.change_chargematch", ],  # 计费逻辑启用禁用
                    'import': ["logistic_config.add_chargematch", "logistic_config.change_chargematch"],  # 导入文件
                    'download': ["logistic_config.add_chargematch", "logistic_config.change_chargematch"]  # 下载计费逻辑模板
                },
                'permissions': [
                    "logistic_config.add_chargematch", "logistic_config.change_chargematch",
                    "logistic_config.view_chargematch",
                ],
                'children': [],

            },
            {
                'path': 'logistics_limited',
                'name': '物流限制配置',
                'component': '/views/base_configuration_logistics/logistics_limited',
                'visible': {
                    'add': ["logistic_limit_sku.add_logisticlimitsku"],  # 新增物流限制规则
                    'edit': ["logistic_limit_sku.change_logisticlimitsku"],  # 修改物流限制规则
                    'delete': ["logistic_limit_sku.delete_logisticlimitsku"],  # 单个删除物流限制规则，批量删除物流限制规则
                    'import': ["logistic_limit_sku.add_logisticlimitsku", "logistic_limit_sku.change_logisticlimitsku"],
                    # 导入文件
                    'download': ["logistic_limit_sku.add_logisticlimitsku",
                                 "logistic_limit_sku.change_logisticlimitsku"],  # 下载物流限制规则模板
                    'export': ["logistic_limit_sku.view_logisticlimitsku"],  # 物流限制规则数据导出 
                },
                'permissions': [
                    "logistic_limit_sku.add_logisticlimitsku", "logistic_limit_sku.change_logisticlimitsku",
                    "logistic_limit_sku.delete_logisticlimitsku", "logistic_limit_sku.view_logisticlimitsku",
                ],
                'children': [],
            },
            {
                'path': 'shipping_address',
                'name': '发件地址管理',
                'component': '/views/base_configuration_logistics/shipping_address',
                'visible': {
                    'add': ['logistic_config.add_shipping_address'],
                    'edit': ['logistic_config.change_shipping_address'],
                    'delete': ['logistic_config.delete_shipping_address'],
                    'copy': ['logistic_config.add_shipping_address'],
                },
                'permissions': ['logistic_config.view_shipping_address', 'logistic_config.add_shipping_address',
                                'logistic_config.change_shipping_address',
                                'logistic_config.delete_shipping_address'],
                'children': [],
            },
            {
                'path': 'logistics_authority_configuration',
                'name': '物流权限配置',
                'component': '/views/base_configuration_logistics/logistics_authority_configuration',
                'visible': {
                    'add': ['auth_ext.add_role'],  # 新增自定义角色
                    'delete': ['auth_ext.delete_role'],  # 删除自定义角色
                    'user_role_deploy': ['auth_ext.change_user'],  # 用户角色配置
                    'user_auth': ['auth_ext.change_user'],  # 用户权限配置
                    'role_auth': ['auth_ext.change_role']  # 角色权限配置
                },
                'permissions': [
                    'auth_ext.add_role', 'auth_ext.change_role', 'auth_ext.delete_role',
                    'auth_ext.change_user',
                ],
                'children': [],
            },
            {
                'path': 'whiteList',
                'name': '物流限制白名单',
                'visible': {
                    'add': ['lms.backdoor'],
                    'delete': ['lms.backdoor'],
                },
                'component': '/views/base_configuration_logistics/whiteList',
                'permissions': ['lms.backdoor'],
                'children': [],
            },
            {
                'path': 'aliexpress_address',
                'name': '速卖通后台地址管理',
                'component': '/views/base_configuration_logistics/aliexpress_address',
                'visible': {
                    'update': ['logistic_config.change_storetoken'],  # 更新地址

                },
                'permissions': [
                    'logistic_config.view_storetoken', 'logistic_config.change_storetoken',
                ],
                'children': [],
            },
            {
                'path': 'edis',
                'name': 'EDIS物流授权管理',
                'component': '/views/base_configuration_logistics/edis',
                'visible': {
                    'add': ['logistic_config.add_storetoken'],  # 添加edis授权店铺或开发者账号

                },
                'permissions': [
                    'logistic_config.view_storetoken', 'logistic_config.add_storetoken',
                ],
                'children': [],
            },
            {
                'path': 'declared_product_management',
                'name': '申报产品管理',
                'component': '/views/base_configuration_logistics/declared_product_management',
                'visible': {
                    'add': ['sku_declarate.add_skudesc'],  # 添加产品申报信息
                    'edit': ['sku_declarate.edit_skudesc'],  # 编辑修改产品申报信息
                    'copy': ['sku_declarate.copy_skudesc'],  # 复制产品申报信息
                    'delete': ['sku_declarate.delete_skudesc'],  # 删除产品申报信息
                    'import': ['sku_declarate.import_skudesc'],  # 导入产品申报信息

                },
                'permissions': [
                    'sku_declarate.view_skudesc', 'sku_declarate.add_skudesc', 'sku_declarate.add_skudesc',
                    'sku_declarate.edit_skudesc', 'sku_declarate.copy_skudesc', 'sku_declarate.delete_skudesc',
                    'sku_declarate.import_skudesc',
                ],
                'children': [],
            },
            {
                'path': 'head_configuration',
                'name': '头程系数配置',
                'component': '/views/base_configuration_logistics/head_configuration',
                'visible': {
                    'view': ['logistic_headway.view_logisticsheadway'],  # 查看头程系数
                    'add': ['logistic_headway.add_logisticsheadway'],  # 添加头程系数
                    'edit': ['logistic_headway.change_logisticsheadway'],  # 修改头程系数
                    'delete': ['logistic_headway.delete_logisticsheadway'],  # 删除头程系数
                },
                'permissions': [
                    'logistic_headway.view_logisticsheadway',
                    'logistic_headway.add_logisticsheadway',
                    'logistic_headway.change_logisticsheadway',
                    'logistic_headway.delete_logisticsheadway'
                ],
                'children': [],
            },
        ],
    },
    {
        'path': '/LogisticsBusinessManagement',
        'name': 'LogisticsBusinessManagement',
        'permissions': [],
        'children': [
            {
                'path': 'document_management',
                'name': '资料管理',
                'component': '/views/Logistics_business_management/document_management',
                'visible': {
                    'add': ["supplier.add_logisticsupplier"],  # 新增物流商资料
                    'edit': ["supplier.change_logisticsupplier"],  # 修改物流商资料
                    'view': ["supplier.view_logisticsupplier"],  # 查看物流商资料
                    'delete': ["supplier.delete_logisticsupplier"],  # 删除物流商资料
                },
                'permissions': [
                    "supplier.add_logisticsupplier", "supplier.change_logisticsupplier",
                    "supplier.delete_logisticsupplier", "supplier.view_logisticsupplier",
                ],
                'children': [],
            },

            {
                'path': 'logistics-appraise',
                'name': '物流商评分',
                'component': '/views/Logistics_business_management/logistics-appraise',
                'visible': {
                    'add': ["supplier.add_logisticsupplierscore"],  # 新增物流商评分
                    'edit': ["supplier.change_logisticsupplierscore"],  # 修改物流商评分
                    'view': ["supplier.view_logisticsupplierscore"],  # 查看物流商评分
                    'delete': ["supplier.delete_logisticsupplierscore"],  # 删除物流商评分
                },
                'permissions': [
                    "supplier.add_logisticsupplierscore", "supplier.change_logisticsupplierscore",
                    "supplier.view_logisticsupplierscore", "supplier.delete_logisticsupplierscore",
                ],
                'children': [],
            },

            {
                'path': 'logistics-list',
                'name': '物流商列表',
                'component': '/views/Logistics_business_management/logistics-list',
                'visible': {
                    'add': ["supplier.add_logisticsuppliernew"],
                    'edit': ["supplier.change_logisticsuppliernew"],
                    'view': ["supplier.view_logisticsuppliernew"],
                    'delete': ["supplier.delete_logisticsuppliernew"],
                    'export': [],
                    'change': ["supplier.change_logisticsuppliernew"],

                },
                'permissions': [
                    "supplier.add_logisticsuppliernew", "supplier.change_logisticsuppliernew",
                    "supplier.view_logisticsuppliernew", "supplier.delete_logisticsuppliernew",
                ],
                'children': [],
            },
            {
                'path': 'logistics-details',
                'name': '物流商详情页',
                'component': '/views/Logistics_business_management/logistics-details',
                'visible': {},
                'permissions': [],
                'children': [],
            },
            {
                'path': 'logistics-edit',
                'name': '物流商增加/编辑页',
                'component': '/views/Logistics_business_management/logistics-edit',
                'visible': {},
                'permissions': [],
                'children': [],
            },
            {
                'path': 'logistics-audit',
                'name': '物流商审批',
                'component': '/views/Logistics_business_management/logistics-audit',
                'visible': {
                    'add': ["supplier.add_logisticsauditconfig"],
                    'edit': ["supplier.change_logisticsauditconfig"],
                    'view': ["supplier.view_logisticsauditconfig"],
                    'delete': ["supplier.delete_logisticsauditconfig"],

                },
                'permissions': [
                    "supplier.add_logisticsauditconfig", "supplier.change_logisticsauditconfig",
                    "supplier.view_logisticsauditconfig", "supplier.delete_logisticsauditconfig",
                ],
                'children': [],
            },
            {
                'path': 'bulk_product_management',
                'name': '大货产品管理',
                'component': '/views/Logistics_business_management/bulk_product_management',
                'visible': {
                    'add': ["supplier.add_logisticsproducts"],  # 新增大货产品
                    'edit': ["supplier.change_logisticsproducts"],  # 修改大货产品
                    'view': ["supplier.view_logisticsproducts"],  # 查看大货产品
                    'change': ["supplier.change_logisticsproducts", "supplier.delete_logisticsproducts"],  # 启用/禁用大货产品
                    'export': ["supplier.view_logisticsproducts"],  # 导出大货产品数据
                    'delete': ["supplier.delete_logisticsproducts"],  # 大货产品删除
                },
                'permissions': [
                    "supplier.add_logisticsproducts", "supplier.change_logisticsproducts",
                    "supplier.delete_logisticsproducts", "supplier.view_logisticsproducts"
                ],
                'children': [],
            },
            {
                'path': 'logistics_products',
                'name': '物流产品',
                'component': '/views/Logistics_business_management/logistics_products',
                'visible': {},
                'permissions': ["supplier.add_logisticsproducts", "supplier.change_logisticsproducts"],
                'children': [],
            },
            {
                'path': 'bulk_product_quotation',
                'name': '大货产品报价',
                'component': '/views/Logistics_business_management/bulk_product_quotation',
                'visible': {
                    'add': ["supplier.add_logisticslargegoodquotation"],  # 新增大货产品报价
                    'edit': ["supplier.change_logisticslargegoodquotation"],  # 修改大货产品报价
                    'view': ["supplier.view_logisticslargegoodquotation"],  # 查看大货产品报价
                    'change': ["supplier.change_logisticslargegoodquotation",
                               "supplier.delete_logisticslargegoodquotation"],  # 启用/禁用大货产品报价
                    'export': ["supplier.view_logisticslargegoodquotation"],  # 导出大货产品报价数据
                    'delete': ["supplier.delete_logisticslargegoodquotation"]  # 删除大货产品报价
                },
                'permissions': [
                    "supplier.add_logisticslargegoodquotation", "supplier.change_logisticslargegoodquotation",
                    "supplier.delete_logisticslargegoodquotation", "supplier.view_logisticslargegoodquotation",
                ],
                'children': [],
            },
            {
                'path': 'logistics_quotation',
                'name': '产品报价',
                'component': '/views/Logistics_business_management/logistics_quotation',
                'visible': {},
                'permissions': [
                    "supplier.add_logisticslargegoodquotation", "supplier.change_logisticslargegoodquotation",
                ],
                'children': [],
            },
            {
                'path': 'small_packages_pricing_rules',
                'name': '小包计价规则',
                'component': '/views/base_configuration_logistics/small_packages_pricing_rules',
                'visible': {
                    'add': ["supplier.add_pricingrule"],  # 新增计价规则
                    'edit': ["supplier.change_pricingrule"],  # 修改计价规则
                    'delete': ["supplier.delete_pricingrule"],  # 删除计价规则
                    'view': ["supplier.view_pricingrule"],  # 查看计价规则
                    'change': ["supplier.change_pricingrule"],  # 计价规则启用禁用
                    'import': ["supplier.add_pricingrule", "supplier.change_pricingrule"],  # 导入文件
                    'download': ["supplier.add_pricingrule", "supplier.change_pricingrule"],  # 下载计价规则模板
                    'batch_enable': ["supplier.change_pricingrule"],  # 批量启用
                    'batch_unenable': ["supplier.change_pricingrule"],  # 批量停用
                    'batch_delete': ["supplier.delete_pricingrule"],  # 批量删除
                    'batch_update': ["supplier.change_pricingrule"],  # 批量修改价格
                },
                'permissions': [
                    "supplier.add_pricingrule", "supplier.change_pricingrule",
                    "supplier.delete_pricingrule", "supplier.view_pricingrule"
                ],
                'children': [],
            },
            {
                'path': 'small_packages_quotation',
                'name': '物流报价',
                'component': '/views/base_configuration_logistics/small_packages_quotation',
                'visible': {},
                'permissions': ["supplier.add_pricingrule", "supplier.change_pricingrule", "supplier.view_pricingrule"],
                'children': [],
            },
            {
                'path': 'transport_configuration',
                'name': '物流方式配置',
                'component': '/views/base_configuration_logistics/transport_configuration',
                'visible': {
                    'add': ["supplier.add_logisticservice"],  # 新增物流方式,批量新增支持平台
                    'edit': ["supplier.change_logisticservice"],  # 修改物流方式
                    'view': ["supplier.view_logisticservice"],  # 查看物流方式
                    'delete': ["supplier.delete_logisticservice"],  # 删除物流方式
                    'change': ["supplier.change_logisticservice", "supplier.delete_logisticservice"],  # 物流方式启用禁用
                },
                'permissions': [
                    "supplier.add_logisticservice", "supplier.change_logisticservice",
                    "supplier.delete_logisticservice", "supplier.view_logisticservice",
                ],
                'children': [],
            },
            {
                'path': 'logistics_token_management',
                'name': '物流商Token管理',
                'component': '/views/Logistics_business_management/logistics_token_management',
                'visible': {
                    'edit': ['shipment.change_shipment_api_token'],
                    'change': ['shipment.change_shipment_api_token'],

                },
                'permissions': [
                    'shipment.view_shipment_api_token', 'shipment.add_shipment_api_token',
                ],
                'children': [],
            },
        ]
    },
    {
        'path': '/OrderManage',
        'name': '订单管理',
        'permissions': [],
        'children': [
            {
                'path': 'order_management',
                'name': '订单列表',
                'component': '/views/logistics/order_management',
                'visible': {
                    'generate_waybill': ["shipment.change_shipment"],  # 生成运单，重新生成运单
                    'edit': ["shipment.change_shipment"],
                    # 单个修改订单信息，批量修改订单信息，单个修改申报信息
                    'view': ["shipment.view_shipment"],  # 查看详情信息
                    'abnormal_delivery': ["shipment.change_shipment"],  # 发货异常
                    'print': ["shipment.view_shipment"],  # 打印标签
                    'download': ["shipment.view_shipment"],  # 下载模板
                    'import': ["shipment.change_shipment"],  # 导入跟踪单号
                    'export': ["shipment.view_shipment"],  # 导出订单信息
                },
                'permissions': [
                    "shipment.add_shipment", "shipment.change_shipment",
                    "shipment.delete_shipment", "shipment.view_shipment",
                ],
                'children': [],
            },
            {
                'path': 'order_detail',
                'name': '订单详情',
                'component': '/views/logistics/order_detail',
                'visible': {},
                'permissions': ["shipment.view_shipment"],
                'children': [],
            },
            {
                'path': 'Logistics_delivery_report',
                'name': '物流发货报表',
                'component': '/report_management/Logistics_delivery_report',
                'visible': {
                    'change': ['shipment.change_report'],  # 设置查询类型按钮
                    'export': ['shipment.export_report'],  # 导出
                    'view': ['shipment.view_report'],  # 查询
                },
                'permissions': [
                    'shipment.change_report',
                    'shipment.export_report',
                    'shipment.view_report'
                ],
                'children': [],
            },
            {
                'path': 'delivery_intercept',
                'name': '发货拦截',
                'component': '/views/logistics/delivery_intercept',
                'visible': {
                    "add": ["shipment.add_intercept"],
                    "edit": ["shipment.change_intercept"],
                    "change": ["shipment.change_intercept"],
                    "view": ["shipment.view_intercept"],
                    "delete": ["shipment.delete_intercept"],
                },
                'permissions': [
                    "shipment.add_intercept",
                    "shipment.change_intercept",
                    "shipment.view_intercept",
                    "shipment.delete_intercept",
                ],
                'children': [],
            },
            {
                'path': 'special_configuration',
                'name': '物流下单特殊配置',
                'component': '/views/logistics/special_configuration',
                'visible': {
                    "add": ["shipment.add_logisticssignature"],
                    "change": ["shipment.change_logisticssignature"],
                    "view": ["shipment.view_logisticssignature"],
                    "delete": ["shipment.delete_logisticssignature"],
                },
                'permissions': [
                    "shipment.add_logisticssignature",
                    "shipment.change_logisticssignature",
                    "shipment.delete_logisticssignature",
                    "shipment.view_logisticssignature",
                ],
                'children': [],
            },

        ]
    },
    {
        'path': '/HeaderManage',
        'name': '头程管理',
        'permissions': [],
        'children': [
            {
                'path': 'header_bill_management',
                'name': '头程单据管理',
                'component': '/views/header_manage/header_bill_management',
                'visible': {
                    'merge': ["large_first_leg.change_requisition"],  # 合单
                    'separate': ["large_first_leg.change_requisition"],  # 拆单
                    'import': ["large_first_leg.change_requisition"],  # 导入
                    'download': ["large_first_leg.view_requisition"],  # 下载模板
                    'view': ["large_first_leg.view_requisition"]  # 装箱明细
                },
                'permissions': [
                    "large_first_leg.change_requisition",
                    "large_first_leg.view_requisition",
                ],
                'children': [],
            },
            {
                'path': 'header_waybill_management',
                'name': '头程运单管理',
                'component': '/views/header_manage/header_waybill_management',
                'visible': {
                    'billing_again': ["large_first_leg.change_waybill"],  # 重新计费
                    'edit': ["large_first_leg.change_waybill"],  # 修改头程运单
                    'add': ["large_first_leg.change_waybill"],  # 添加附加费
                    'view': ["large_first_leg.view_waybill"],  # 查看附加费详情
                    'export': ["large_first_leg.view_waybill"],  # 导出头程单据数据
                },
                'permissions': [
                    "large_first_leg.change_waybill",
                    "large_first_leg.view_waybill"
                ],
                'children': [],
            },
            {
                'path': 'bulk_timeliness',
                'name': '大货时效',
                'visible': {
                    'change': [],
                    'export': [],
                },
                'component': '/views/header_manage/bulk_timeliness',
                'permissions': [
                    "large_first_leg.view_timeliness",
                ]
            },
            {
                'path': 'bulk_reconciliation',
                'name': '大货对账管理',
                'component': '/views/header_manage/bulk_reconciliation',
                'visible': {
                    'audit': ["large_first_leg.audit_reconciliation"],  # 审核账单数据
                    'view': ["large_first_leg.view_reconciliation"],  # 大货装箱明细，大货分摊明细
                    'edit': ["large_first_leg.edit_reconciliation"],  # 编辑大货对账数据
                    'delete': ["large_first_leg.delete_reconciliation"],  # 删除大货账单数据
                    'add': ["finance.apply_payment"],  # 设置审核规则，生成请款单
                    'download': ["large_first_leg.view_reconciliation"],  # 下载大货账单模板文件
                    'import': ["large_first_leg.change_reconciliation"],  # 账单导入
                    'export': ["large_first_leg.view_reconciliation"]  # 导出账单数据
                },
                'permissions': [
                    "large_first_leg.change_reconciliation", "large_first_leg.audit_reconciliation",
                    "large_first_leg.delete_reconciliation", "large_first_leg.view_reconciliation",
                    "large_first_leg.edit_reconciliation"
                ],
                'children': [],
            },
            {
                'path': 'ManualManage',
                'name': '手工应付管理',
                'component': '/views/header_manage/manual_manage/index',
                'visible': {
                    'add': ["large_first_leg.change_waybill"],  # 新增附加费
                    'edit': ["large_first_leg.change_waybill"],  # 修改附加费
                    'change': ["large_first_leg.change_waybill"],  # 手工应付启用禁用
                    'export': ["large_first_leg.change_waybill"],  # 导出手工应付数据
                },
                'permissions': [
                    "large_first_leg.change_waybill", "large_first_leg.view_waybill"
                ],
                'children': [],
            },
            {
                'path': 'audit_rule_management',
                'name': '大货审核规则管理',
                'component': '/views/header_manage/audit_rule_management',
                'visible': {
                    'add': ["large_first_leg.add_audit_rule"],  # 新增审核规则
                    'edit': ["large_first_leg.change_audit_rule"],  # 编辑审核规则
                    'change': ["large_first_leg.change_audit_rule"],  # 审核规则启用禁用
                    # 'delete': ["large_first_leg.delete_auditrule"]  # 删除审核规则
                },
                'permissions': [
                    "large_first_leg.add_audit_rule", "large_first_leg.change_audit_rule",
                    "large_first_leg.view_audit_rule"
                ],
                'children': [],
            },
            {
                'path': 'shipping_method_management',
                'name': '大货运输方式',
                'component': '/views/header_manage/shipping_method_management',
                'visible':{
                    'view': ['large_first_leg.view_firstlegshippingmethod'], # 查看运输方式
                    'add': ['large_first_leg.add_firstlegshippingmethod'],  # 新增运输方式
                    'change': ['large_first_leg.change_firstlegshippingmethod'],  # 编辑运输方式
                    'delete': ['large_first_leg.delete_firstlegshippingmethod']  # 删除运输方式
                },
                'permissions': [
                    'large_first_leg.view_firstlegshippingmethod','large_first_leg.add_firstlegshippingmethod',
                    'large_first_leg.change_firstlegshippingmethod','large_first_leg.delete_firstlegshippingmethod'
                ],
                'children': [],
            }
        ]
    },
    {
        'path': '/PaymentManage',
        'name': '请款单管理',
        'permissions': [],
        'children': [
            {
                'path': 'payment_request_list',
                'name': '请款单列表',
                'component': '/views/payment_request_management/payment_request_list',
                'visible': {
                    'add': ['finance.apply_payment'],  # 新增请款申请
                    'edit': ['finance.apply_payment'],  # 修改请款
                    'view': [],  # 请款审批进度,查看请款详情
                    'delete': ['finance.delete_payment_application'],  # 删除请款申请
                    'revoke': ['finance.revoke_payment_application'],  # 撤销请款申请
                    'audit': ['finance.audit_payment_application'],  # 提交请款审批,重新提交请款审批,审批请款单
                },
                'permissions': [
                    'finance.apply_payment', 'finance.view_payment_application',
                    'finance.audit_payment_application', 'finance.revoke_payment_application',
                    'finance.delete_payment_application'
                ],
                'children': [],
            },
            {
                'path': 'payment_detail',
                'name': '请款单详情',
                'component': '/views/payment_request_management/payment_detail',
                'visible': {},
                'permissions': [
                    'finance.apply_payment', 'finance.view_payment_application',
                    'finance.audit_payment_application', 'finance.revoke_payment_application',
                    'finance.delete_payment_application'
                ],
                'children': [],
            },

            {
                'path': 'Logistics_bulk_report',
                'name': '账单报表',
                'component': '/views/report_management/Logistics_bulk_report',
                'visible': {
                    'view': ['finance.view_payment_application'],  # 请款审批进度,查看请款详情
                },
                'permissions': [
                    'finance.view_payment_application',
                ],
                'children': [],
            },

        ]
    },

]
