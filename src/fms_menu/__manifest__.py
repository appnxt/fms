# -*- coding: utf-8 -*-
{
    'name': "fms_menu",

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
    'depends': ['hr','sale','purchase','mrp','maintenance',
                'web_responsive','web_search_with_and','base_user_role',
                'dms','quality_control_oca',
                'fms_core'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir.actions.server.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fms_menu/static/src/js/*.js',
            'fms_menu/static/src/css/base.scss',
        ],
    },
    "license": "AGPL-3",
    'application': True,
}
