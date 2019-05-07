# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Customer Wallet Management",
    "version" : "11.0.0.4",
    "category" : "Point of Sale",
    "depends" : ['base','sale','account','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'This apps helps manage customer wallet and allow recharge wallet for the customer',
    "description": """
    
    Purpose :- 
This Module allow the seller to recharge wallet for the customer. 
    POS Customer Wallet Management
    POS Wallet Management
    point of sale Wallet Management
    point of sales Wallet management
    Customer Wallet payment with POS
    Customer wallet POS
    customer credit POS
    POS customer credit payment    
    POS Customer Wallet payment Management
    POS Wallet payment Management
    point of sale Wallet payment Management
    point of sales Wallet payment management
    wallet on POs
    wallet on point of sale

    
    
    
    """,
    "website" : "www.browseinfo.in",
    "price": 55,
    "currency": "EUR",
    "data": [
        'security/ir.model.access.csv',
        'views/custom_pos_view.xml',
        'views/wallet.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
