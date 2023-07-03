
{
    'name': 'Portcities Payroll Integration Employment Hero',
    'version': '16.0.1.0.1',
    'sequence': 1,
    'category': 'Services/Payroll/Timesheets',
    'summary': 'Keypay Payroll Integration',
    'description': """
        This module contains extended customization for keypay payroll integration. \n
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'images': [],
    'depends': [
        'hr_timesheet',
        'auth_oauth',
        'l10n_au_keypay',
    ],
    'data': [
        # Data
        'data/cron_actions.xml',
        'data/timesheet_data.xml',
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/res_company_views.xml',
        'views/employee_view.xml',
        'views/sync_keypay_log_views.xml',
        'views/account_analytic_view.xml',
        'views/project_task_work_type_views.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
