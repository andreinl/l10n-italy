# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_stamp_product_id = fields.Many2one(
        'product.product', 'Tax Stamp Product',
        help="Product used as Tax Stamp in customer invoices."
    )


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    tax_stamp_product_id = fields.Many2one(
        related='company_id.tax_stamp_product_id',
        string="Tax Stamp Product",
        help="Product used as Tax Stamp in customer invoices."
    )

    def default_get(self, cr, uid, fields, context=None):
        res = super(AccountConfigSettings, self).default_get(
            cr, uid, fields, context)
        if res:
            user = self.pool['res.users'].browse(cr, uid, uid, context)
            res['tax_stamp_product_id'] = \
                user.company_id.tax_stamp_product_id.id
        return res
