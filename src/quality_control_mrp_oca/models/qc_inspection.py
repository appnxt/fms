# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == "mrp.production":
            res["qty"] = object_ref.product_qty
        if object_ref and object_ref._name == "mrp.workorder":
            res["qty"] = object_ref.qty_remaining
        return res

    @api.depends("object_id")
    def _compute_production_id(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move":
                    inspection.production_id = inspection.object_id.production_id
                elif inspection.object_id._name == "mrp.production":
                    inspection.production_id = inspection.object_id
                elif inspection.object_id._name == "mrp.workorder":
                    inspection.workorder_id = inspection.object_id
                    inspection.production_id = inspection.object_id.production_id

    @api.depends("object_id")
    def _compute_product_id(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            super()._compute_product_id()
            if inspection.object_id and inspection.object_id._name == "mrp.production":
                inspection.product_id = inspection.object_id.product_id
            if inspection.object_id and inspection.object_id._name == "mrp.workorder":
                inspection.product_id = inspection.object_id.product_id

    def object_selection_values(self):
        objects = super().object_selection_values()
        objects.append(("mrp.production", "Manufacturing Order"))
        objects.append(("mrp.workorder", "Worker Order"))
        return objects

    production_id = fields.Many2one(
        comodel_name="mrp.production", compute="_compute_production_id", store=True
    )
    workorder_id = fields.Many2one(
        comodel_name="mrp.workorder", compute="_compute_production_id", store=True
    )

    def button_scrap(self):
        self.ensure_one()
        # 生产报废
        return {
            'name': _('Scrap'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.production_id.id,
                        'product_ids': (self.production_id.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.production_id.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        'default_company_id': self.production_id.company_id.id
                        },
            'target': 'new',
        }

class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        related="inspection_id.production_id",
        store=True,
        string="Production order",
    )
