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

class SaleOrderOutsource(models.Model):
    _name = 'sale.order.outsource'
    _description = 'Outsourcing Orders'

    order_id = fields.Many2one('sale.order',string='Sale order')
    sale_line_id = fields.Many2one('sale.order.line',string='SO行')
    product_id = fields.Many2one(related='sale_line_id.product_id',string='Material')
    product_uom_qty = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one(related='sale_line_id.product_uom',string='UoM')
    vendor_id = fields.Many2one('res.partner',string='Vendor')
    outsource_type = fields.Selection([
        ('outsourcing','Outsourcing'),
        ('subcontract','Subcontract'),
    ],string='Outsource Type',default='outsourcing')
    price_unit = fields.Float(string='Price')
    subcontract_bom_id = fields.Many2one('mrp.bom',string='Subcontract BOM')

    def _get_supplierinfo_id(self,product_id=False,vendor_id=False):
        self.ensure_one()
        supplier_infos = self.env['product.supplierinfo'].search([
            ('product_id', '=', product_id or self.product_id.id),
            ('partner_id', '=', vendor_id or self.vendor_id.id),
        ])
        if not supplier_infos: # todo opt
            supplier_infos = self.create_supplier_info()
        return supplier_infos[0]

    def create_supplier_info(self):
        # create a supplier_info only in case of blanket order
        return self.env['product.supplierinfo'].sudo().create({
                'partner_id': self.vendor_id.id,
                'product_id': self.product_id.id,
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'price': self.price_unit,
                'currency_id': self.order_id.pricelist_id.currency_id.id,
            })

    def _set_subcontract_bom_id(self):
        self.ensure_one()
        if self.outsource_type == 'subcontract':
            bom = self.env['mrp.bom'].sudo()._bom_subcontract_find(
                self.product_id,
                # picking_type=self.picking_type_id,
                # company_id=self.company_id.id,
                bom_type='subcontract',
                subcontractor=self.vendor_id,
            )
            if not bom:
                bom = self._add_subcontract_bom_auto()
            self.subcontract_bom_id = bom.id

    def _add_subcontract_bom_auto(self):
        bom = self.env['mrp.bom']
        product, picking_type,company_id,bom_type = self.product_id, False,self.order_id.company_id.id,'subcontract'
        domain = bom._bom_find_domain(product, picking_type=picking_type, company_id=company_id, bom_type=bom_type)
        bom = bom.env['mrp.bom'].search(domain, order='sequence, product_id, id', limit=1)
        if bom:
            bom[0].sudo().write({
                'subcontractor_ids': [(4,self.vendor_id.id,False)]
            })
        else:
            if not self.sale_line_id.material_id:
                raise ValidationError('Raw materials are required.')
            bom = self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': self.product_id.product_tmpl_id.id,
                'product_qty': 1,
                'type': 'subcontract',
                'subcontractor_ids': [(4,self.vendor_id.id,False)],
                'bom_line_ids': [(0,0,{
                    'product_id': self.sale_line_id.material_id.id,
                    'product_qty': 1,
                })],
            })
        return bom