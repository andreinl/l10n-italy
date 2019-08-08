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
        user = self.env['res.users'].browse(self.env.uid)
        style_sheet_mode = user.company_id.style_sheet_mode

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
        for attachment in self:
            # if att.id in self.cache_get_attachment_fields:
            #     res[att.id] = self.cache_get_attachment_fields[att.id]
            #     continue

            attachment.xml_attachment_datas = False
            attachment.xml_attachment_filename = ''

            if attachment.xml_have_attachment:
                supplier_id = attachment.xml_supplier_id and attachment.xml_supplier_id.id or False
                name = 'Errore'
                if supplier_id:
                    supplier_ids = self.env['res.partner'].search([('id', '=', supplier_id)])
                    if supplier_ids:
                        name = attachment.xml_supplier_id.name

                    # attachment.xml_attachment_datas = False,
                    attachment.xml_attachment_filename = u"{}.zip".format(name)

                in_memory_zip = StringIO()
                zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_STORED, False)
                zf.debug = 3

                try:
                    fatt = self.env.get('wizard.import.fatturapa').get_invoice_obj(attachment)
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
                # self.cache_get_attachment_fields[attachment.id] = res[attachment.id].copy()
        return

    @api.multi
    def _compute_xml_data(self):
        for att in self:
            # if att.id in self.cache_compute_xml_data:
            #     ret[att.id] = self.cache_compute_xml_data[att.id]
            #
            #     continue

            # DDT_number = []
            # supplier_invoice_numbers = []
            # supplier_invoice_dates = []
            # partner_id = False
            # invoices_total = 0
            # xml_invoice_type = 'TD01'
            # invoices_number = 0
            xml_have_attachment = False
            # xml_errors = ''
            try:
                fatt = self.env.get('wizard.import.fatturapa').get_invoice_obj(att)
                # cedentePrestatore = fatt.FatturaElettronicaHeader.CedentePrestatore
                # partner_id = self.pool.get('wizard.import.fatturapa').getCedPrest(cedentePrestatore)
                # invoices_number = len(fatt.FatturaElettronicaBody)
                for invoice_body in fatt.FatturaElettronicaBody:
                    # docType = invoice_body.DatiGenerali.DatiGeneraliDocumento.TipoDocumento
                    # supplier_invoice_numbers.append(invoice_body.DatiGenerali.DatiGeneraliDocumento.Numero)
                    # if invoice_body.DatiGenerali.DatiGeneraliDocumento.Data:
                    #     data = datetime.strptime(str(invoice_body.DatiGenerali.DatiGeneraliDocumento.Data)[0:10], DEFAULT_SERVER_DATE_FORMAT)
                    #     supplier_invoice_dates.append(data.strftime("%d/%m/%Y"))
                    # invoices_total += float(
                    #     invoice_body.DatiGenerali.DatiGeneraliDocumento.ImportoTotaleDocumento or 0
                    # )
                    # for DDT in invoice_body.DatiGenerali.DatiDDT:
                    #     DDT_number.append(DDT.NumeroDDT)
                    xml_have_attachment = invoice_body.Allegati

                # try:
                #     xml_invoice_type = str(docType)
                # except Exception as e:
                #     _logger.error(e)
                #     xml_errors = str(e)

            except Exception as e:
                _logger.error(e)
                # xml_errors = str(e)

                # att.xml_invoice_type': xml_invoice_type,
                # att.xml_supplier_id': partner_id,
                # att.invoices_number': invoices_number,
                # att.invoices_total': invoices_total,
                # att.ddt_number': ','.join(list(set(DDT_number))),
                # att.supplier_invoice_numbers': ','.join(list(set(supplier_invoice_numbers))),
                # att.invoices_date': ','.join(list(set(supplier_invoice_dates))),
                att.xml_have_attachment = xml_have_attachment
                # att.xml_errors': xml_errors

            # self.cache_compute_xml_data[att.id] = vals

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

    xml_preview = fields.Text(compute=_get_fattura_elettronica_preview, string="Preview")
    xml_attachment_datas = fields.Binary(compute=_get_attachment_fields, string="XML File")
    xml_attachment_filename = fields.Char(compute=_get_attachment_fields, string="XML File Name")
    xml_have_attachment = fields.Boolean(compute=_compute_xml_data, string="Have Attachment", store=True)

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
