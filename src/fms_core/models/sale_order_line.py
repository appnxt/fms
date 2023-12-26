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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    drawing_no = fields.Char(string='Drawing Number',related='product_id.default_code',readonly=False)
    material_id = fields.Many2one('product.product',string='Material', domain=[('purchase_ok','=',True)])
    qty_material = fields.Float(related='material_id.free_qty',string='Available inventory')
    qty_production = fields.Float('Planned production quantity')
    bom_id = fields.Many2one('mrp.bom',string='BOM')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.material_id = self.product_id.material_id and self.product_id.material_id.id or False
            bom = self.env['mrp.bom'].sudo()._bom_find(self.product_id,bom_type='normal')[self.product_id]
            self.bom_id = bom and bom.id or False

    def _validate_analytic_distribution(self):
        for line in self:
            if not line.material_id or not line.drawing_no:
                raise ValidationError(f'Need {line.product_id.display_name}Drawing number or Material')  
            if not line.product_id.material_id or not line.product_id.default_code:  
                line.product_id.write({
                    'default_code': line.drawing_no,
                    'material_id': line.material_id.id
                })
        return super()._validate_analytic_distribution()

    def _get_production_extra_vals(self):
        self.ensure_one()
        if not self.bom_id:
            raise ValidationError(f"Need {self.product_id.display_name}'s BOM")
        extra_val = {
            'sale_line_id':self.id,
            'quantity':self.qty_production,
            'bom_id': self.bom_id,
        }
        return extra_val
    
    def action_show_bom_details(self):
        self.ensure_one()
        view = self.env.ref('mrp.mrp_bom_form_view')
        if not self.material_id:
            raise ValidationError(f"Need {self.product_id.display_name}'s Material")
        if not self.bom_id:
            bom = self.env['mrp.bom'].create({
                'product_id': self.product_id.id, 
                'type':'normal',
                'product_tmpl_id':self.product_id.product_tmpl_id.id,
                'bom_line_ids': [Command.create({
                    'product_id': self.material_id.id,
                    'product_uom_id': self.material_id.uom_id.id,
                    'product_qty': 1,
                })]
            })
            self.bom_id = bom.id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.bom_id.id,
            'context': dict(
                self.env.context,
            ),
        }
