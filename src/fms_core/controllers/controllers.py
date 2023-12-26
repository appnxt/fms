# -*- coding: utf-8 -*-
# from odoo import http


# class FmsPlanOrder(http.Controller):
#     @http.route('/fms_core/fms_core', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fms_core/fms_core/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fms_core.listing', {
#             'root': '/fms_core/fms_core',
#             'objects': http.request.env['fms_core.fms_core'].search([]),
#         })

#     @http.route('/fms_core/fms_core/objects/<model("fms_core.fms_core"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fms_core.object', {
#             'object': obj
#         })
