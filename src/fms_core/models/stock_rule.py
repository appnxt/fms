# -*- coding: utf-8 -*-
##############################################################################
#
#    FMS aSuite Appnxt.com Jun.ac
#    Copyright (C) 2017~2023 上海磐麓网络科技有限公司 (<https://www.appnxt.com/>).
#
##############################################################################
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['sale_line_id','purchase_line_id','workorder_id']
        return fields

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, bom):
        mo_values = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values, bom)
        mo_values.update({
            'sale_line_id': values.get('sale_line_id',False),
            'qty_planned': values.get('quantity', 0),
        })
        return mo_values