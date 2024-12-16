from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"

    request_id = fields.Many2one(
        comodel_name="purchase.request", 
        string="Order Reference", 
        ondelete="cascade")

    state = fields.Selection(
        related="request_id.state", 
        string="State", 
        readonly=True)

    product_id = fields.Many2one(
        comodel_name="product.template", 
        string="Product", 
        required=True)

    uom_id = fields.Many2one(
        comodel_name="uom.uom", 
        string="Unit Of Measure", 
        required=True)

    price_unit = fields.Float(
        string="Unit Price", 
        required=True)

    qty = fields.Float(
        string="Quantity", 
        required=True)

    qty_approve = fields.Float(
        string="Aprroved Quantity")

    total = fields.Float(
        compute="_compute_total", 
        string="Total", 
        readonly=True)
    
    @api.model
    def create(self, vals):
        purchase_request = self.env['purchase.request'].browse(vals.get('request_id'))
        if purchase_request.state != 'draft':
            raise UserError(_("You can only add purchase request details in 'Draft' state."))
        return super(PurchaseRequestLine, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("You can only delete purchase request details in 'Draft' state."))
        return super(PurchaseRequestLine, self).unlink()

    def write(self, vals):
        for record in self:
            if record.state != 'draft':
                if record.state == 'wait' and 'qty_approve' in vals:
                    pass 
        return super(PurchaseRequestLine, self).write(vals)

    @api.depends("qty", "product_id.list_price", "price_unit", "qty_approve")
    def _compute_total(self):
        for record in self:
            if record.product_id:
                unit_price = record.price_unit or record.product_id.list_price
                quantity = (
                    record.qty_approve if record.qty_approve != 0.00 else record.qty
                )
                record.total = quantity * unit_price

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                purchase_line = self.env["purchase.order.line"].search(
                    [("product_id", "=", record.product_id.id)],
                    order="create_date desc",
                    limit=1,
                )
                record.price_unit = purchase_line.price_unit
                record.uom_id = purchase_line.product_uom or "Units"

    @api.onchange("qty_approve", "price_unit")
    def _onchange_qty_approve_and_price(self):
        for record in self:
            price = record.price_unit or record.product_id.list_price
            record.total = record.qty_approve * price
