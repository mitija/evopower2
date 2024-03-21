from odoo import api, fields, models
from odoo.http import request

MS_MIMETYPE = ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
               'application/msword',
               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
               'application/vnd.ms-excel',
               'application/vnd.openxmlformats-officedocument.presentationml.presentation',
               'application/vnd.ms-powerpoint']


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super().create(vals_list)
        attachments.filtered(lambda att: att.mimetype in MS_MIMETYPE).generate_access_token()
        return attachments

    def _attachment_format(self, legacy=False):
        safari = request and request.httprequest.user_agent and request.httprequest.user_agent.browser == 'safari'
        res_list = []
        attachments = self.filtered(lambda att: att.mimetype in MS_MIMETYPE)
        if attachments:
            attachments.with_context(
                bypass_check_access=True).generate_access_token()
        for attachment in self:
            res = {
                'access_token': attachment.access_token,
                'checksum': attachment.checksum,
                'id': attachment.id,
                'filename': attachment.name,
                'name': attachment.name,
                'mimetype': 'application/octet-stream' if safari and attachment.mimetype and 'video' in attachment.mimetype else attachment.mimetype,
            }
            if not legacy:
                res['originThread'] = [('insert', {
                    'id': attachment.res_id,
                    'model': attachment.res_model,
                })]
            else:
                res.update({
                    'res_id': attachment.res_id,
                    'res_model': attachment.res_model,
                })
            res_list.append(res)
        return res_list
