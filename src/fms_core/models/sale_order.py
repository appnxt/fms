# -*- coding: utf-8 -*-
##############################################################################
#
#    FMS aSuite Appnxt.com Jun.ac
#    Copyright (C) 2017~2023 上海磐麓网络科技有限公司 (<https://www.appnxt.com/>).
#
##############################################################################
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError,UserError
from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo.tools.misc import clean_context
from odoo.fields import Command
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    outsource_ids = fields.One2many('sale.order.outsource','order_id',string='Outsourcing Lines')
    is_outsourcing = fields.Boolean(string='Is outsourcing')
    fms_mrp_production_count = fields.Integer(compute='_compute_docs_count')
    fms_purchase_order_count = fields.Integer(compute='_compute_docs_count')

    def _compute_docs_count(self):
        for order in self:
            order.fms_mrp_production_count = len(self.env['mrp.production'].sudo().search([('sale_line_id','in',order.order_line.ids)]))
            order.fms_purchase_order_count = len(self.env['purchase.order.line'].sudo().search([('sale_outsource_id','in',self.outsource_ids.ids)]).mapped('order_id'))

    def action_view_purchase_orders_fms(self):
        self.ensure_one()
        purchase_order_ids = self.env['purchase.order.line'].sudo().search([('sale_outsource_id','in',self.outsource_ids.ids)]).mapped('order_id').ids
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
        if len(purchase_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': purchase_order_ids[0],
            })
        else:
            action.update({
                'name': _("Purchase Order generated from %s", self.name),
                'domain': [('id', 'in', purchase_order_ids)],
                'view_mode': 'tree,form',
            })
        return action

    def action_mrp_production_orders(self):
        self.ensure_one()
        order_ids = self.env['mrp.production'].sudo().search([('sale_line_id','in',self.order_line.mapped('id'))]).ids
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': order_ids[0],
            })
        else:
            action.update({
                'name': _("Production Order generated from %s", self.name),
                'domain': [('id', 'in', order_ids)],
                'view_mode': 'tree,form',
            })
        return action


    def action_production_replenish(self):
        '''product.replenish'''
        route_ids = [self.env.ref('mrp.route_warehouse0_manufacture').id]
        for r in self:
            for line in r.order_line: 
                if float_compare(line.qty_production, 0.0, precision_rounding=0.001) == 0:
                    continue
                if not line.material_id or not line.bom_id:
                    raise ValidationError('Need BOM and material fields')
                if len(line.bom_id.bom_line_ids) != 1:
                    raise ValidationError('BOM line should be single')
                if line.material_id != line.bom_id.bom_line_ids[0].product_id:
                    raise ValidationError('The raw materials and the components in the Bill of Materials are not consistent.')
                replenish_wizard = self.env['product.replenish'].create({
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_template_id.id,
                    'product_uom_id': line.product_uom.id,
                    'quantity': line.qty_production,
                    'warehouse_id': r.warehouse_id.id,
                    'route_ids': [(6,0,route_ids)]
                })
                extra_val = line._get_production_extra_vals()
                replenish_wizard.with_context(extra_val=extra_val).launch_replenishment2(line.order_id.name,line.order_id.name)
        return True

    def action_purchase_replenish(self):
        for r in self: 
            route_ids = [self.env.ref('purchase_stock.route_warehouse0_buy').id]
            for line in r.outsource_ids:
                if float_compare(line.product_uom_qty, 0.0, precision_rounding=0.001) == 0:
                    raise ValidationError('Outsource line quantity is 0.0')
                line._set_subcontract_bom_id()
                if line.outsource_type == 'subcontract':
                    route_resupply = self.env.ref('mrp_subcontracting.route_resupply_subcontractor_mto')
                    route_ids = [route_resupply.id] 
                    # 原料补货路线设置检查 todo write未保存
                    if route_resupply not in line.sale_line_id.material_id.route_ids:
                        line.sale_line_id.material_id.product_tmpl_id.write({
                            'route_ids':[Command.link(route_resupply.id)]
                        }) 
                replenish_wizard = self.env['product.replenish'].create({
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'quantity': line.product_uom_qty,
                    'warehouse_id': r.warehouse_id.id,
                    'route_ids': [(6,0,route_ids)],
                })
                extra_val = {
                    'supplierinfo_id': line._get_supplierinfo_id(),
                    'outsource_type': line.outsource_type,
                    'sale_outsource_id': line.id,
                    'subcontract_bom_id': line.subcontract_bom_id and line.subcontract_bom_id.id or False,
                }
                # 采购行需求禁止合并设置检查
                route_buy = self.env.ref('purchase_stock.route_warehouse0_buy')
                for rule in route_buy.rule_ids:
                    if rule.group_propagation_option != 'propagate':
                        rule.group_propagation_option = 'propagate'
                replenish_wizard.with_context(extra_val=extra_val).launch_replenishment2(line.order_id.name,line.order_id.name)                
        return True

