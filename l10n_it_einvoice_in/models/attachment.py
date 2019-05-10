# -*- coding: utf-8 -*-
#
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError


class FatturaPAAttachmentIn(models.Model):
    _name = "fatturapa.attachment.in"
    _description = "E-bill import file"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']
    _order = 'id desc'

    ir_attachment_id = fields.Many2one(
        'ir.attachment', 'Attachment', required=True, ondelete="cascade")
    in_invoice_ids = fields.One2many(
        'account.invoice', 'fatturapa_attachment_in_id',
        string="In Bills", readonly=True)
    xml_supplier_id = fields.Many2one(
        "res.partner", string="Supplier", compute="_compute_xml_data",
        store=True)
    invoices_number = fields.Integer(
        "Bills Number", compute="_compute_xml_data", store=True)
    invoices_total = fields.Float(
        "Bills Total", compute="_compute_xml_data", store=True,
        help="If specified by supplier, total amount of the document net of "
             "any discount and including tax charged to the buyer/ordered"
    )
    registered = fields.Boolean(
        "Registered", compute="_compute_xml_data", store=True)
    uid = fields.Char('Uid', size=255)
    date_invoice0 = fields.Date(
        'Date Invoice', store=True,
        compute='_compute_xml_data')

    @api.onchange('datas_fname')
    def onchange_datas_fname(self):
        if self.search([('name', '=', self.datas_fname)]):
            raise UserError(
                    _("File %s already loaded!")
                    % self.datas_fname)
        self.name = self.datas_fname

    def get_xml_string(self):
        if self.ir_attachment_id:
            return self.ir_attachment_id.get_xml_string()
        return False

    @api.multi
    @api.depends('ir_attachment_id.datas', 'in_invoice_ids')
    def _compute_xml_data(self):
        wizard_model = self.env['wizard.import.fatturapa']
        for att in self:
            fatt = wizard_model.get_invoice_obj(att)
            if not fatt:
                continue
            cedentePrestatore = fatt.FatturaElettronicaHeader.CedentePrestatore
            partner_id = wizard_model.getCedPrest(cedentePrestatore)
            att.xml_supplier_id = partner_id
            att.invoices_number = len(fatt.FatturaElettronicaBody)
            att.registered = False
            if att.in_invoice_ids:
                att.date_invoice0 = att.in_invoice_ids[0].date_invoice
                if len(att.in_invoice_ids) == att.invoices_number:
                    att.registered = True
            att.invoices_total = 0
            for invoice_body in fatt.FatturaElettronicaBody:
                att.invoices_total += float(
                    invoice_body.DatiGenerali.DatiGeneraliDocumento.
                    ImportoTotaleDocumento or 0
                )
                if not att.in_invoice_ids:
                    att.date_invoice0 = invoice_body.\
                        DatiGenerali.DatiGeneraliDocumento.Data

    @api.multi
    @api.depends('ir_attachment_id.datas', 'in_invoice_ids')
    def revaluate_due_date(self):
        wizard_model = self.env['wizard.import.fatturapa']
        for att in self:
            fatt = wizard_model.get_invoice_obj(att)
            if not fatt:
                continue
            for fattura in fatt.FatturaElettronicaBody: 
                wizard_model.set_payment_term(
                    att.in_invoice_ids[0],
                    att.in_invoice_ids[0].company_id,
                    fattura.DatiPagamento)
