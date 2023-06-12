from odoo import _, api, fields, models
import re
class EvoSaleOpportunity(models.Model):
    _inherit = 'crm.lead'
    _order = 'stage_id'

    product_ids = fields.One2many('crm.lead.product', 'lead_id', string='Products')
    installer = fields.Char(_("Installer"))
    chance_of_sale = fields.Float(string='Chance of Sale', compute='_compute_chance_of_sale')
    follow_up_comments = fields.Char(_("Last Follow Up Comments"))
    comments = fields.Char(_("Comments"), compute='_compute_comments')
    last_contact_date = fields.Date()
    weighted_nominal = fields.Integer(string='Weighted Nominal')
    system_all = fields.Char(_('System'), compute='_compute_system_string')
    solution_all = fields.Char(_('Solution'), compute='_compute_solution_string')
    nominal_value = fields.Integer(string='Nominal Value', compute='_nominal_value')
    weighted_forecast = fields.Integer(string='Weighted Forecast', compute='_weighted_forecast')

    power_kW_opportunity = fields.Integer(string='Power kW Opportunity', compute='_power_kW_opportunity')
    usable_kWh_opportunity = fields.Integer(string='Usable kWh Opportunity', compute='_usable_kWh_opportunity')
    
    kw_weighted_forecast = fields.Integer(string='kW Weighted Forecast', compute='_kw_weighted_forecast')
    kwh_weighted_forecast = fields.Integer(string='kWh Weighted Forecast', compute='_kwh_weighteed_forecast')

    lost_reason_name = fields.Char(related='lost_reason_id.display_name', string='Lost Reason Name')
    lost_feedback = fields.Html(
        'Lost Reason Detail', sanitize=True
    )

    @api.depends('probability')
    def _compute_chance_of_sale(self):
        for record in self:
            record.chance_of_sale = record.probability / 100

    @api.depends('product_ids')
    def _compute_system_string(self):
        for record in self:
            system = ''
            for product in record.product_ids:
                system += product.system + ' ; '
            record.system_all = system
        
    @api.depends('product_ids')
    def _compute_solution_string(self):
        for record in self:
            solution = ''
            for product in record.product_ids:
                solution += product.solution + ' ; '
            record.solution_all = solution

    @api.depends('expected_revenue', 'probability')
    def _weighted_forecast(self):
        for record in self:
            record.weighted_forecast = record.expected_revenue * record.chance_of_sale

    @api.depends('product_ids')
    def _power_kW_opportunity(self):
        for record in self:
            kw_oppor_total = 0
            for product in record.product_ids:
                kw_oppor_total += (product.power_kW_opportunity * product.quantity)
            record.power_kW_opportunity = kw_oppor_total

    @api.depends('product_ids')
    def _usable_kWh_opportunity(self):
        for record in self:
            kwh_oppor_total = 0
            for product in record.product_ids:
                kwh_oppor_total += (product.usable_kWh_product * product.quantity)
            record.usable_kWh_opportunity = kwh_oppor_total

    @api.depends('weighted_nominal', 'probability')
    def _nominal_value(self):
        for record in self:
            record.nominal_value = record.weighted_nominal * record.chance_of_sale
    
    @api.depends('product_ids', 'probability')
    def _kw_weighted_forecast(self):
        for record in self:
            record.kw_weighted_forecast = record.power_kW_opportunity * record.chance_of_sale

    @api.depends('product_ids', 'probability')
    def _kwh_weighteed_forecast(self):
        for record in self:
            record.kwh_weighted_forecast = record.usable_kWh_opportunity * record.chance_of_sale
    
    @api.depends('description')
    def _compute_comments(self):
        for record in self:
            if record.description is not None: 
                html_text = '' if not record.description else record.description
                record.comments = self._apply_html_regex(html_text) 

    def _apply_html_regex(self, html_text):
        html_pattern = "<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>"
        cleaned_description = re.sub(html_pattern, '', html_text)
        return cleaned_description


class EvoCrmProduct(models.Model):
    _name = "crm.lead.product"
    _description = 'Evo CRM Product'

    product_ids = fields.Many2one('product.template', string='Products')
    lead_id = fields.Many2one('crm.lead', string='Leads')
    company_currency = fields.Many2one(related='lead_id.company_currency', readonly=True, store=True)
    quantity = fields.Integer(_('Quantity'))
    power_kW_product = fields.Integer(_('Power kW Product'))
    usable_kWh_product = fields.Integer(_('Usable kWh Product'))

    system = fields.Char(related='product_ids.display_name')
    solution = fields.Char(related='product_ids.product_category')
    product_price = fields.Float(related='product_ids.list_price', string='Price', default=0.0, readonly=False, store=True)
    subtotal = fields.Integer(_('Subtotal'), compute='_count_subtotal')
    product_subtotal = fields.Integer(_('Product Subtotal'), compute='_count_product_subtotal')
    power_kW_opportunity = fields.Integer(string='Power kW Opportunity', compute='_power_kW_opportunity')
    usable_kWh_opportunity = fields.Integer(string='Usable kWh Opportunity', compute='_usable_kWh_opportunity')
    
    @api.depends('quantity', 'product_price')
    def _count_subtotal(self):
        for product in self:
            product.subtotal = product.quantity * product.product_price

    @api.depends('power_kW_opportunity', 'usable_kWh_opportunity')
    def _count_product_subtotal(self):
        for product in self:
            product.subtotal = product.power_kW_opportunity + product.usable_kWh_opportunity

    @api.depends('quantity', 'power_kW_product')
    def _power_kW_opportunity(self):
        for record in self:
            record.power_kW_opportunity = record.quantity * record.power_kW_product

    @api.depends('quantity', 'usable_kWh_product')
    def _usable_kWh_opportunity(self):
        for record in self:
            record.usable_kWh_opportunity = record.quantity * record.usable_kWh_product

