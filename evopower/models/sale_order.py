from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    currency_rate = fields.Float(
        string="Currency Rate",
        compute='_compute_currency_rate',
        digits=(12, 6),
        store=True, 
        readonly=False,
        required=False)

    @api.depends('currency_id', 'date_order', 'company_id')
    def _compute_currency_rate(self):
        cache = {}
        for order in self:
            if order.currency_rate:
                continue
            order_date = order.date_order.date()
            if not order.company_id:
                order.currency_rate = order.currency_id.with_context(date=order_date).rate or 1.0
                continue
            elif not order.currency_id:
                order.currency_rate = 1.0
            else:
                key = (order.company_id.id, order_date, order.currency_id.id)
                if key not in cache:
                    cache[key] = self.env['res.currency']._get_conversion_rate(
                        from_currency=order.company_id.currency_id,
                        to_currency=order.currency_id,
                        company=order.company_id,
                        date=order_date,
                    )
                order.currency_rate = cache[key]

    @api.depends("currency_id")
    def _set_exchange_rate(self):
        for record in self:
            record.custom_exchange_rate = 0
            if record.currency_id:
                record.custom_exchange_rate = record.currency_id.rate

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped("state")):
            raise UserError(
                _(
                    "It is not allowed to confirm an order in the following states: %s",
                    ", ".join(self._get_forbidden_state_confirm()),
                )
            )

        self.order_line._validate_analytic_distribution()

        for order in self:
            order.validate_taxes_on_sales_order()

        self.write(self._prepare_confirmation_values())

        context = self._context.copy()
        context.pop("default_name", None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group("sale.group_auto_done_setting"):
            self.action_done()
