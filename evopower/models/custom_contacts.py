from odoo import api, fields, models, _

class ChannelGroup(models.Model):
    _name = 'channel.group'

    name = fields.Char()


class MarketMap(models.Model):
    _name = 'market.map'

    name = fields.Char()


class PartnerInstaller(models.Model):
    _name = 'partner.installer'

    name = fields.Char()


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    channel_group_id = fields.Many2one('channel.group', string='Channel Group')
    market_map = fields.Many2one('market.map', string='Market Map')
    close_date = fields.Date(string='Close Date')
    company_domain_name = fields.Char(string='Company Domain Name')
    create_date = fields.Datetime(string='Create Date')
    description = fields.Text(string='Description')
    last_activity_date = fields.Datetime(string='Last Activity Date')
    linkedin_bio = fields.Text(string='LinkedIn Bio')
    linkedin_company_page = fields.Char(string='LinkedIn Company Page')
    parent_company_id = fields.Many2one('res.partner', string='Parent Company')
    child_company_id = fields.One2many('res.partner','parent_company_id', string='Child Company')
    last_contacted_date = fields.Datetime(string='Last Contacted Date')
    installer_id = fields.Many2one('partner.installer', string='Installer')
    user_created = fields.Many2one('hr.employee', string='Created by User')