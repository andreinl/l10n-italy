# -*- coding: utf-8 -*-
#
# Copyright 2014    - Davide Corio <davide.corio@lsweb.it>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class FatturaPAAttachment(models.Model):
    _name = "fatturapa.attachment.out"
    _description = "E-invoice Export File"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']

    @api.multi
    def _compute_invoice_data(self):
        for attachment_out in self:
            partners = self.env['res.partner']
            for invoice in attachment_out.out_invoice_ids:
                partner = invoice.partner_id
                if partner.id not in partners.ids:
                    partners += partner

            if len(partners) == 1:
                attachment_out.invoice_partner_id = partners[0].id

    @api.multi
    def _compute_invoice_numbers(self):
        for attachment_out in self:
            invoice_numbers = [invoice.number for invoice in attachment_out.out_invoice_ids]
            attachment_out.invoice_number = ', '.join(invoice_numbers)

    @api.multi
    def _compute_invoice_date(self):
        for attachment_out in self:
            invoice_dates = [invoice.date_invoice for invoice in attachment_out.out_invoice_ids]
            attachment_out.invoice_date = ', '.join(invoice_dates)

    ir_attachment_id = fields.Many2one(
        'ir.attachment', 'Attachment', required=True, ondelete="cascade")
    out_invoice_ids = fields.One2many(
        'account.invoice', 'fatturapa_attachment_out_id',
        string="Out Invoices", readonly=True)
    invoice_partner_id = fields.Many2one(
        'res.partner',
        compute=_compute_invoice_data,
        string='Customer',
        store=False,
        # relation=
    )
    invoice_number = fields.Char(
        compute=_compute_invoice_numbers,
        string='Number',
        store=False
    )
    invoice_date = fields.Date(
        compute=_compute_invoice_date,
        string='Date',
        store=False
    )
