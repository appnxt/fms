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

class OperationNmae(models.Model):
    _name = 'operation.name'
    _description = 'Operation Name'

    name = fields.Char(string='Name', required=True, translate=True,help='Operation Name')

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    op_name_id = fields.Many2one('operation.name', string='Operation Name')
    name = fields.Char(related='op_name_id.name', string='Operation Name')