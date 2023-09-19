from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    currency_rate = fields.Float(
        "Currency Rate",
        compute="_compute_currency_rate",
        compute_sudo=True,
        store=True,
        readonly=False,
        required=False,
        help="Ratio between the purchase order currency and the company currency",
    )

    @api.depends("date_order", "currency_id", "company_id", "company_id.currency_id")
    def _compute_currency_rate(self):
        for order in self:
            if order.currency_rate:
                continue
            order.currency_rate = self.env["res.currency"]._get_conversion_rate(
                order.company_id.currency_id,
                order.currency_id,
                order.company_id,
                order.date_order,
            )
