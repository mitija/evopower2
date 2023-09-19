{
  'name': "Customization for Evopower",
  'version': '1.0',
  'summary': 'Custom Module created for Evopower',
  'description': "EVO Power Application",
  'author': "Mplus Software",
  'website': "https://www.mplus.software/",
  'depends': ['sale_crm', 'base','account'],  
  'data' : [
      'security/ir.model.access.csv',
      'views/crm_lead_views.xml',
      'views/res_partner_views.xml',
      'views/sale_order_views.xml',
      'views/purchase_views.xml',
  ]
}

