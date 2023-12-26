# -*- coding: utf-8 -*-
##############################################################################
#
#    FMS aSuite Appnxt.com Jun.ac
#    Copyright (C) 2017~2023 上海磐麓网络科技有限公司 (<https://www.appnxt.com/>).
#
##############################################################################
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import ValidationError,UserError
from odoo.fields import Command

class StockMove(models.Model):
    _inherit = 'stock.move'

    def object_selection_values(self):
        """
        Overridable method for adding more object models to an inspection.
        :return: A list with the selection's possible values.
        """
        return [("sale.order.line", "销售行"),('purchase.order.line','采购行')]

    x_product_uom_qty = fields.Float(compute='_compute_object_id',string='订单量',group_operator="avg",store=False)
    x_qty_delivered = fields.Float(compute='_compute_object_id',string='已发货',group_operator="avg",store=False)
    x_qty_invoiced = fields.Float(compute='_compute_object_id',string='已开票',group_operator="avg",store=False)
    x_qty_to_invoice = fields.Float(compute='_compute_object_id',string='待开票',group_operator="avg",store=False)
    account_move_line_ids = fields.One2many('account.move.line','stock_move_id',string='发票行')
    object_id = fields.Reference(
        string="Reference",
        selection="object_selection_values",
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="set null", compute="_compute_object_id",store=False
    )

    # @api.depends('sale_line_id','purchase_line_id')
    def _compute_object_id(self):
        for r in self:
            object_ref = r.sale_line_id or r.purchase_line_id or False
            r.object_id = object_ref\
                    and "{},{}".format(object_ref._name, object_ref.id)\
                    or False
            x_product_uom_qty = x_qty_delivered = x_qty_invoiced = x_qty_to_invoice = 0
            if r.object_id:
                x_qty_invoiced = r.object_id.qty_invoiced
                x_qty_to_invoice = r.object_id.qty_to_invoice
                if object_ref._name == 'sale.order.line':
                    x_product_uom_qty = r.object_id.product_uom_qty
                    x_qty_delivered = r.object_id.qty_delivered
                else:
                    x_product_uom_qty = r.object_id.product_qty
                    x_qty_delivered = r.object_id.qty_received 
            r.x_product_uom_qty = x_product_uom_qty
            r.x_qty_delivered = x_qty_delivered
            r.x_qty_invoiced = x_qty_invoiced
            r.x_qty_to_invoice = x_qty_to_invoice

    def _action_confirm(self, merge=True, merge_into=False):
        res = super()._action_confirm(merge=merge, merge_into=merge_into)
        return res

    def _get_subcontract_bom(self):
        self.ensure_one()
        if self.purchase_line_id and self.purchase_line_id.subcontract_bom_id:
            if self.picking_id.partner_id not in self.purchase_line_id.subcontract_bom_id.subcontractor_ids:
                self.purchase_line_id.subcontract_bom_id.write({
                    'subcontractor_ids': [Command.link(self.picking_id.partner_id.id)]
                })
            return self.purchase_line_id.subcontract_bom_id
        return super()._get_subcontract_bom()   

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        if self.purchase_line_id and self.purchase_line_id.workorder_id:
            res['purchase_line_id'] = self.purchase_line_id.id
            res['workorder_id'] = self.purchase_line_id.workorder_id.id
        return res
    
    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for r in self: #todo 未生效
            if r.purchase_line_id and r.purchase_line_id.outsource_type == 'process_outsourcing':
                if r.picking_type_id.code == 'incoming':
                    r.workorder_id.button_finish()
                if r.picking_type_id.code == 'outgoing':
                    r.workorder_id.button_start()                    
        return res

    def create_invoices(self):
        todo_moves = self.filtered(lambda r: r.state == 'done' and not r.account_move_line_ids)
        if not todo_moves:
            raise ValidationError('没有需要开票的库存移动！')
        orders = todo_moves.mapped('sale_line_id').mapped('order_id')
        if len(orders.mapped('partner_id')) >1:
            raise ValidationError('一次只能对一个客户开票！')
        
        invoice_vals_list = []
        invoice_line_vals = []
        invoice_item_sequence = 0
        invoice_vals = orders[0]._prepare_invoice()
        for sm in todo_moves:
            line = sm.sale_line_id
            invoice_item_sequence += 1
            val = line._prepare_invoice_line(sequence=invoice_item_sequence)
            if not float_compare(val['quantity'],0,2) == 1:
                raise ValidationError('已经没有代开发票!')
            val['stock_move_id'] = sm.id
            # todo sm 判断更精确
            val['quantity'] = -sm.product_uom_qty if (sm.location_dest_id.usage != "customer" and sm.to_refund) else sm.product_uom_qty
            invoice_line_vals.append(
                Command.create(
                    val
                ),
            )
        invoice_vals['invoice_line_ids'] += invoice_line_vals
        invoice_vals_list.append(invoice_vals)

        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        for move in moves:
            move.message_post_with_view(
                'mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.stock_move_id.picking_id},
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'))
        return moves