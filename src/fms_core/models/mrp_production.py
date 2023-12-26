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
from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo.fields import Command

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    _order = 'id desc'

    sale_line_id = fields.Many2one('sale.order.line','SO行')
    qty_planned = fields.Float(string='Planned quality',readonly=True)
    qty_scrap = fields.Float(string='Unqualified quantity')

    def action_confirm(self):
        for r in self:
            r.create_outsourcing_orders()
        return super().action_confirm()
    
    def create_outsourcing_orders(self):
        for wo in self.workorder_ids:
            if wo.operation_id.outsourcing_product_id:
                self._create_process_outsourcing_po(wo)
        
    def _create_process_outsourcing_po(self,wo):
        vals = {
            'partner_id': wo.operation_id.outsourcing_partner_id.id,
            'origin': ','.join([wo.production_id.name,wo.production_id.sale_line_id.order_id.name]) if wo.production_id.sale_line_id else wo.production_id.name,
            'order_line': [Command.create({
                'product_id': wo.operation_id.outsourcing_product_id.id,
                'product_uom': wo.operation_id.outsourcing_product_id.uom_po_id.id,
                'product_uom_qty': wo.qty_remaining,
                'workorder_id': wo.id,
                'outsource_type': 'process_outsourcing',
            })]
        }
        return self.env['purchase.order'].sudo().create(vals)
    
    def button_mark_done(self):
        """不合格数量自动创建报废单"""
        res = super().button_mark_done()
        for r in self:
            if float_compare(r.qty_scrap,0,precision_rounding=0.001) == 1:
                scrap = self.env['stock.scrap'].create({
                    'product_id': r.product_id.id,
                    'product_uom_id': r.product_uom_id.id,
                    'production_id': r.id,
                    'location_id': r.location_dest_id.id,
                    'scrap_qty': r.qty_scrap
                })  
                scrap.do_scrap()              
        return res
