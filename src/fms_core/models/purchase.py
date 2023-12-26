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

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.order_line.filtered(lambda l: l.workorder_id):
            res['location_id'] = self.company_id.subcontracting_location_id.id
        return res
    
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for r in self:
            r.group_id.stock_move_ids._action_cancel()
        return res
    