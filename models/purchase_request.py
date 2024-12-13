# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"

    name = fields.Char(
        "Purchase Reference", 
        readonly=True, 
        required=True, 
        copy=False, 
        default="New")

    purchase_order_ids = fields.One2many(
        'purchase.order', 
        'purchase_request_id', 
        string="Purchase Orders", 
        readonly=True)

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        default=lambda self: self.env.user.department_id,
        readonly=True,
        required=True)

    request_id = fields.Many2one(
        comodel_name="res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        readonly=True,
        required=True)

    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        default=lambda self: self.env.user.employee_ids.parent_id,
        readonly=True,
        required=True)

    date_request = fields.Date(
        string="Request Date",
        default=fields.Date.context_today,
        readonly=True,
        required=True)

    date_approve = fields.Date(
        string="Approve Date", 
        readonly=True)

    description = fields.Text(
        string="Description")

    state = fields.Selection(
        selection=[
            ("draft", "Quotation"),
            ("wait", "Waiting"),
            ("approved", "Approved"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
    )

    request_line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Request Line",
    )

    total_qty = fields.Float(
        compute="_compute_total_quantity", 
        string="Total Quantity")

    total_amount = fields.Float(
        compute="_compute_total_amount", 
        string="Total Amount")

    @api.depends("request_line_ids.qty", "request_line_ids.qty_approve")
    def _compute_total_quantity(self):
        for record in self:
            record.total_qty = sum(
                line.qty if not line.qty_approve else line.qty_approve
                for line in record.request_line_ids
            )

    @api.depends("request_line_ids.total")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.total for line in record.request_line_ids)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("purchase.request")
            return super(PurchaseRequest, self).create(vals)
    

    # ACTIONS
    def action_pr_back(self):
        self.state = "draft"

    def action_pr_reject(self):
        return {
            "name": "Enter the reason for rejection",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "purchase.request.reject.wizard",
            "target": "new",
        }

    def action_request_approval(self):
        if any(line.qty == 0.00 for line in self.request_line_ids):
            raise ValidationError("The quantity for all request lines must be greater than zero.")
        self.state = "wait"

    def action_pr_approve(self):
        if any(
            line.qty_approve == 0.00 or line.qty_approve > line.qty
            for line in self.request_line_ids
        ):
            raise ValidationError(
                "The approved quantity must be greater than zero and cannot exceed the requested quantity."
            )
        self.date_approve = fields.Date.context_today(self)
        self.state = "approved"

    def action_pr_order(self):
        self.ensure_one()
        
        purchase_order_data = {
            'purchase_request_id': self.id,
            'order_line': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom': line.product_id.uom_po_id.id,
                    'product_qty': line.qty_approve,
                })
                for line in self.request_line_ids
            ],
        }
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'context': {
                'default_' + k: v for k, v in purchase_order_data.items()
            },
            'target': 'current',
        }

