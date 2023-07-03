# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Cash Forecasting',
    'version': '16.2.0',
    'price' : 279,
    'currency' :'EUR',
    'category': 'Accounting/Accounting',
    'summary': """ 
        The cash Forecast solution calculates and allows end users to know the available cash 
        in the upcoming future considering the Opening balance, all cash receipts, and all cash expenditures.
        cash forecasting, cash flow forecasting, cash in, cash out, expense, forecast budget, liquidity risk management,
        cash needs, inflow, outflow, payment, in payment, out payment, chart of accounts, forecast finance, forecast cash flow,
        net income, depreciation, inventory, receivable, payable, fixed asset, opening balance, closing balance,
        income, expenses, net forecast, total cash in, total cash out, opening forecast, closing forecast, recurring forecast, real forecast,
        cash forecast analysis, treasure, cash analytic, advance cash planning, cash capital, cashin, cashout,
        treasury analysis, cashflow management, cash flow management,  
        """,
    'description': """
        The cash Forecast solution calculates and allows end users to know the available cash 
        in the upcoming future considering the Opening balance, all cash receipts, and all cash expenditures. 
        Also, various statistical and analytical reports allow users to have a complete insight into 
        all income and expenditures for each period.
    """,
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'images': ['static/description/banner.gif'],
    'depends': ['account', 'sale'],
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'license': 'OPL-1',
    'sequence': 20,
    'data': [
    	'security/security.xml',
        'security/ir.model.access.csv',
        'views/setu_cash_forecast_group.xml',
        'views/setu_cash_forecast_type.xml',
        'views/cash_forecast_tag.xml',
        # 'views/setu_cash_forecast_calculation.xml',
        'views/cash_forecast_fiscal_year.xml',
        'views/setu_cash_forecast_dashboard_menu.xml',
        'views/create_update_cash_forecast.xml',
        'views/setu_cash_forecast.xml',
        'views/setu_cash_forecast_report_view.xml',
        'views/account_account_view.xml',
        'views/cash_onboarding_templates.xml',
        'data/setu_cash_forecast_actual_value_cron.xml',
        'data/demo_data.xml'
        ],
    'assets': {
        'web.assets_backend': [
                'setu_cash_flow_forecasting/static/src/js/setu_kanban_chart.js',
                'setu_cash_flow_forecasting/static/src/js/get_rule.js',
                'setu_cash_flow_forecasting/static/src/js/setu_cash_forecasting_dashboard.js',
                'setu_cash_flow_forecasting/static/src/scss/main.scss',
                'setu_cash_flow_forecasting/static/src/js/pivot.js',
                'setu_cash_flow_forecasting/static/src/xml/**/*',
            ],
    },
    'application': True,
    'post_init_hook': 'create_cash_forecast_type',
    'live_test_url' : 'https://www.youtube.com/playlist?list=PLH6xCEY0yCIB-k1yPvSZHhZEsqVYE0evq',
}
