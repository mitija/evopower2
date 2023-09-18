from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
