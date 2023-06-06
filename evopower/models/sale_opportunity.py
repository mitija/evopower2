from odoo import api, fields, models, _

class EvoSaleOpportunity(models.Model):
    _inherit = 'crm.lead'
    _order = 'stage_id'

    product_ids = fields.Many2one('product.template', string='Product')
    installer = fields.Char(_("Installer"))
    chance_of_sale = fields.Float(string='Chance of Sale', compute='_compute_chance_of_sale')
    follow_up_comments = fields.Char(_("Last Follow Up Comments"))
    last_contact_date = fields.Date()
    quantity = fields.Integer(_("Quantity"))
    power_kW_product = fields.Integer(string='Power kW Product')
    usable_kWh_product = fields.Integer(string='Usable kWh Product')

    system = fields.Char(related='product_ids.display_name')
    solution = fields.Char(related='product_ids.product_category')

    weighted_forecast = fields.Integer(string='Weighted Forecast', compute='_weighted_forecast')
    power_kW_opportunity = fields.Integer(string='Power kW Opportunity', compute='_power_kW_opportunity')
    usable_kWh_opportunity = fields.Integer(string='Usable kWh Opportunity', compute='_usable_kWh_opportunity')

    kw_weighted_forecast = fields.Integer(string='kW Weighted Forecast', compute='_kw_weighted_forecast')
    kwh_weighted_forecast = fields.Integer(string='kWh Weighted Forecast', compute='_kwh_weighteed_forecast')

    lost_reason_name = fields.Char(related='lost_reason_id.display_name', string='Lost Reason Name')
    lost_feedback = fields.Html(
        'Lost Reason Detail', sanitize=True
    )

    @api.onchange('product_ids')
    def _onchange_product_id(self):
        if self.product_ids:
            self.name = self.product_ids.name

    @api.depends('probability')
    def _compute_chance_of_sale(self):
        for record in self:
            record.chance_of_sale = record.probability / 100

    @api.depends('expected_revenue', 'probability')
    def _weighted_forecast(self):
        for record in self:
            record.weighted_forecast = record.expected_revenue * record.chance_of_sale

    @api.depends('quantity', 'power_kW_product')
    def _power_kW_opportunity(self):
        for record in self:
            record.power_kW_opportunity = record.quantity * record.power_kW_product

    @api.depends('quantity', 'usable_kWh_product')
    def _usable_kWh_opportunity(self):
        for record in self:
            record.usable_kWh_opportunity = record.quantity * record.usable_kWh_product
    
    @api.depends('power_kW_opportunity', 'probability')
    def _kw_weighted_forecast(self):
        for record in self:
            record.kw_weighted_forecast = record.power_kW_opportunity * record.chance_of_sale

    @api.depends('usable_kWh_opportunity', 'probability')
    def _kwh_weighteed_forecast(self):
        for record in self:
            record.kwh_weighted_forecast = record.usable_kWh_opportunity * record.chance_of_sale