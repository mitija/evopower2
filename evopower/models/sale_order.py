from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    manual_currency_rate = fields.Float(string="Currency Rate")

    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        self.manual_currency_rate = self.currency_id.rate

