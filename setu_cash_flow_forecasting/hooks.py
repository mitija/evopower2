from odoo import api, SUPERUSER_ID
from odoo.exceptions import ValidationError


def create_cash_forecast_type(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].sudo().search([])
    tag_obj = env['cash.forecast.tag']
    cash_forecast_type = env['setu.cash.forecast.type']

    for company in companies:
        account_ids = env['account.account'].search([('company_id', '=', company.id),
                                                     ('account_type', '=', 'asset_cash')])
        if not account_ids:
            raise ValidationError('Please configure first chart of account for your company')
        opening_tag = tag_obj.create([{'name': 'Opening', 'company_id': company.id}])
        account_ids.cash_forecast_tag = opening_tag.id
        cash_forecast_type.with_context(demo_data=True).create({'name': 'Opening Forecast',
                                                                'type': 'opening',
                                                                'forecasting_tag': opening_tag.id,
                                                                'cash_forecast_category_id': env.ref(
                                                                    'setu_cash_flow_forecasting.cash_forecast_categories_opening').id,
                                                                'company_id': company.id,
                                                                'sequence': 0,
                                                                'account_ids': [(6, 0, account_ids.ids)]
                                                                })

        cash_forecast_type.with_context(demo_data=True).create({'name': 'Closing Forecast',
                                                                'type': 'closing',
                                                                'cash_forecast_category_id': env.ref(
                                                                    'setu_cash_flow_forecasting.cash_forecast_categories_closing').id,
                                                                'company_id': company.id,
                                                                'sequence': 100,
                                                                # 'account_ids': [(6, 0, account_ids.ids)]
                                                                })

        cash_forecast_type.with_context(demo_data=True).create({'name': 'Net Forecast',
                                                                'type': 'net_forecast',
                                                                'cash_forecast_category_id': env.ref(
                                                                    'setu_cash_flow_forecasting.cash_forecast_categories_net_forecasting').id,
                                                                'company_id': company.id,
                                                                'sequence': 99,
                                                                # 'account_ids': [(6, 0, account_ids.ids)]
                                                                })

        pending_account = env['account.account'].search([('account_type', '=', 'asset_receivable'),
                                                              ('company_id', '=', company.id)])
        if not pending_account:
            raise ValidationError('Please configure first chart of account for your company')
        
        receivable_tag = tag_obj.create({'name': 'Receivable', 'company_id': company.id})
        pending_account.cash_forecast_tag = receivable_tag.id
        cash_forecast_type.with_context(demo_data=True).create({'name': 'Pending Receivable',
                                                                'type': 'income',
                                                                'forecasting_tag': receivable_tag.id,
                                                                'calculate_from': 'pending',
                                                                'cash_forecast_category_id': env.ref(
                                                                    'setu_cash_flow_forecasting.cash_forecast_categories_income').id,
                                                                'company_id': company.id,
                                                                'sequence': 1,
                                                                'account_ids': [(6, 0, pending_account.ids)]
                                                                })

        payable_account = env['account.account'].search([('account_type', '=', 'liability_payable'),
                                                              ('company_id', '=', company.id)])
        if not payable_account:
            raise ValidationError('Please configure first chart of account for your company')
        payable_tag = tag_obj.create({'name': 'Payable', 'company_id': company.id})
        payable_account.cash_forecast_tag = payable_tag.id
        cash_forecast_type.with_context(demo_data=True).create({'name': 'Pending Payable',
                                                                'type': 'expense',
                                                                'calculate_from': 'pending',
                                                                'forecasting_tag': payable_tag.id,
                                                                'cash_forecast_category_id': env.ref(
                                                                    'setu_cash_flow_forecasting.cash_forecast_categories_expense').id,
                                                                'company_id': company.id,
                                                                'sequence': 2,
                                                                'multiply_by': -1,
                                                                'account_ids': [(6, 0, payable_account.ids)]
                                                                })
    return True
