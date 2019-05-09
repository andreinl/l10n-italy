# -*- coding: utf-8 -*-
#
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    e_invoice_default_product_id = fields.Many2one(
        comodel_name='product.product',
        string='E-bill Default Product',
        help="Used by electronic invoice XML import. "
             "If filled in, generated bill lines will use this product when "
             "no other possible product is found."
    )
    e_invoice_default_account_id = fields.Many2one(
        comodel_name='account.account',
        string='E-bill Default Account',
        help="Used by electronic invoice XML import. "
             "If filled in, generated bill lines will use this account when "
             "no other possible product is found."
    )
    e_invoice_detail_level = fields.Selection([
        ('0', 'Minimum'),
        # ('1', 'Aliquote'),
        ('2', 'Maximum'),
    ], string="E-bills Detail Level",
        help="Minimum level: Bill is created with no lines; "
             "User will have to create them, according to what specified in "
             "the electronic bill.\n"
             # "Livello Aliquote: viene creata una riga fattura per ogni "
             # "aliquota presente nella fattura elettronica\n"
             "Maximum level: every line contained in the electronic bill "
             "will create a line in the bill.",
        default='2', required=True
    )
