# -*- coding: utf-8 -*-
{
    'name': "fms_core",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Junac",
    'website': "https://www.appnxt.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','sale_stock','purchase','mrp','hr','maintenance',
                'web_responsive','web_search_with_and','base_user_role',
                'dms','quality_control_oca'
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir.actions.server.csv',
        'views/templates.xml',
        'views/sale_order.xml',
        'views/mrp_production.xml',
        'views/product.xml',
        'views/purchase_order.xml',
        'views/mrp_routing_workcenter.xml',
        'views/operation_name.xml',
        'views/stock_move.xml',
        'views/account_move.xml',
        'views/maintenance_equipment.xml',
        'views/mrp_bom.xml',
        # 'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "license": "AGPL-3",
}
