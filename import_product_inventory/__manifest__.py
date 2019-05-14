# -*- coding: utf-8 -*-

{'name': 'Import product in Batch',
 'version': '12.0.8.5.2019',
 'category': 'other',
 'depends': ['l10n_mx','l10n_mx_edi','sale_stock','purchase'],
 'author': "Terra Colligo",
 'license': 'OPL-1',
 'website': '',
 'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/cron.xml',
        'views/product_import_batch_view.xml',
        'views/product_cierries_import_batch_view.xml',
        'wizard/import_product_wizard_view.xml',
        'wizard/import_cierres_product_wizard_view.xml',
        'wizard/export_product_view.xml',
        ],
  "qweb": [
       "static/src/xml/base.xml",
        ],
 'installable': True,
 'application': True,
 }
