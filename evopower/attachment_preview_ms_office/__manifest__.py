

{
    'name': 'MS Office Attachment Preview',
    'version': '16.0.1.0.0',
    'sequence': 1,
    'category': 'Tools',
    'summary': 'MS Office Attachment Preview',
    'description': """
        MS Office Attachment Preview
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'images': [],
    'depends': ['mail', 'web'],
    'assets': {
        'mail.assets_messaging': [
            '/attachment_preview_ms_office/static/src/js/*.js',
        ],
        'mail.assets_discuss_public': [
            '/attachment_preview_ms_office/static/src/xml/preview_ms_office.xml',
        ],
        'web.assets_backend': [
            '/attachment_preview_ms_office/static/src/xml/preview_ms_office.xml',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
