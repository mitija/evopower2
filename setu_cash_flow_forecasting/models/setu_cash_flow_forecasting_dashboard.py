import calendar
from builtins import str
from odoo import fields, models, api
from collections import OrderedDict
from datetime import date, datetime, timedelta


class SetuCashFlowForecastingDashboard(models.Model):
    _name = 'setu.cash.flow.forecasting.dashboard'
    _description = 'Cash Forecast Dashboard'


    def get_calander_list(self):
        year = self.env['cash.forecast.fiscal.year'].search(
            [('start_date', '<=', date.today()), ('end_date', '>=', date.today()),('company_id', '=', self.env.company.id)], limit=1)
        month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        list_date = {}
        if year:
            # month_list = list(OrderedDict(((year.start_date + timedelta(_)).strftime(r"%b"), None) for _ in
            #                               range((year.end_date - year.start_date).days)).keys())
            if year.period_interval in ['days', 'weeks','months']:
                for x in month_list:
                    start_dt = datetime.strptime('%s-%s-01' % (year.start_date.year, month_list.index(x) + 1),
                                                 '%Y-%m-%d').date()
                    end_dt = datetime.strptime('%s-%s-%s' % (year.start_date.year, month_list.index(x) + 1,
                                                             calendar.monthrange(year.start_date.year,
                                                                                 month_list.index(x) + 1)[1]),
                                               '%Y-%m-%d').date()
                    list_date[x] = self.env['cash.forecast.fiscal.period'].search(
                        [('start_date', '>=', start_dt),
                         ('end_date', '<=', end_dt), ('company_id', '=', self.env.company.id)]).ids
        return month_list,list_date

    @api.model
    def get_dashboard_data(self, filter=False):
        final_result = []
        filter_start_date = date.today()
        filter_end_date = date.today()

        date_domain = [('start_date', '<=', date.today()), ('end_date', '>=', date.today()), ('company_id', '=', self.env.company.id)]
        # Currently There Is No Filter Applied
        if filter is not False:
            if filter[0].get('filter') == 'Current Fiscal Period':
                period = self.env['cash.forecast.fiscal.period'].search(date_domain)
                filter_start_date = period.start_date
                filter_end_date = period.end_date

            elif filter[0].get('filter') == 'Current Fiscal Year':
                period_year = self.env['cash.forecast.fiscal.year'].search(date_domain)
                filter_start_date = period_year.start_date
                filter_end_date = period_year.end_date

            elif filter[0].get('filter') == 'time_period':
                filter_end_date = datetime.strptime(filter[2].get('end_date'), '%Y-%m-%d').date()
                filter_start_date = datetime.strptime(filter[1].get('start_date'), '%Y-%m-%d').date()
        else:
            filter_start_date = self.env['cash.forecast.fiscal.year'].search(date_domain).start_date
            filter_end_date = self.env['cash.forecast.fiscal.year'].search(date_domain).end_date

        # ORM METHOD START
        if not filter_start_date and not filter_start_date:
            filter_start_date = datetime.now().date()
            filter_end_date = datetime.now().date()

        # Prepare Expense Line Card Chart Data
        expense_line_cart_chart = self.get_card_line_chart_data(search_domain="expense")

        # Prepare Income Line Card Chart Data
        income_line_cart_chart = self.get_card_line_chart_data(search_domain="income")

        # Prepare income vs expanse ratio bar chart data
        income_vs_expanse_ratio_chart = self.get_income_vs_expanse_ratio_bar_chart_data()

        # Prepare income vs expanse Value bar chart data
        income_vs_expanse_value_chart = self.get_income_vs_expanse_value_bar_chart_data()

        # Prepare expanse Bar Chart Data
        expanse_bar_chart_result = self.get_bar_chart_date(search_domain='expense', start_date=filter_start_date,
                                                           end_date=filter_end_date)

        # Prepare income Bar Chart Data
        income_bar_chart_result = self.get_bar_chart_date(search_domain='income', start_date=filter_start_date,
                                                          end_date=filter_end_date)

        # Prepare expanse Line Chart Data
        expanse_line_chart_result = self.get_line_chart_data(search_domain='expense')

        # Prepare income Line Chart Data
        income_line_chart_result = self.get_line_chart_data(search_domain='income')

        # ORM METHOD END
        table_data = {'table_data': 'dashboard_data'}
        final_result.append(table_data)

        chart_data = []
        chart_data = {'chart_data': chart_data}
        final_result.append(chart_data)

        expense_chart_data = {'expense_chart_data': expanse_bar_chart_result}
        final_result.append(expense_chart_data)

        final_expense_chart_data = []
        final_expense_chart_data.append(expanse_line_chart_result)

        income_chart_data = {'income_chart_data': income_bar_chart_result}
        final_result.append(income_chart_data)


        final_income_chart_data = []
        final_income_chart_data.append(income_line_chart_result)
        final_result.append(final_expense_chart_data)
        final_result.append(final_income_chart_data)

        final_result.append('final_expense_doughnut_chart_data')
        final_result.append('final_income_doughnut_chart_data')
        final_result.append('final_income_vs_income_doughnut_chart_data')

        # Prepare Fiscal Period Data
        # add comment for getting current fiscal year data
        # fiscal_data = self.env['cash.forecast.fiscal.period'].search([])
        fiscal_data = self.env['cash.forecast.fiscal.year'].search(
            [('start_date', '<', date.today()), ('end_date', '>', date.today()),('company_id', '=', self.env.company.id)]).fiscal_period_ids
        fiscal_period = []
        for data in fiscal_data:
            fiscal_period.append([data.code, data.start_date, data.end_date])
        final_result.append(fiscal_period)

        final_result.append(expense_line_cart_chart)
        final_result.append(income_line_cart_chart)
        final_result.append(self.env.company.currency_id.symbol)

        final_result.append(income_vs_expanse_value_chart)
        final_result.append(income_vs_expanse_ratio_chart)

        return final_result

    def get_bar_chart_date(self, search_domain, start_date, end_date):
        income_types = self.env['setu.cash.forecast.type'].search([('type', '=', search_domain), ('company_id', '=', self.env.company.id)])
        income_list_data = []
        for type_record in income_types:
            data = {}
            data_case = self.env['setu.cash.forecast'].search([('forecast_type_id', '=', type_record.id), ('company_id', '=', self.env.company.id)]).filtered(
                lambda
                    f: f.forecast_period_id.start_date >= start_date and f.forecast_period_id.end_date <= end_date)
            if data_case:
                data['name'] = type_record.name
                data['forecast_value'] = sum(data_case.mapped('forecast_value'))
                data['real_value'] = sum(data_case.mapped('real_value'))
                income_list_data.append(data)
        return income_list_data

    def get_line_chart_data(self, search_domain):
        types = self.env['setu.cash.forecast.type'].search([('type', '=', search_domain), ('company_id', '=', self.env.company.id)])
        month_list, periods = self.get_calander_list()
        list_data = []
        for type_record in types:
            data = {}
            forecast_value_list = []
            data['name'] = type_record.name
            data['forecast_period'] = month_list
            for month_item in month_list:
                period_ids = periods.get(month_item)
                forecast_value = self.env['setu.cash.forecast'].search([('forecast_period_id', 'in', period_ids),('forecast_type_id', '=', type_record.id)]).mapped('forecast_value')
                forecast_value_list.append(sum(forecast_value))
                data['forecast_value'] = forecast_value_list
            list_data.append(data)
        return list_data

    # Done
    def get_card_line_chart_data(self,search_domain):
        month = []
        total = []
        data = {}
        month_list,periods = self.get_calander_list()
        for month_item in month_list:
            period_ids = periods.get(month_item)
            data = {}
            data_case = self.env['setu.cash.forecast'].search(
                [('forecast_period_id', 'in', period_ids), ('forecast_type', '=', search_domain), ('company_id', '=', self.env.company.id)])
            data['month'] = month.append(month_item)
            data['total'] = total.append(sum(data_case.mapped('forecast_value')))
        data['month'] = month
        if self.env.company.currency_id.position == "before":
            data['currency'] = [self.env.company.currency_id.symbol + "" + str(suit) for suit in total]
        else:
            data['currency'] = [str(suit) + "" + self.env.company.currency_id.symbol for suit in total]
        data['total'] = total
        return data

    # Done
    def get_income_vs_expanse_ratio_bar_chart_data(self):
        result = []
        month_list, periods = self.get_calander_list()

        for month_item in month_list:
            period_ids = periods.get(month_item)
            total_income = self.env['setu.cash.forecast'].search(
                [('forecast_period_id', 'in', period_ids), ('forecast_type', '=', 'income'), ('company_id', '=', self.env.company.id)]).mapped(
                'forecast_value')
            total_expanse = self.env['setu.cash.forecast'].search(
                [('forecast_period_id', 'in', period_ids), ('forecast_type', '=', 'expense'), ('company_id', '=', self.env.company.id)]).mapped(
                'forecast_value')
            result.append({month_item: round((sum(total_income) or 0) / (sum(total_expanse) or 1), 2)})
        return result

    # Done
    def get_income_vs_expanse_value_bar_chart_data(self):
        result = []
        month_list, periods = self.get_calander_list()

        for month_item in month_list:
            period_ids = periods.get(month_item)
            total_income = self.env['setu.cash.forecast'].search(
                [('forecast_period_id', 'in', period_ids), ('forecast_type', '=', 'income'), ('company_id', '=', self.env.company.id)]).mapped(
                'forecast_value')
            total_expanse = self.env['setu.cash.forecast'].search(
                [('forecast_period_id', 'in', period_ids), ('forecast_type', '=', 'expense'), ('company_id', '=', self.env.company.id)]).mapped(
                'forecast_value')
            result.append({month_item: [sum(total_income) or 0, sum(total_expanse) or 0]})

        return result
