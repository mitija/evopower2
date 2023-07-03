from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    keypay_employee_externalId = fields.Integer("Keypay Employee ID", groups="hr.group_hr_user")
