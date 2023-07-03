from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    keypay_secret_key = fields.Char("API Secret Key")
    keypay_secret_encoded = fields.Char("Basic Auth")

    # Location
    keypay_url_location = fields.Char("API Location URL")

    # Journal Entries
    keypay_journal_entries_url_get = fields.Char("API Journal Entries URL GET")

    # Timesheet
    keypay_url_timesheet = fields.Char("API Timesheet URL")

    # Approval
    keypay_url_manager = fields.Char("API Manager URL")

    # Work Type
    keypay_url_worktype = fields.Char("API Worktype URL")
