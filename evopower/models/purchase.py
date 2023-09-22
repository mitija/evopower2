from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    manual_currency_rate = fields.Float(string="Currency Rate")

    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        self.manual_currency_rate = self.currency_id.rate