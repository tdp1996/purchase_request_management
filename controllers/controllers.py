# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseRequestManagement(http.Controller):
#     @http.route('/purchase_request_management/purchase_request_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_request_management/purchase_request_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_request_management.listing', {
#             'root': '/purchase_request_management/purchase_request_management',
#             'objects': http.request.env['purchase_request_management.purchase_request_management'].search([]),
#         })

#     @http.route('/purchase_request_management/purchase_request_management/objects/<model("purchase_request_management.purchase_request_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_request_management.object', {
#             'object': obj
#         })
