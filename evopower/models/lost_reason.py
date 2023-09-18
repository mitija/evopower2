from odoo import models, _

class LostReason(models.TransientModel):
  _inherit = 'crm.lead.lost'
  _description = 'Get Lost Reason'


  def action_lost_reason_apply(self):
    self.ensure_one()
    leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
    res = super(EvoLostReason, self).action_lost_reason_apply()
    res = leads.action_set_lost(lost_reason_id=self.lost_reason_id.id, lost_feedback = self.lost_feedback)
    return res
