{
    'name': 'Contact Card Custom',
    'summary': 'Contact Card Custom',
    'version': '1.0.2',
    'category': 'contact',
    'sequence': 1,
    'auther': 'Kiran Kantesariya',
    'depends': [
        'contacts', 'point_of_sale', 'account'
    ],
    'data': [
        'report/contact_report.xml',
        'data/mail.template.xml',
        'wizard/partner_email.xml',
        'wizard/send_journal_wiz_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}