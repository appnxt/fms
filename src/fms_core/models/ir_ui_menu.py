# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID

class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @api.returns('self')
    def get_user_roots(self):
        """ Return all root menu ids visible for the user.

        :return: the root menu ids
        :rtype: list(int)
        """
        if not self.env.uid == SUPERUSER_ID:
            domain = [('module','=','fms_menu'),('name','=like','menu_fms_%')]
            ids = self.env['ir.model.data'].sudo().search(domain).mapped('res_id')
            return self.browse(ids)
        return super().get_user_roots()