

from odoo import api, fields, models, Command, _


class AccountMoveLine(models.Model):
  _inherit = "account.move.line"

  @api.depends('sale_line_ids.order_id.manual_currency_rate', 'purchase_line_id.order_id.manual_currency_rate')
  def _compute_currency_rate(self):
      for line in self:
          if line.currency_id:
              if line.journal_id.type == 'sale':
                line.currency_rate = line.sale_line_ids.order_id.manual_currency_rate
              elif line.journal_id.type == 'purchase':
                line.currency_rate = line.purchase_line_id.order_id.manual_currency_rate
          else:
              line.currency_rate = 1

