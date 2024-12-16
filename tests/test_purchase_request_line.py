from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError
from odoo import fields
from datetime import datetime

@tagged('-at_install', 'post_install')
class TestPurchaseRequestLine(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestLine, self).setUp()
        
        # Tạo dữ liệu cần thiết
        self.department = self.env['hr.department'].create({
            'name': 'IT',
        })
        self.request_user = self.env['res.users'].create({
            'name': 'Request User',
            'login': 'request_user'
        })
        self.approver_user = self.env['res.users'].create({
            'name': 'Approver User',
            'login': 'approver_user'
        })
        self.product = self.env['product.template'].create({
            'name': 'Test Product',
            'list_price': 100.0
        })
        self.uom = self.env.ref('uom.product_uom_unit')
        
        # Tạo purchase request
        self.purchase_request = self.env['purchase.request'].create({
            'department_id': self.department.id,
            'request_id': self.request_user.id,
            'approver_id': self.approver_user.id,
        })
        
        self.purchase_request_line = self.env['purchase.request.line'].create({
            'product_id': self.product.id,
            'uom_id': self.uom.id,
            'price_unit': 0.0,
            'qty': 5.0,
            'request_id': self.purchase_request.id,  
        })


    def test_compute_total_with_qty_and_list_price(self):
        self.purchase_request_line._compute_total()
        expected_total = 5.0 * 100.0 
        self.assertEqual(self.purchase_request_line.total, expected_total)

    def test_compute_total_with_unit_price(self):
        self.purchase_request_line.write({'price_unit': 125.0})
        self.purchase_request_line._compute_total()
        expected_total = 5.0 * 125.0 
        self.assertEqual(self.purchase_request_line.total, expected_total)

    def test_compute_total_with_qty_approve(self):
        self.purchase_request_line.write({'qty_approve': 3.0})
        self.purchase_request_line._compute_total()
        expected_total = 3.0 * 100.0
        self.assertEqual(self.purchase_request_line.total, expected_total)

    def test_onchange_qty_approve_and_price(self):
        self.purchase_request_line.qty_approve = 2.0
        self.purchase_request_line.price_unit = 120.0
        self.purchase_request_line._onchange_qty_approve_and_price()
        expected_total = 2.0 * 120.0
        self.assertEqual(self.purchase_request_line.total, expected_total)

    def test_create_in_draft_state(self):
        self.purchase_request.write({'state': 'wait'})
        with self.assertRaises(UserError):
            self.env['purchase.request.line'].create({
                'request_id': self.purchase_request.id,
                'product_id': self.product.id,
                'uom_id': self.uom.id,
                'price_unit': 100.0,
                'qty': 2.0
            })

    def test_create_valid(self):
        line = self.env['purchase.request.line'].create({
            'request_id': self.purchase_request.id,
            'product_id': self.product.id,
            'uom_id': self.uom.id,
            'price_unit': 50.0,
            'qty': 3.0
        })
        self.assertEqual(line.price_unit, 50.0)
        self.assertEqual(line.qty, 3.0)

    def test_unlink_valid(self):
        self.purchase_request_line.unlink()
        self.assertFalse(self.purchase_request_line.exists())

    def test_unlink_invalid(self):
        self.purchase_request_line.write({'state': 'wait'})
        with self.assertRaises(UserError):
            self.purchase_request_line.unlink()

    def test_write_valid(self):
        self.purchase_request_line.write({'state': 'wait','qty_approve': 3.0})
        self.assertEqual(self.purchase_request_line.qty_approve, 3.0)

