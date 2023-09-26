from odoo import Command, _, api, fields, models


class AccountMoveLine(models.Model):
  _inherit = "account.move.line"

  @api.depends('sale_line_ids.order_id.manual_currency_rate', 'purchase_line_id.order_id.manual_currency_rate')
  def _compute_currency_rate(self):
      def get_rate(from_currency, to_currency, company, date):
          return self.env['res.currency']._get_conversion_rate(
              from_currency=from_currency,
              to_currency=to_currency,
              company=company,
              date=date,
          )
      for line in self:
          if line.currency_id:
              if (line.journal_id.type == 'sale' 
                  and line.sale_line_ids.order_id.manual_currency_rate > 0):
                line.currency_rate = line.sale_line_ids.order_id.manual_currency_rate
              elif (line.journal_id.type == 'purchase' 
                    and line.purchase_line_id.order_id.manual_currency_rate > 0):
                line.currency_rate = line.purchase_line_id.order_id.manual_currency_rate
              else:
                line.currency_rate = get_rate(
                  from_currency=line.company_currency_id,
                  to_currency=line.currency_id,
                  company=line.company_id,
                  date=line.move_id.invoice_date 
                  or line.move_id.date 
                  or fields.Date.context_today(line),
              )
          else:
              line.currency_rate = 1
