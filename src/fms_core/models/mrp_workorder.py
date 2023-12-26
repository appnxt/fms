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


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    move_ids = fields.One2many('stock.move', 'workorder_id', string='Moves')

    def _cal_cost(self, times=None):
        if self.operation_id.outsourcing_product_id and self.move_ids:
            return self.move_ids[0]._get_price_unit()
        return super()._cal_cost(times)