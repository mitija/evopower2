import logging
import base64
import requests

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SyncKeypay(models.Model):
    _name = 'sync.keypay'
    _description = 'Keypay Syncing Operations'

    def process_sync_keypay(self, action, payload):
        kp_id = False
        status = 'failed'
        url = message = status_code = ''
        try:
            response, url = self.sync_keypay(action, payload)
            status_code = str(response.status_code)
            if status_code.startswith('20'):
                status = 'success'
                if action != 'delete':
                    message = response.json()
                    kp_id = message.get('id')
        except Exception as e:
            message = e

        analytic_account_id = payload.pop('analytic_account_id', False)
        ts_id = payload.pop('ts_id', False)

        log_vals = {
            'payload': payload,
            'action': action,
            'url': url,
            'message': message,
            'status': status,
            'status_code': status_code,
            'ref_id': kp_id,
            'timesheet_id': ts_id,
            'analytic_account_id': analytic_account_id,
        }
        self.env['sync.keypay.log'].create(log_vals)
        return kp_id, status

    def sync_keypay(self, action, payload=None):
        action_split = action.split('-')
        object_type = action_split[0]
        action_type = action_split[1]
        kp_ref_id = payload.pop('kp_ref_id', False)
        url = getattr(self.env.user.company_id, f'keypay_url_{object_type}')
        if not url:
            raise UserError("The URL for Location Delete is not set")

        headers = self._prepare_api_header()

        if action_type == 'update':
            url = url + f'/{kp_ref_id}'
            response = requests.put(url, json=payload, headers=headers)
        elif action_type in ['create', 'approve', 'reject']:
            if action_type != 'create':
               employee_id = payload['employeeId']
               ts_id = payload['id']
               url = url.format(employeeId=employee_id, timesheetId=ts_id, action=action_type)
            response = requests.post(url, json=payload, headers=headers)
        else:
            url = url + f'/{kp_ref_id}'
            response = requests.delete(url, headers=headers)
        return response, url

    def _prepare_api_header(self):
        if not self.env.user.company_id.keypay_secret_key:
            return {}
        if self.env.user.company_id.keypay_secret_encoded:
            auth = self.env.user.company_id.keypay_secret_encoded
        else:
            auth = base64.urlsafe_b64encode(str((self.env.user.company_id.keypay_secret_key)).encode("utf-8")).decode('utf-8')
        if not auth:
            raise UserError("The Credential for Integration is not set (API Secret or Basic Auth)")

        return {
            'Authorization': 'Basic %s' % (auth)
        }

    def _cron_sync_keypay_worktype(self):
        url = self.env.user.company_id.keypay_url_worktype
        if not url:
            raise UserError("Please config the url for syncing Keypay WorkType in Company")
        status = status_code = message = ''
        try:
            headers = self._prepare_api_header()
            response = requests.get(url, headers=headers)
            status_code = str(response.status_code)
            if status_code.startswith('20'):
                status = 'success'
                message = response.json()
        except Exception as e:
            message = e

        worktype_vals = []
        worktype_env = self.env['project.task.work.type']
        list_kp_id = []
        for val in message:
            kp_id = val.get('id', False)
            list_kp_id.append(kp_id)
            kp_worktype_name = val.get('name', '')
            related_worktype = worktype_env.search([('kp_id', '=', kp_id)])
            if related_worktype:
                related_worktype.write({'name': kp_worktype_name})
            else:
                val_temp = {
                    'kp_id': kp_id,
                    'name': kp_worktype_name,
                }
                worktype_vals.append(val_temp)

        _logger.warning(f"\n\n ===== worktype_vals === {worktype_vals}")
        if worktype_vals:
            worktype_env.create(worktype_vals)
        deprecated_worktypes = worktype_env.search([('kp_id', 'not in', list_kp_id)])
        deprecated_worktypes.unlink()

        log_vals = {
            'payload': '',
            'action': 'worktype-sync',
            'url': url,
            'message': message,
            'status': status,
            'status_code': status_code,
        }

        self.env['sync.keypay.log'].create(log_vals)


class SyncKeypaylog(models.Model):
    _name = 'sync.keypay.log'
    _description = 'Log of Keypay Syncing'
    _order = "write_date desc, id desc"

    ref_id = fields.Integer()
    status = fields.Selection(selection=[('success', 'Success'), ('failed', 'Failed')], readonly=True, copy=False)
    action = fields.Selection(selection=[
        ('worktype-sync', 'KEYPAY SYNC - UPDATE WORKTYPE'),
        ('manager-approve', 'KEYPAY SYNC - APPROVE TIMESHEET'),
        ('manager-reject', 'KEYPAY SYNC - REJECT TIMESHEET'),
        ('location-create', 'KEYPAY SYNC - CREATE ANALYTIC'),
        ('timesheet-create', 'KEYPAY SYNC - CREATE TIMESHEET'),
        ('location-update', 'KEYPAY SYNC - UPDATE ANALYTIC'),
        ('timesheet-update', 'KEYPAY SYNC - UPDATE TIMESHEET'),
        ('location-delete', 'KEYPAY SYNC - DELETE ANALYTIC'),
        ('timesheet-delete', 'KEYPAY SYNC - DELETE TIMESHEET')], readonly=True, copy=False)
    url = fields.Char(readonly=True, copy=False)
    status_code = fields.Char(readonly=True, copy=False)
    payload = fields.Text(string="Request Message", readonly=True, copy=False)
    message = fields.Text(string="Reponse Message", readonly=True, copy=False)
    timesheet_id = fields.Many2one(comodel_name='account.analytic.line', readonly=True, copy=False)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', readonly=True, copy=False)
