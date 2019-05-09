# -*- coding: utf-8 -*-
#
# Copyright 2014    - Davide Corio
# Copyright 2015-16 - Lorenzo Battistini - Agile Business Group
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    'name': 'Italian Localization - FatturaPA - Emission',
    'version': '8.0.3.2.2',
    'category': 'Localization/Italy',
    'summary': 'Electronic invoices emission',
    'author': 'Odoo Italia Associazione,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.odoo-italia.org',
    'license': 'AGPL-3',
    "depends": [
        'l10n_it_einvoice_base',
        'l10n_it_split_payment',
    ],
    "data": [
        'wizard/wizard_export_fatturapa_view.xml',
        'views/attachment_view.xml',
        'views/account_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'external_dependencies': {
        'python': ['unidecode'],
    }
}
