# -*- coding: utf-8 -*-
# Copyright 2018 Sergio Corato (https://efatto.it)
# Copyright 2018 Enrico Ganzaroli (enrico.gz@gmail.com)
# Copyright 2018 Ermanno Gnan (ermannognan@gmail.com)
# Copyright 2018 Lorenzo Battistini (https://github.com/eLBati)
# Copyright 2018 Sergio Zanchetta (https://github.com/primes2h)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Italian Localization - Tax Stamp',
    'version': '8.0.1.0.1',
    'category': 'Localization/Italy',
    'summary': 'Tax stamp automatic management',
    'author': 'Ermanno Gnan, Sergio Corato, Enrico Ganzaroli, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/l10n-italy',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'account',
        'l10n_it_einvoice_out',
    ],
    'data': [
        'data/data.xml',
        'views/invoice_view.xml',
        'views/product_view.xml',
        'views/company_view.xml',
    ],
    'installable': True,
}
