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
from odoo.tools import frozendict, formatLang, format_date, float_compare, Query
from odoo.tools.misc import clean_context

class ProductReplenish(models.TransientModel):
    _inherit = 'product.replenish'

    def launch_replenishment2(self,name,origin):
        uom_reference = self.product_id.uom_id
        self.quantity = self.product_uom_id._compute_quantity(self.quantity, uom_reference, rounding_method='HALF-UP')
        try:
            extra_val = self.env.context.get('extra_val',{})
            self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                self.env['procurement.group'].Procurement(
                    self.product_id,
                    self.quantity,
                    uom_reference,
                    self.warehouse_id.lot_stock_id,  # Location
                    name,  # Name
                    origin,  # Origin
                    self.warehouse_id.company_id,
                    self.with_context(extra_val=extra_val)._prepare_run_values()  # Values
                )
            ])
        except UserError as error:
            raise UserError(error)

    def _prepare_run_values(self):
        values = super()._prepare_run_values()
        extra_val = self.env.context.get('extra_val')
        if extra_val:
            values.update(extra_val)
        return values

