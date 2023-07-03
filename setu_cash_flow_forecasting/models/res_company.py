from odoo import fields, models, api, _

ONBOARDING_STEP_STATES = [
    ('not_done', "Not done"),
    ('just_done', "Just done"),
    ('done', "Done"),
]
DASHBOARD_ONBOARDING_STATES = ONBOARDING_STEP_STATES + [('closed', 'Closed')]


class ResCompany(models.Model):
    _inherit = "res.company"

    cash_dashboard_onboarding_state = fields.Selection(DASHBOARD_ONBOARDING_STATES,
                                                       string="State of the Cash dashboard onboarding panel",
                                                       default='not_done')

    fiscal_year_setup_data_state = fields.Selection(ONBOARDING_STEP_STATES,
                                                    string="State of the onboarding Fiscal Year data step",
                                                    default='not_done')

    forecast_category_setup_data_state = fields.Selection(ONBOARDING_STEP_STATES,
                                                          string="State of the onboarding Forecast Category data step",
                                                          default='not_done')
    forecast_type_setup_data_state = fields.Selection(ONBOARDING_STEP_STATES,
                                                      string="State of the onboarding Forecast Type data step",
                                                      default='not_done')
    create_forecast_data_state = fields.Selection(ONBOARDING_STEP_STATES,
                                                  string="State of the onboarding Create Forecast data step",
                                                  default='not_done'
                                                  )

    def get_and_update_cash_dashboard_onboarding_state(self):
        """ This method is called on the controller rendering method and ensures that the animations
            are displayed only one time. """
        return self._get_and_update_onboarding_state(
            'cash_dashboard_onboarding_state',
            self.get_cash_dashboard_onboarding_steps_states_names()
        )

    def get_cash_dashboard_onboarding_steps_states_names(self):
        """ Necessary to add/edit steps from other modules (account_winbooks_import in this case). """
        return [
            'fiscal_year_setup_data_state',
            'forecast_category_setup_data_state',
            'forecast_type_setup_data_state',
            'create_forecast_data_state'
        ]

    @api.model
    def action_close_cash_forecasting_onboarding(self):
        self.env.company.cash_dashboard_onboarding_state = 'closed'

    @api.model
    def cash_setting_init_fiscal_year_action(self):
        company = self.env.company
        # new_wizard = self.env['cash.forecast.fiscal.year'].create({'company_id': company.id})
        view_id = self.env.ref('setu_cash_flow_forecasting.form_cash_forecast_fiscal_year').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Accounting Periods'),
            'view_mode': 'form',
            'res_model': 'cash.forecast.fiscal.year',
            'target': 'new',
            # 'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
        }

    @api.model
    def cash_setting_init_forecast_categories_action(self):
        view_id = self.env.ref('setu_cash_flow_forecasting.form_setu_cash_forecast_categories').id
        return {'type': 'ir.actions.act_window',
                'name': _('Create a Forecast Categories'),
                'res_model': 'setu.cash.forecast.categories',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                }

    @api.model
    def cash_setting_init_forecast_type_action(self):
        view_id = self.env.ref('setu_cash_flow_forecasting.form_setu_cash_forecast_type').id
        return {'type': 'ir.actions.act_window',
                'name': _('Create a Forecast Type'),
                'res_model': 'setu.cash.forecast.type',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                }
    
    @api.model
    def cash_setting_init_create_forecast_action(self):
        view_id = self.env.ref('setu_cash_flow_forecasting.form_create_update_cash_forecast').id
        return {'type': 'ir.actions.act_window',
                'name': _('Create a Cash Forecast'),
                'res_model': 'create.update.cash.forecast',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                }
