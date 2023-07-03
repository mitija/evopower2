import json
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from statistics import mean


class SetuCashForecastType(models.Model):
    _name = 'setu.cash.forecast.type'
    _description = 'Cash Forecast Type'
    _inherit = ['mail.thread']
    _order = 'sequence'

    name = fields.Char('Name')
    code = fields.Char('Code')
    type = fields.Selection([('income', 'Cash In'), ('expense', 'Cash Out'),
                             ('opening', 'Opening Forecast'), ('closing', 'Closing Forecast'),
                             ('net_forecast', 'Net Forecasting')],
                            string="Group")
    forecasting_tag = fields.Many2one('cash.forecast.tag', string='Forecasting Tag')
    cash_forecast_category_id = fields.Many2one('setu.cash.forecast.categories', string="Category name")
    is_group_for_opening = fields.Boolean("Is Group For Opening Balance",
                                          related='cash_forecast_category_id.is_group_for_opening')
    sequence = fields.Integer('Sequence')
    is_recurring = fields.Boolean('Recurring forecast', default=False,
                                  help="Enable this option to Calculate Forecast repeatedly after the months"
                                       "that you select in Forecast Execution Duration")
    forecast_start_period = fields.Many2one('cash.forecast.fiscal.period', string='Forecast Start Period',
                                            help="Forecast will be calculated from the period that is selected here")
    forecast_end_period = fields.Many2one('cash.forecast.fiscal.period', string='Forecast End Period',
                                          help="Forecast will be calculated up to the period that is selected here")
    period_interval = fields.Selection(string='Period Interval', selection=[('days', 'Daily'),
                                                                            ('weeks', 'Weekly'),
                                                                            ('months', 'Monthly')],
                                       related='forecast_start_period.fiscal_id.period_interval')
    recurring_duration_interval = fields.Integer(default='1', string='Forecast Execution Duration(In Months)',
                                        help="Select duration in Months after which you wish to Execute next Forecast"
                                               "Forecast will be executed after the number of Months that is selected"
                                               " here between duration of Forecast Start Period and Forecast End Period"
                                        )

    parent_forecast_type_id = fields.Many2one('setu.cash.forecast.type', string='Parent forecast type')
    child_forecast_ids = fields.One2many('setu.cash.forecast.type', 'parent_forecast_type_id',
                                         string='Child forecast types')

    account_ids = fields.Many2many('account.account', string="Accounts", copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Accounts", copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=False, default=lambda self: self.env.company)

    auto_calculate = fields.Boolean("Auto Calculate", default=True,
                                    help="Enable this option if Cash Forecast should be calculated based "
                                         "on Auto Calculation Formula set."
                                         "If this option is disabled then "
                                         "Cash Forecast will be calculated based on Fixed Value that you enter")
    fixed_value = fields.Float("Fixed value")
    dep_forecast_ids = fields.Many2many('setu.cash.forecast.type', 'cash_forecast_type_dependent', 'forecast_type_id',
                                        string='Dependant Forecast Type', copy=False)
    invisible_in_report = fields.Boolean('Invisible in report', default=False)

    # Forecast calculate formula
    calculate_from = fields.Selection([('past_account_entries', 'Past Accounting Entries'),
                                       ('past_period_forecasting_entries', 'Past Period Forecasting Entries'),
                                       ('pending', 'Pending Payable / Receivable'),
                                       ('dependant', 'Base on Dependant Forecast')],
                                      string="Calculate from",
                                      help="-Past Accounting Entries of the Accounts that are selected in Account tab "
                                           "will be considered based on option that you select in Calculation Pattern "
                                           "-Entries of previous forecast calculated will be considered"
                                           "-All of Pending Payable to Vendors or Pending Receivable from Customers "
                                           "from the Accounts that are selected in Accounts tab will be considered"
                                           "-Entries will be considered from Forecast Type that you select in Dependant"
                                           " Forecast Type tab")

    calculation_pattern = fields.Selection([('average', 'Average Value of Last X Days'),
                                            ('average_entries', 'Average Value of Last X Entries'),
                                            ('seasonal', 'Same Period Previous Year')],
                                           string="Calculation pattern",
                                           help="-Cash Forecast will be calculated by taking the Average value of the "
                                                "entries of option selected in Calculate from functionality for "
                                                "Number of days entered"
                                                "-Cash Forecast will be calculated by taking the Average value of the "
                                                "entries of option selected in Calculate from functionality for "
                                                "Number of Entries entered"
                                                "-Entries of same forecast period of previous year will be considered"
                                                "while calculating Cash Forecast")
    multiply_by = fields.Float(string="Multiply by",
                               help="This option allows you to increment the Forecast Value by percentage "
                                    "that you enter here."
                                    "For eg: To increment forecast value by 5% enter 0.05. To double the "
                                    "forecast value enter 2")
    average_value_of_days = fields.Integer(string="Number of days", default=90)
    number_of_period_months = fields.Integer(string='Number Of Periods', default=1)

    real_value_multiply_by = fields.Float(string='Real value multiply by',
                                          help="While calculating Real Value of this type, "
                                               "if valuation of account appears negative and "
                                               "you wish to display it positive then multiply it with -1")

    # past_period_type_id = fields.Many2one('setu.cash.forecast.type')

    # [Dipesh] create field for store kanban_dashboard_graph data
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')

    @api.model
    def create(self, vals):
        if not self._context.get('demo_data', False) and vals.get('type') in ['income', 'expense', 'opening'] and \
                not vals.get('account_ids', [(6, 0, [])])[0][2]:
            raise ValidationError(_("Please set proper account in cash forecast type"))
        return super(SetuCashForecastType, self).create(vals)

    def write(self, vals):
        res = super(SetuCashForecastType, self).write(vals)
        for rec in self:
            if not self._context.get('demo_data', False) and not rec.account_ids and rec.type in ['income', 'expense', 'opening']:
                raise ValidationError(_("Please set proper account in cash forecast type"))
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(
            name=_("%s (copy)") % (self.name or ''))
        return super(SetuCashForecastType, self).copy(default)

    @api.constrains('multiply_by', 'average_value_of_days', 'number_of_period_months', 'calculate_from',
                    'calculation_pattern')
    # [Dipesh] getting cash forecast types and generate json data for chart
    def _kanban_dashboard_graph(self):
        for data in self:
            data.kanban_dashboard_graph = json.dumps(data.get_bar_graph_datas())

    # [Dipesh] method for generate json chart data
    def get_bar_graph_datas(self):
        record = self.env['setu.cash.forecast'].search([('forecast_type', '=', self.type), ('name', '=', self.name)])
        result = []
        for data in record:
            result.append(
                {'label': data.forecast_period_id.display_name, 'value': data.forecast_value, 'type': 'future'})
        data = [{'label': '21-27 Aug', 'value': 33337.5, 'type': ''}, ]
        if not result.__len__():
            return [{'values': data, 'title': "dummy"}]
        if all(d['value'] == 0.0 for d in result):
            return [{'values': data, 'title': "zero-dummy"}]
        else:
            return [{'values': result, 'title': "graph_title"}]

    # [Dipesh] Create action for open setu.cash.forecast.type form view when click on kanban view title
    def open_action(self):
        return {
            'name': _('Refund Orders'),
            'view_mode': 'form',
            'res_model': 'setu.cash.forecast.type',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    @api.onchange('cash_forecast_category_id')
    def _compute_group(self):
        self.type = self.cash_forecast_category_id.type

    def _check_numeric_field(self):
        if self.multiply_by < 0:
            raise ValidationError(_("Please Enter positive values For 'Multiply by'"))

        if self.calculate_from == 'past_period_forecasting_entries' and self.number_of_period_months <= 0 \
                or self.calculate_from in ['past_account_entries', 'past_sales'] and \
                self.calculation_pattern == 'average' and self.average_value_of_days <= 0:
            raise ValidationError(_("Please Enter greater then 0 values For "
                                    "'{}'".format(
                'Number Of Periods' if self.calculate_from == 'past_period_forecasting_entries'
                else 'Number of days')))
        return True

    @api.constrains('name', 'type', 'company_id')
    def _check_forecast_type(self):
        for record in self:
            if record.type in ['opening', 'closing']:
                duplicate_records = self.search([('id', '!=', record.id),
                                                 ('type', '=', record.type),
                                                 ('company_id', '=', record.company_id.id)])
            else:
                duplicate_records = self.search([('id', '!=', record.id),
                                                 ('name', '=', record.name),
                                                 ('company_id', '=', record.company_id.id)])
            if duplicate_records:
                raise ValidationError(_('Forecast type you want to create is duplicate'))

    @api.constrains('forecast_end_period', 'forecast_start_period')
    def _validate_dates(self):
        if self.forecast_start_period and self.forecast_end_period and \
                self.forecast_start_period.start_date > self.forecast_end_period.start_date:
            raise ValidationError(_('Please select valid period range.'))

    def _check_duplicates(self, forecast_period_id):
        return self.env['setu.cash.forecast'].search([('forecast_type_id', '=', self.id),
                                                      ('forecast_period_id', '=', forecast_period_id.id),
                                                      ('company_id', '=', self.company_id.id),
                                                      ('account_ids', 'in', self.account_ids.ids)])

    # @api.model
    # def create_default_forecast_type(self):
    #     companies = self.env['res.company'].sudo().search([])
    #     tag_obj = self.env['cash.forecast.tag']
    #     for company in companies:
    #         account_ids = self.env['account.account'].search([('company_id', '=', company.id),
    #                                                           ('account_type', '=', 'asset_cash')])
    #         opening_tag = tag_obj.create([{'name': 'Opening', 'company_id': company.id}])
    #         account_ids.cash_forecast_tag = opening_tag.id
    #         self.with_context(demo_data=True).create({'name': 'Opening Forecast',
    #                                                   'type': 'opening',
    #                                                   'forecasting_tag': opening_tag.id,
    #                                                   'cash_forecast_category_id': self.env.ref(
    #                                                       'setu_cash_flow_forecasting.cash_forecast_categories_opening').id,
    #                                                   'company_id': company.id,
    #                                                   'sequence': 0,
    #                                                   'account_ids': [(6, 0, account_ids.ids)]
    #                                                   })
    #
    #         self.with_context(demo_data=True).create({'name': 'Closing Forecast',
    #                                                   'type': 'closing',
    #                                                   'cash_forecast_category_id': self.env.ref(
    #                                                       'setu_cash_flow_forecasting.cash_forecast_categories_closing').id,
    #                                                   'company_id': company.id,
    #                                                   'sequence': 100,
    #                                                   # 'account_ids': [(6, 0, account_ids.ids)]
    #                                                   })
    #
    #         self.with_context(demo_data=True).create({'name': 'Net Forecast',
    #                                                   'type': 'net_forecast',
    #                                                   'cash_forecast_category_id': self.env.ref(
    #                                                       'setu_cash_flow_forecasting.cash_forecast_categories_net_forecasting').id,
    #                                                   'company_id': company.id,
    #                                                   'sequence': 99,
    #                                                   # 'account_ids': [(6, 0, account_ids.ids)]
    #                                                   })
    #
    #         pending_account = self.env['account.account'].search([('account_type', '=', 'asset_receivable'),
    #                                                               ('company_id', '=', company.id)])
    #         receivable_tag = tag_obj.create({'name': 'Receivable', 'company_id': company.id})
    #         pending_account.cash_forecast_tag = receivable_tag.id
    #         self.with_context(demo_data=True).create({'name': 'Pending Receivable',
    #                                                   'type': 'income',
    #                                                   'forecasting_tag': receivable_tag.id,
    #                                                   'calculate_from': 'pending',
    #                                                   'cash_forecast_category_id': self.env.ref(
    #                                                       'setu_cash_flow_forecasting.cash_forecast_categories_income').id,
    #                                                   'company_id': company.id,
    #                                                   'sequence': 1,
    #                                                   'account_ids': [(6, 0, pending_account.ids)]
    #                                                   })
    #
    #         payable_account = self.env['account.account'].search([('account_type', '=', 'liability_payable'),
    #                                                               ('company_id', '=', company.id)])
    #         payable_tag = tag_obj.create({'name': 'Payable', 'company_id': company.id})
    #         payable_account.cash_forecast_tag = payable_tag.id
    #         self.with_context(demo_data=True).create({'name': 'Pending Payable',
    #                                                   'type': 'expense',
    #                                                   'calculate_from': 'pending',
    #                                                   'forecasting_tag': payable_tag.id,
    #                                                   'cash_forecast_category_id': self.env.ref(
    #                                                       'setu_cash_flow_forecasting.cash_forecast_categories_expense').id,
    #                                                   'company_id': company.id,
    #                                                   'sequence': 2,
    #                                                   'account_ids': [(6, 0, payable_account.ids)]
    #                                                   })
    #         return True

    def approve_forecast_type(self, forecast_period_id):
        flag = False
        if self.type in ['closing', 'opening', 'net_forecast'] or self.calculate_from == 'pending':
            flag = True
        elif self.is_recurring:
            if self.forecast_start_period and self.forecast_start_period.start_date <= forecast_period_id.start_date:
                recurring_date = self.forecast_start_period.start_date
                period_list = [self.forecast_start_period.id]
                while recurring_date < forecast_period_id.start_date:
                    recurring_date = recurring_date + relativedelta(**{forecast_period_id.period_interval:
                                                                           self.recurring_duration_interval})
                    recurring_period = forecast_period_id.search([('start_date', '<=', recurring_date),
                                                                  ('end_date', '>=', recurring_date),
                                                                  ('company_id', '=', forecast_period_id.company_id.id)])

                    period_list.append(recurring_period.id)
                if forecast_period_id.id in period_list:
                    if self.forecast_end_period:
                        if self.forecast_end_period.start_date >= forecast_period_id.start_date:
                            flag = True
                    else:
                        flag = True
        elif forecast_period_id.id == self.forecast_start_period.id:
            flag = True
        return flag

    def _get_opening_balance(self, forecast_period_id):
        prev_period_id = self.env['cash.forecast.fiscal.period'].search(
            [('end_date', '=', forecast_period_id.start_date - timedelta(days=1)),
              ('company_id', '=', forecast_period_id.company_id.id)])
        if previous_cash_forecast := self.env['setu.cash.forecast'].search(
                [('forecast_type', '=', 'closing'), ('forecast_period_id', '=', prev_period_id.id)], limit=1):
            balance = previous_cash_forecast.forecast_value
        else:
            query = """
                select
                    sum(aml.debit)-sum(aml.credit) as balance
                from
                    account_move_line aml
                    join account_move am on am.id = aml.move_id
                where
                    am.state = 'posted' and
                    aml.date < '{}' and aml.account_id {} {}
            """.format(forecast_period_id.start_date,
                       'in' if len(self.account_ids.ids) > 1 else '=',
                       tuple(self.account_ids.ids) if len(self.account_ids.ids) > 1 else self.account_ids.id)
            self._cr.execute(query)
            balance = self._cr.fetchall()[0][0]
        return balance or 0

    def _get_closing_forecast_value(self, forecast_period_id):
        current_period_forecasts = self.env['setu.cash.forecast'].search(
            [('forecast_period_id', '=', forecast_period_id.id)])

        period_opening = sum(current_period_forecasts.filtered(
            lambda frc: frc.forecast_type == 'opening').mapped('forecast_value'))
        period_income = sum(current_period_forecasts.filtered(
            lambda frc: frc.forecast_type == 'income').mapped('forecast_value'))
        period_expense = sum(current_period_forecasts.filtered(
            lambda frc: frc.forecast_type == 'expense').mapped('forecast_value'))

        return period_opening + period_income - period_expense

    def get_calculation_days(self, forecast_period_id):
        if self.calculation_pattern == 'average':
            start_date = date.today() - timedelta(days=self.average_value_of_days)
            end_date = date.today()
            days = self.average_value_of_days
        else:
            start_date = datetime.combine(forecast_period_id.start_date - relativedelta(years=1), datetime.min.time())
            end_date = datetime.combine(forecast_period_id.end_date - relativedelta(years=1), datetime.max.time())
            days = (end_date - start_date).days + 1
        return start_date, end_date, days

    def _get_past_account_entries_forecast_value(self, forecast_period_id):
        account_move_line_obj = self.env['account.move.line']
        period_days = (forecast_period_id.end_date - forecast_period_id.start_date
                       ).days + 1 if self.calculation_pattern != 'average_entries' else 1

        domain = [('company_id', '=', self.company_id.id),
                  ('move_id.state', 'not in', ['draft', 'cancel']),
                  ('account_id', 'in', self.account_ids.ids)]

        if self.calculation_pattern == 'average_entries':
            move_line = account_move_line_obj.search(domain, order='date desc', limit=self.average_value_of_days)
            days = self.average_value_of_days

        else:
            start_date, end_date, days = self.get_calculation_days(forecast_period_id)
            domain += [('date', '>=', start_date), ('date', '<=', end_date)]
            move_line = account_move_line_obj.search(domain)

        credited_line = move_line.filtered(lambda line: line.account_id.internal_group in ['income'])
        credited_amount = sum(credited_line.mapped('credit')) - sum(credited_line.mapped('debit'))

        debited_line = move_line.filtered(lambda line: line.account_id.internal_group in ['expense', 'liability', 'asset'])
        debited_amount = sum(debited_line.mapped('debit')) - sum(debited_line.mapped('credit'))

        return ((credited_amount + debited_amount) / days) * period_days

    def _get_past_analytic_account_entries_forecast_value(self, forecast_period_id):
        analytic_line_obj = self.env['account.analytic.line']
        period_days = (forecast_period_id.end_date - forecast_period_id.start_date
                       ).days + 1 if self.calculation_pattern != 'average_entries' else 1

        domain = [('account_id', '=', self.analytic_account_id.id),
                  ('general_account_id', 'in', self.account_ids.ids),
                  ('company_id', '=', self.company_id.id)]

        if self.calculation_pattern == 'average_entries':
            analytic_line = analytic_line_obj.search(domain, order='date desc', limit=self.average_value_of_days)
            days = self.average_value_of_days
        else:
            date_from, date_to, days = self.get_calculation_days(forecast_period_id)
            domain += [('date', '>=', date_from),
                        ('date', '<=', date_to)]

            analytic_line = analytic_line_obj.search(domain)
        return (sum(analytic_line.mapped('amount')) / days) * period_days

    def _get_net_forecast_value(self, forecast_period_id):
        current_period_forecasts = self.env['setu.cash.forecast'].search([
            ('forecast_period_id', '=', forecast_period_id.id),
            ('forecast_type', 'not in', ['opening', 'closing'])])

        period_income = sum(current_period_forecasts.filtered(
            lambda frc: frc.forecast_type == 'income').mapped('forecast_value'))
        period_expense = sum(current_period_forecasts.filtered(
            lambda frc: frc.forecast_type == 'expense').mapped('forecast_value'))

        return period_income - period_expense

    def _get_past_sale_forecast_value(self, forecast_period_id):
        period_days = (forecast_period_id.end_date - forecast_period_id.start_date).days + 1
        start_date, end_date, days = self.get_calculation_days(forecast_period_id)
        return (sum(past_sales.mapped('amount_total')) / days) * period_days if (
            past_sales := self.env['sale.order'].search(
                [('company_id', '=', self.company_id.id), ('state', 'in', ['sale', 'done']),
                 ('date_order', '>=', start_date), ('date_order', '<=', end_date)])) else 0

    def _get_past_period_forecasting_entries_value(self, forecast_period_id):
        no_of_periods = self.number_of_period_months or 1
        past_periods_avg = self.env['setu.cash.forecast'].search([('forecast_period_id', '!=', forecast_period_id.id),
                                                                  ('forecast_type_id', '=', self.id),
                                                                  ('forecast_period_id.start_date', '>=',
                                                                   forecast_period_id.start_date - relativedelta(
                                                                       months=no_of_periods))])
        forecast_value = sum(past_periods_avg.mapped('forecast_value')) / no_of_periods
        return forecast_value or 0

    def _get_pending_forecast_value(self, forecast_period_id):
        prev_period_id = self.env['cash.forecast.fiscal.period'].search([
            ('end_date', '=', forecast_period_id.start_date - timedelta(days=1)),
            ('company_id', '=', forecast_period_id.company_id.id)])

        previous_forecast = self.env['setu.cash.forecast'].search([('forecast_type_id.calculate_from', '=', 'pending'),
                                                                   ('forecast_period_id', '=', prev_period_id.id)],
                                                                  limit=1)
        #
        domain = [('move_id.payment_state', '!=', 'paid'),
                  ('move_id.state', 'not in', ['draft', 'cancel']),
                  ('company_id', '=', self.company_id.id),
                  ('account_id', 'in', self.account_ids.ids)]

        if previous_forecast:
            domain.append(('move_id.invoice_date_due', '>=', forecast_period_id.start_date))
        domain.append(('move_id.invoice_date_due', '<=', forecast_period_id.end_date))

        pending_move_line = self.env['account.move.line'].search(domain)
        pending_move = pending_move_line.mapped('move_id')
        pending_invoice = pending_move.filtered(lambda x: x.move_type in ['out_invoice', 'in_invoice'])
        pending_refund = pending_move.filtered(lambda x: x.move_type in ['out_refund', 'in_refund'])
        return sum(pending_invoice.mapped('amount_residual_signed')) - sum(
            pending_refund.mapped('amount_residual_signed'))
        # return sum(pending_invoice.mapped('amount_total')) - sum(
        #     pending_refund.mapped('amount_total'))

    def _get_dependant_forecast_value(self, forecast_period_id):
        dep_forecast_ids = self.env['setu.cash.forecast'].search([('forecast_type_id', 'in', self.dep_forecast_ids.ids),
                                                                  ('forecast_period_id', '=', forecast_period_id.id)])
        dep_forecast_income = sum(dep_forecast_ids.filtered(lambda frc: frc.forecast_type == 'income'
                                                            ).mapped('forecast_value'))
        dep_forecast_expense = sum(dep_forecast_ids.filtered(lambda frc: frc.forecast_type == 'expense'
                                                             ).mapped('forecast_value'))

        return abs(dep_forecast_income - dep_forecast_expense)

    def _get_forecast_value(self, forecast_period_id):
        forecast_value = 0
        calculation_method = self.calculate_from

        if self.cash_forecast_category_id.is_group_for_opening:
            forecast_value = self._get_opening_balance(forecast_period_id)

        elif self.type == 'closing':
            forecast_value = self._get_closing_forecast_value(forecast_period_id)

        elif self.type == 'net_forecast':
            forecast_value = self._get_net_forecast_value(forecast_period_id)

        elif calculation_method == 'pending':
            forecast_value = self._get_pending_forecast_value(forecast_period_id)

        elif not self.auto_calculate:
            forecast_value = self.fixed_value or 0.0

        elif calculation_method == 'past_sales':
            forecast_value = self._get_past_sale_forecast_value(forecast_period_id)

        elif calculation_method == 'past_account_entries':
            if self.analytic_account_id:
                forecast_value = self._get_past_analytic_account_entries_forecast_value(forecast_period_id)
            else:
                forecast_value = self._get_past_account_entries_forecast_value(forecast_period_id)

        elif calculation_method == 'past_period_forecasting_entries':
            forecast_value = self._get_past_period_forecasting_entries_value(forecast_period_id)

        elif calculation_method == 'dependant':
            forecast_value = self._get_dependant_forecast_value(forecast_period_id)

        if self.multiply_by and self.type not in ['opening', 'net_forecast', 'closing']:
            forecast_value *= self.multiply_by
        return round(forecast_value)
