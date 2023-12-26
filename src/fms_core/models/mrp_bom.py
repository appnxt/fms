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

class MRBOM(models.Model):
    _inherit = 'mrp.bom'

    def name_get(self):
        return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name if not bom.product_id else bom.product_id.display_name)) for bom in self]    