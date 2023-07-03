from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CashForecastFiscalYear(models.Model):
    _name = 'cash.forecast.fiscal.year'
    _description = "Cash forecast Fiscal Year"
    _order = "end_date desc"

    code = fields.Char("Code")
    name = fields.Char("Name")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    period_interval = fields.Selection(
        string='Period Interval',
        selection=[('days', 'Daily'),
                   ('weeks', 'Weekly'),
                   ('months', 'Monthly')])

    fiscal_period_ids = fields.One2many("cash.forecast.fiscal.period", "fiscal_id", "Fiscal Period")
    company_id = fields.Many2one('res.company', string='Company')

    @api.constrains('code', 'start_date', 'end_date')
    def _check_period_date(self):
        if self.search([('id', '!=', self.id), '|', ('code', '=', self.code),
                        '&', ('start_date', '<', self.end_date),
                        ('end_date', '>', self.start_date),('company_id', '=', self.company_id.id)
                        ]):
            raise ValidationError(_("This Start Date, End Date or Code is used in other fiscal year"))
        if self.start_date >= self.end_date:
            raise ValidationError(_("End Date should be greater than Start Date"))
        return True

    def create_monthly_period(self, interval=1):
        period_obj = self.env['cash.forecast.fiscal.period']
        ds = datetime.strptime(self.start_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
        weeks_index = 1
        while ds.date() < self.end_date:
            if self.period_interval != 'days':
                de = ds + relativedelta(**{self.period_interval: interval}, days=-1)
            else:
                de = ds

            if de.date() > self.end_date:
                de = datetime.strptime(str(self.end_date), '%Y-%m-%d')

            if self.period_interval == 'days':
                code = ds.strftime('%Y-%m-%d')
            elif self.period_interval == 'weeks':
                code = f"{self.code}-W{weeks_index}"
                weeks_index += 1
            else:
                code = ds.strftime('%m/%Y')

            period_obj.create({
                'code': code,
                'start_date': ds.strftime('%Y-%m-%d'),
                'end_date': de.strftime('%Y-%m-%d'),
                'fiscal_id': self.id,
            })
            ds = ds + relativedelta(**{self.period_interval: interval})
        return True


class CashForecastFiscalPeriod(models.Model):
    _name = 'cash.forecast.fiscal.period'
    _description = "Cash forecast Fiscal Period"
    _rec_name = 'code'
    _order = 'start_date'

    code = fields.Char("Code")
    fiscal_id = fields.Many2one("cash.forecast.fiscal.year", "Fiscal Year", ondelete='cascade')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    company_id = fields.Many2one('res.company', string='Company', related='fiscal_id.company_id')
    period_interval = fields.Selection(
        string='Period Interval',
        selection=[('days', 'Daily'),
                   ('weeks', 'Weekly'),
                   ('months', 'Monthly')],
                    related='fiscal_id.period_interval')

    def update_cash_forecast(self):
        return self.env['create.update.cash.forecast'].with_context(period_id=self.id).update_cash_forecast()

    @api.constrains('start_date', 'end_date')
    def _check_period_date(self):
        if self.search([('id', '!=', self.id), '|', ('start_date', '=', self.start_date),
                        ('end_date', '=', self.end_date),('company_id', '=', self.company_id.id)]):
            raise ValidationError(_("This date period is already created"))
        return True

    def unlink(self):
        if self.env['setu.cash.forecast'].search([('forecast_period_id', 'in', self.ids)]):
            raise ValidationError(_("You can't Delete period Because This Period Forecast already created"))
        return super(CashForecastFiscalPeriod, self).unlink()
