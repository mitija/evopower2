from odoo import models, fields


class ProjectTaskWorkType(models.Model):
    _name = 'project.task.work.type'
    _description = 'Work Type for Task'

    sequence = fields.Integer("Sequence")
    name = fields.Char()
    kp_id = fields.Integer()
