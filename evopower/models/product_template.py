from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_category = fields.Char(related="categ_id.display_name", string="Solution")
