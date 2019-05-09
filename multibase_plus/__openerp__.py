# -*- coding: utf-8 -*-
# Copyright 2016-18 Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
# License AGPL-30 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'multibase_plus',
    'summary': 'Enhanced Odoo Features',
    'version': '8.0.0.1.2',
    'category': 'Base',
    'author': 'SHS-AV s.r.l.',
    'website': 'https://www.zeroincombenze.it/',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'purchase',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/purchase_order_view.xml'
    ],
    'installable': True,
}
