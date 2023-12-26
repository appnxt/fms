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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_process_outsourcing = fields.Boolean(string='Process Outsourcing')

    @api.constrains('is_process_outsourcing')
    def _check_is_process_outsourcing(self):
        for r in self:
            if r.is_process_outsourcing and r.detailed_type != 'consu':
                raise ValidationError('Process outsourcing products can only be consumed types')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    material_id = fields.Many2one('product.product',string='Material')
    # design_drawing = fields.Binary(string='图纸')

    @api.constrains('material_id')
    def _check_material_id(self):
        for r in self:
            if r.material_id.id == r.id:
                raise ValidationError('The raw material cannot have the same material number as the finished product.')


