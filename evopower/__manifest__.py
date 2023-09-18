{
  'name': "Customization for Evopower",
  'version': '1.0',
  'summary': 'Custom Module created for Evopower',
  'description': "EVO Power Application",
  'author': "Mplus Software",
  'website': "http://www.yourcompany.com",
  'depends': ['sale_crm', 'base','account'],  
  'data' : [
      'security/ir.model.access.csv',
      'views/evo_opportunity_report.xml',
      'views/evo_opportunity_form.xml',
      'views/evo_lost_reason.xml',
      'views/evo_filter_report.xml',
      'views/evo_kanban_ribbon.xml',
      'views/evo_custom_contacts.xml',
  ]
}

