# -*- coding: utf-8 -*-
#
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
#
from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError
import lxml.etree as ET
from openerp.modules.module import get_module_resource
from io import BytesIO, StringIO
import logging
import zipfile
import base64
# from datetime import datetime
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class FatturaPAAttachmentIn(models.Model):
    _name = "fatturapa.attachment.in"
    _description = "E-bill import file"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']
    _order = 'id desc'

    @api.multi
    def _get_fattura_elettronica_preview(self):
        # config = self.env['account.config.settings'].browse(1)

        # style_sheet_mode = self.user_id.company_id.style_sheet_mode
        style_sheet_mode = False

        if not style_sheet_mode or style_sheet_mode == 'asso_software':
            xsl_path = get_module_resource('l10n_it_einvoice_base', 'data', 'FoglioStileAssoSoftware.xsl')
        else:
            xsl_path = get_module_resource('l10n_it_einvoice_base', 'data', 'fatturaordinaria_v1.2.1.xsl')
        xslt = ET.parse(xsl_path)

        for fatturapa_attachment in self:
            try:
                xml_string = fatturapa_attachment.with_context({'bin_size': False}).get_xml_string()
                xml_file = BytesIO(xml_string)
                recovering_parser = ET.XMLParser(recover=True)
                dom = ET.parse(xml_file, parser=recovering_parser)
                transform = ET.XSLT(xslt)
                newdom = transform(dom)
                fatturapa_attachment.xml_preview = ET.tostring(newdom, pretty_print=True)
            except Exception as e:
                fatturapa_attachment.xml_preview = '<?xml version="1.0" encoding="UTF-8"?>'
        return

    @api.multi
    def _get_attachment_fields(self):
        for attachment in self.with_context({'bin_size': False}):
            # if att.id in self.cache_get_attachment_fields:
            #     res[att.id] = self.cache_get_attachment_fields[att.id]
            #     continue

            # attachment.xml_attachment_datas = False
            # attachment.xml_attachment_filename = ''

            if attachment.xml_have_attachment:
                supplier_id = attachment.xml_supplier_id and attachment.xml_supplier_id.id or False
                name = 'Errore'
                if supplier_id:
                    supplier_ids = self.env['res.partner'].search([('id', '=', supplier_id)])
                    if supplier_ids:
                        name = attachment.xml_supplier_id.name

                    # attachment.xml_attachment_datas = False,
                    attachment.xml_attachment_filename = u"{}.zip".format(name)

                in_memory_zip = BytesIO()
                zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_STORED, False)
                zf.debug = 3

                try:
                    fatt = self.env['wizard.import.fatturapa'].get_invoice_obj(attachment)
                except Exception as e:
                    continue

                attachments = False
                for invoice_body in fatt.FatturaElettronicaBody:
                    AttachmentsData = invoice_body.Allegati
                    if AttachmentsData:
                        for attach in AttachmentsData:
                            if not attach.NomeAttachment:
                                raise Warning(_('Attachment Name is Required'))
                            content = attach.Attachment
                            name = attach.NomeAttachment
                            _attach_dict = {
                                'name': name,
                                'datas': base64.b64encode(str(content)),
                                'datas_fname': name,
                                'description': attach.DescrizioneAttachment or '',
                                'compression': attach.AlgoritmoCompressione or '',
                                'format': attach.FormatoAttachment or '',
                            }
                            attachments = True
                            zf.writestr(_attach_dict['name'], _attach_dict['datas'].decode("base64"))
                if attachments:
                    for zfile in zf.filelist:
                        zfile.create_system = 0

                    if not zf.infolist():
                        zf.writestr('empty', 'empty')

                    for info in zf.infolist():
                        _logger.info(
                            u"{0}, {1}, {2}, {3}".format(info.filename, info.date_time, info.file_size,
                                                         info.compress_size))
                    zf.close()
                    in_memory_zip.seek(0)
                    out = in_memory_zip.getvalue()
                    out.encode("base64")
                    attachment.xml_attachment_datas = out

                    # attachment.write({
                    #     'xml_attachment_datas': out,
                    #     'xml_attachment_filename': attachment.xml_attachment_filename
                    # })
                # self.cache_get_attachment_fields[attachment.id] = res[attachment.id].copy()
        return

    @api.multi
    @api.depends('xml_supplier_id')
    def _count_related_products(self):
        for xml_attachment in self:
            if xml_attachment.xml_supplier_id:
                if xml_attachment.xml_supplier_id.e_invoice_default_product_id:
                    xml_attachment.xml_supplier_related_products = 1
                else:
                    xml_attachment.xml_supplier_related_products = 0
                xml_attachment.xml_supplier_related_products += self.env['product.supplierinfo'].search([
                    ('name', '=', xml_attachment.xml_supplier_id.id)
                ], count=True)
                xml_attachment.xml_supplier_default_product_id = xml_attachment.xml_supplier_id.e_invoice_default_product_id.id

        return

    ir_attachment_id = fields.Many2one(
        'ir.attachment', 'Attachment', required=True, ondelete="cascade")
    in_invoice_ids = fields.One2many(
        'account.invoice', 'fatturapa_attachment_in_id',
        string="In Bills", readonly=True)
    xml_supplier_id = fields.Many2one(
        "res.partner", string="Supplier", compute="_compute_xml_data",
        store=True)
    # xml_supplier_default_product_id = fields.Many2one(
    #     related="xml_supplier_id.e_invoice_default_product_id", string="Default product", store=True)
    # xml_supplier_default_product_id = fields.Many2one(
    #     "product.product", compute="_compute_xml_data", string="Default product")
    xml_supplier_default_product_id = fields.Many2one(
        "product.product", compute=_count_related_products, string="Default product")

    # xml_supplier_related_products = fields.Integer(compute="_compute_xml_data", string="Supplier products")
    xml_supplier_related_products = fields.Integer(compute=_count_related_products, string="Supplier products")

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

    supplier_invoice_numbers = fields.Char(
        compute="_compute_xml_data", string="Invoices number", size=2048, store=True)

    xml_preview = fields.Text(compute=_get_fattura_elettronica_preview, string="Preview")
    xml_attachment_datas = fields.Binary(compute=_get_attachment_fields, string="XML File")
    xml_attachment_filename = fields.Char(compute=_get_attachment_fields, string="XML File Name")
    xml_have_attachment = fields.Boolean(compute="_compute_xml_data", string="Have Attachment", store=True)

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

        # Problem with cache system for new API https://github.com/odoo/odoo/issues/6276
        if self._context.get('bin_size'):
            context = self._context.copy()
            context['bin_size'] = False
            attachments = self.with_context(context)
        else:
            attachments = self

        # for att in self.with_context({'bin_size': False}):
        for att in attachments:
            supplier_invoice_numbers = []
            # supplier_invoice_dates = []
            xml_have_attachment = False

            try:
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
                    supplier_invoice_numbers.append(invoice_body.DatiGenerali.DatiGeneraliDocumento.Numero)

                    if not att.in_invoice_ids:
                        att.date_invoice0 = invoice_body.\
                            DatiGenerali.DatiGeneraliDocumento.Data

                    xml_have_attachment = invoice_body.Allegati
            except Exception as e:
                _logger.error(e)

            att.supplier_invoice_numbers = ','.join(list(set(supplier_invoice_numbers)))
            att.xml_have_attachment = xml_have_attachment

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

    def extract_attachments(self, AttachmentsData, invoice_id):
        AttachModel = self.env['fatturapa.attachments']
        for attach in AttachmentsData:
            if not attach.NomeAttachment:
                name = _("Attachment without name")
            else:
                name = attach.NomeAttachment
            content = attach.Attachment
            _attach_dict = {
                'name': name,
                'datas': base64.b64encode(content),
                'datas_fname': name,
                'description': attach.DescrizioneAttachment or '',
                'compression': attach.AlgoritmoCompressione or '',
                'format': attach.FormatoAttachment or '',
                'invoice_id': invoice_id,
            }
            AttachModel.create(_attach_dict)
