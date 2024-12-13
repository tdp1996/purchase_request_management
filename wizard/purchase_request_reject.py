from odoo import fields, models

class PurchaseRequestReject(models.TransientModel):
    _name = 'purchase.request.reject.wizard'
    _description = 'Purchase Request Rejection Reason'

    reject_reason = fields.Text(string="Reason for refusal", require=True)

    def action_rejection_reason_apply(self):
        self.ensure_one()
        request = self.env['purchase.request'].browse(
                self.env.context.get('active_ids'))
        request.write({
            'state': 'cancel',
            'description': self.reject_reason
        })


        

