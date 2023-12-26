# -*- coding: utf-8 -*-
##############################################################################
#
#    FMS aSuite Appnxt.com Jun.ac
#    Copyright (C) 2017~2023 上海磐麓网络科技有限公司 (<https://www.appnxt.com/>).
#
##############################################################################
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Command


class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    # todo: outsource_type -> move.is_subcontract

    outsource_type = fields.Selection([
        ('outsourcing','Normal'),
        ('subcontract','Subcontract'),
        ('process_outsourcing','Process Outsourcing'),
    ],string='模式',default='outsourcing')
    sale_outsource_id = fields.Many2one('sale.order.outsource',string='OS行')
    subcontract_bom_id = fields.Many2one('mrp.bom',string='BOM')
    workorder_id = fields.Many2one('mrp.workorder',string='WOR')

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line_from_procurement(product_id, product_qty, product_uom, company_id, values, po)
        res['outsource_type'] = values.get('outsource_type')
        res['sale_outsource_id'] = values.get('sale_outsource_id')
        res['subcontract_bom_id'] = values.get('subcontract_bom_id')
        return res
    
    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        if self.workorder_id:
            res['location_id'] = self.company_id.subcontracting_location_id.id
            res['workorder_id'] = self.workorder_id and self.workorder_id.id or False
            res['description_picking'] = res['description_picking'] = ':'.join([self.workorder_id.production_id.product_id.display_name,self.product_id.display_name])
        return res
    
    def _create_stock_moves(self, picking):
        res = super()._create_stock_moves(picking)
        if self.workorder_id: # 触发工序委外补货
            res._adjust_procure_method()
        return res

    
