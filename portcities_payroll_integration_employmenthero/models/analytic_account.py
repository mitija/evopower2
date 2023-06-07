import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AnalyticAccountAccount(models.Model):
    _inherit = 'account.analytic.account'

    # Integration
    keypay_location_external_id = fields.Integer("Keypay Location External ID")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if not rec.keypay_location_external_id:
                rec.keypay_action_location('location-create')
        return res

    def write(self, vals):
        res = super().write(vals)
        sync_keypay_analytic = self._context.get('sync_keypay_analytic', False)
        for rec in self:
            if not sync_keypay_analytic:
                rec.keypay_action_location('location-update')
        return res

    def unlink(self):
        self.keypay_action_location('location-delete')
        return super().unlink()

    def keypay_action_location(self, action=None):
        payload = {
            "name": self.name,
            "isGlobal": True,
            'kp_ref_id': self.keypay_location_external_id,
            'analytic_account_id': self.id,
        }
        kp_id, status = self.env['sync.keypay'].process_sync_keypay(action, payload)
        if status == 'success':
            self.with_context(sync_keypay_analytic=True).update({'keypay_location_external_id': kp_id})


class AnalyticAccountLine(models.Model):
    _inherit = 'account.analytic.line'

    state = fields.Selection([
        ('open', 'Open'),
        ('to_approve', 'To Approve'),
        ('validated', 'Approved'),
        ('reject', 'Rejected'),
    ], default="open", required=True)
    time_start = fields.Float()
    time_stop = fields.Float()
    unit_amount = fields.Float()
    worktype_id = fields.Many2one('project.task.work.type')
    keypay_timesheet_external_id = fields.Integer("Keypay Timesheet External ID")
    is_sync_success = fields.Boolean('Keypay Sync', default=False)

    #
    # FUNCTIONAL FEATURES
    #
    @api.constrains('time_start', 'time_stop')
    def _validate_time_start_stop(self):
        for rec in self:
            if rec.time_start < 0 or rec.time_start > 24:
                raise ValidationError(_('Time Start must be in 0h - 24h'))
            if rec.time_stop < 0 or rec.time_stop > 24:
                raise ValidationError(_('Time Stop must be in 0h - 24h'))
            if rec.time_stop < rec.time_start:
                raise ValidationError(_('Time Stop must be after Time Start'))

    @api.onchange('time_start', 'time_stop')
    def _onchange_unit_amount(self):
        start = timedelta(hours=self.time_start)
        stop = timedelta(hours=self.time_stop)
        self.unit_amount = (stop - start).seconds / 3600

    def action_validate_timesheet(self):
        analytic_lines = self.filtered(lambda line: line.state in ['to_approve'])
        if not analytic_lines:
            raise UserError(_("There is no timesheet to validate."))
        analytic_lines.write({
            'state': 'validated'
        })
        return super().action_validate_timesheet()

    def action_invalidate_timesheet(self):
        '''
            action_invalidate_timesheet called for action server: 'Reset to Draft'
            xml_id: timesheet_grid.invalidate_timesheet_action
        '''
        self.write({
            "state": "open",
        })
        return super().action_invalidate_timesheet()

    def action_submit_timesheet(self):
        submit_line = self.filtered(lambda line: line.state in ['open'])
        if not submit_line:
            raise UserError(_("There is no timesheet to submit."))
        submit_line.write({
            "state": "to_approve",
        })
        return {}

    def action_reject_timesheet(self):
        reject_line = self.filtered(lambda line: line.state in ['to_approve', 'validated'])
        if not reject_line:
            raise UserError(_("There is no timesheet to reject."))
        reject_line.write({
            "state": "reject",
            "validated": True,
        })
        return {}

    #
    # KEYPAY SYNC INTEGRATION
    #
    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if not rec.keypay_timesheet_external_id:
                rec.keypay_action_timesheet('timesheet-create')
        return res

    def write(self, vals):
        res = super(AnalyticAccountLine, self).write(vals)
        sync_keypay_ts = self._context.get('sync_keypay_ts', False)
        for rec in self:
            if not sync_keypay_ts:
                rec.keypay_action_timesheet('timesheet-update')
                action = rec.state
                if action == 'validated':
                    action = 'approve'
                if action in ['reject', 'approve']:
                    rec.keypay_action_timesheet(f'manager-{action}')
        return res

    def unlink(self):
        for rec in self:
            rec.keypay_action_timesheet('timesheet-delete')
        return super(AnalyticAccountLine, self).unlink()

    def keypay_action_timesheet(self, action):
        payload = {
            "employeeId": self.employee_id.keypay_employee_externalId,
            "startTime": "%s %s" % (self.date.strftime('%Y-%m-%d'), str(timedelta(hours=self.time_start))),
            "endTime": "%s %s" % (self.date.strftime('%Y-%m-%d'), str(timedelta(hours=self.time_stop))),
            "locationId": self.account_id.keypay_location_external_id,
            "comments": self.name,
            'status': self.state,
            'workTypeId': self.worktype_id and self.worktype_id.kp_id or False,
            'id': self.keypay_timesheet_external_id,
            'kp_ref_id': self.keypay_timesheet_external_id,
            'ts_id': self.id,
        }
        kp_id, status = self.env['sync.keypay'].process_sync_keypay(
            action, payload)
        result_vals = {}
        if status == 'success':
            result_vals.update({
                'keypay_timesheet_external_id': kp_id,
                'is_sync_success': True,
            })
        else:
            result_vals.update({
                'is_sync_success': False,
            })
        self.with_context(sync_keypay_ts=True).update(result_vals)
