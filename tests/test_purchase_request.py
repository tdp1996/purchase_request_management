from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError

@tagged('-at_install', 'post_install')
class TestPurchaseRequestLine(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestLine, self).setUp()
        
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
        self.product_a = self.env['product.template'].create({
            'name': 'Test Product A',
            'list_price': 100.0
        })

        self.product_b = self.env['product.template'].create({
            'name': 'Test Product B',
            'list_price': 50.0
        })
        self.uom = self.env.ref('uom.product_uom_unit')
        
        # Tạo purchase request
        self.purchase_request = self.env['purchase.request'].create({
            'department_id': self.department.id,
            'request_id': self.request_user.id,
            'approver_id': self.approver_user.id,
        })
        
        self.purchase_request_line = self.env['purchase.request.line'].create({
            'product_id': self.product_a.id,
            'uom_id': self.uom.id,
            'price_unit': 100.0,
            'qty': 5.0,
            'request_id': self.purchase_request.id,  
        })

    def test_unlink_valid(self):
        self.purchase_request.unlink()
        self.assertFalse(self.purchase_request.exists())

    def test_unlink_invalid(self):
        self.purchase_request.write({'state': 'wait'})
        with self.assertRaises(UserError):
            self.purchase_request.unlink()

    def test_compute_total_quantity(self):
        self.purchase_request_line = self.env['purchase.request.line'].create({
            'product_id': self.product_b.id,
            'uom_id': self.uom.id,
            'price_unit': 50.0,
            'qty': 3.0,
            'request_id': self.purchase_request.id,  
        })
        self.purchase_request._compute_total_quantity()
        expected_total_qty = 5.0 + 3.0
        self.assertEqual(self.purchase_request.total_qty, expected_total_qty)

    def test_compute_total_amount(self):
        self.purchase_request_line = self.env['purchase.request.line'].create({
            'product_id': self.product_b.id,
            'uom_id': self.uom.id,
            'price_unit': 50.0,
            'qty': 3.0,
            'request_id': self.purchase_request.id,  
        })
        self.purchase_request._compute_total_amount()
        expected_total_amount = 5.0*100.0 + 3.0*50.0
        self.assertEqual(self.purchase_request.total_amount, expected_total_amount)

    def test_purchase_request_state_transitions(self):
        self.purchase_request.action_request_approval()
        self.assertEqual(self.purchase_request.state, 'wait')

        self.purchase_request.action_pr_approve()
        self.assertEqual(self.purchase_request.state, 'approved')

        self.purchase_request.action_pr_back()
        self.assertEqual(self.purchase_request.state, 'draft')
