from odoo import api, fields, models, _


class EvoProduct(models.Model):
    _inherit = "product.template"
    
    product_category = fields.Char(related='categ_id.display_name', string='Solution')

