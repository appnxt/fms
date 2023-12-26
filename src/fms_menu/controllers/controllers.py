# -*- coding: utf-8 -*-
# from odoo import http


# class FmsMenu(http.Controller):
#     @http.route('/fms_menu/fms_menu', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fms_menu/fms_menu/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fms_menu.listing', {
#             'root': '/fms_menu/fms_menu',
#             'objects': http.request.env['fms_menu.fms_menu'].search([]),
#         })

#     @http.route('/fms_menu/fms_menu/objects/<model("fms_menu.fms_menu"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fms_menu.object', {
#             'object': obj
#         })
