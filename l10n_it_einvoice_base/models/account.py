# -*- coding: utf-8 -*-
#
# Copyright 2014    - Davide Corio <davide.corio@lsweb.it>
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import fields, orm

RELATED_DOCUMENT_TYPES = {
    'order': 'DatiOrdineAcquisto',
    'contract': 'DatiContratto',
    'agreement': 'DatiConvenzione',
    'reception': 'DatiRicezione',
    'invoice': 'DatiFattureCollegate',
}
# TODO: Use module for classification
EU_COUNTRIES = ['AT', 'BE', 'BG', 'CY', 'HR', 'DK', 'EE',
                'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LV',
                'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'GB',
                'CZ', 'RO', 'SK', 'SI', 'ES', 'SE', 'HU']


class FatturapaFormat(orm.Model):
    # _position = ['1.1.3']
    _name = "fatturapa.format"
    _description = 'FatturaPA Format'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=5),
    }

#  used in fatturaPa import
class FatturapaPaymentData(orm.Model):
    # _position = ['2.4.2.2']
    _name = "fatturapa.payment.data"
    _description = 'FatturaPA Payment Data'

    _columns = {
        #  2.4.1
        'payment_terms': fields.many2one(
            'fatturapa.payment_term', string="Electronic Invoice Payment Method"),
        #  2.4.2
        'payment_methods': fields.one2many(
            'fatturapa.payment.detail', 'payment_data_id',
            'Payments Details'
        ),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
    }


class FatturapaPaymentDetail(orm.Model):
    # _position = ['2.4.2']
    _name = "fatturapa.payment.detail"
    _columns = {
        'recipient': fields.char('Recipient', size=200),
        'fatturapa_pm_id': fields.many2one(
            'fatturapa.payment_method', string="FatturaPA Payment Method"),
        'payment_term_start': fields.date('Payment Term Start'),
        'payment_days': fields.integer('Payment Term Days'),
        'payment_due_date': fields.date('Payment due Date'),
        'payment_amount': fields.float('Payment Amount'),
        'post_office_code': fields.char('Post Office Code', size=20),
        'recepit_name': fields.char("Recepit payment partner firstname"),
        'recepit_surname': fields.char("Recepit payment partner lastname"),
        'recepit_cf': fields.char("Recepit payment partner fiscalnumber"),
        'recepit_title': fields.char("Recepit payment partner title"),
        'payment_bank_name': fields.char("Bank name"),
        'payment_bank_iban': fields.char("IBAN"),
        'payment_bank_abi': fields.char("ABI"),
        'payment_bank_cab': fields.char("CAB"),
        'payment_bank_bic': fields.char("BIC"),
        'payment_bank': fields.many2one(
            'res.partner.bank', string="Payment Bank"),
        'prepayment_discount': fields.float('Prepayment Discount'),
        'max_payment_date': fields.date('Maximum date for Payment'),
        'penalty_amount': fields.float('Amount of Penality'),
        'penalty_date': fields.date('Effective date of Penality'),
        'payment_code': fields.char('Payment code'),
        'account_move_line_id': fields.many2one(
            'account.move.line', string="Payment Line"),
        'payment_data_id': fields.many2one(
            'fatturapa.payment.data', 'Related payments Data',
            ondelete='cascade', select=True),
    }


class FatturapaFiscalPosition(orm.Model):
    # _position = ['2.1.1.7.7', '2.2.1.14']
    _name = "fatturapa.fiscal_position"
    _description = 'Electronic Invoice Fiscal Position'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4),
    }


class WelfareFundType(orm.Model):
    # _position = ['2.1.1.7.1']
    _name = "welfare.fund.type"
    _description = 'welfare fund type'

    _columns = {
        'name': fields.char('name'),
        'description': fields.char('description'),
    }


class WelfareFundDataLine(orm.Model):
    # _position = ['2.1.1.7']
    _name = "welfare.fund.data.line"
    _description = 'FatturaPA Welfare Fund Data'

    _columns = {
        'name': fields.many2one(
            'welfare.fund.type', string="Welfare Fund Type"),
        'tax_nature_id': fields.many2one(
            'italy.ade.tax.nature', string="No taxable nature"),
        'welfare_rate_tax': fields.float('Welfare Rate tax'),
        'welfare_amount_tax': fields.float('Welfare Amount tax'),
        'welfare_taxable': fields.float('Welfare Taxable'),
        'welfare_Iva_tax': fields.float('Welfare tax'),
        'subjected_withholding': fields.char(
            'Subjected at Withholding', size=2),
        'pa_line_code': fields.char('PA Code for this record', size=20),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True
        ),
    }


class DiscountRisePrice(orm.Model):
    # _position = ['2.1.1.8', '2.2.1.10']
    _name = "discount.rise.price"
    _description = 'FatturaPA Discount Rise Price Data'

    _columns = {
        'name': fields.selection(
            [('SC', 'Discount'), ('MG', 'Rise Price')], 'Type'),
        'percentage': fields.float('Percentage'),
        'amount': fields.float('Amount'),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice',
            ondelete='cascade', index=True),
        'invoice_id': fields.many2one(
            'account.invoice.line', 'Related Invoice',
            ondelete='cascade', select=True
        ),
    }


class FatturapaRelatedDocumentType(orm.Model):
    # _position = ['2.1.2', '2.2.3', '2.1.4', '2.1.5', '2.1.6']
    _name = 'fatturapa.related_document_type'
    _description = 'FatturaPA Related Document Type'

    _columns = {
        'type': fields.selection(
            [
                ('order', 'Order'),
                ('contract', 'Contract'),
                ('agreement', 'Agreement'),
                ('reception', 'Reception'),
                ('invoice', 'Related Invoice')
            ],
            'Document Type', required=True
        ),
        'name': fields.char('DocumentID', size=20, required=True),
        'lineRef': fields.integer('LineRef'),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice Line',
            ondelete='cascade', select=True),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
        'date': fields.date('Date'),
        'numitem': fields.char('NumItem', size=20),
        'code': fields.char('Order Agreement Code', size=100),
        'cig': fields.char('CIG Code', size=15),
        'cup': fields.char('CUP Code', size=15),
    }

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if vals.get('invoice_line_id'):
            line_obj = self.pool.get('account.invoice.line')
            line = line_obj.browse(
                cr, uid, vals['invoice_line_id'], context=context)
            vals['lineRef'] = line.sequence
        return super(FatturapaRelatedDocumentType,
                     self).create(cr, uid, vals, context)


class FaturapaActivityProgress(orm.Model):
    # _position = ['2.1.7']
    _name = "faturapa.activity.progress"

    _columns = {
        'fatturapa_activity_progress': fields.integer('Activity Progress'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True)
    }


class FatturaAttachments(orm.Model):
    # _position = ['2.5']
    _name = "fatturapa.attachments"
    _description = "FatturaPA attachments"
    _inherits = {'ir.attachment': 'ir_attachment_id'}

    _columns = {
        'ir_attachment_id': fields.many2one(
            'ir.attachment', 'Attachment', required=True, ondelete="cascade"),
        'compression': fields.char('Compression', size=10),
        'format': fields.char('Format', size=10),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True)
    }


class FatturapaRelatedDdt(orm.Model):
    # _position = ['2.1.2', '2.2.3', '2.1.4', '2.1.5', '2.1.6']
    _name = 'fatturapa.related_ddt'
    _description = 'FatturaPA Related DdT'

    _columns = {
        'name': fields.char('DocumentID', size=20, required=True),
        'date': fields.date('Date'),
        'lineRef': fields.integer('LineRef'),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice Line',
            ondelete='cascade', select=True),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
    }

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if vals.get('invoice_line_id'):
            line_obj = self.pool.get('account.invoice.line')
            line = line_obj.browse(
                cr, uid, vals['invoice_line_id'], context=context)
            vals['lineRef'] = line.sequence
        return super(FatturapaRelatedDdt,
                     self).create(cr, uid, vals, context)


class AccountInvoiceLine(orm.Model):
    # _position = ['2.2.1']
    _inherit = "account.invoice.line"

    _columns = {
        'related_documents': fields.one2many(
            'fatturapa.related_document_type', 'invoice_line_id',
            'Related Documents Type'
        ),
        'ftpa_related_ddts': fields.one2many(
            'fatturapa.related_ddt', 'invoice_line_id',
            'Related DdT'
        ),
        'admin_ref': fields.char('Administration ref.', size=20),
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'invoice_line_id',
            'Discount and Rise Price Details'
        ),
        'ftpa_line_number': fields.integer("Line number", readonly=True)
    }


class FaturapaSummaryData(orm.Model):
    # _position = ['2.2.2']
    _name = "faturapa.summary.data"
    _columns = {
        'tax_rate': fields.float('Tax Rate'),
        'non_taxable_nature': fields.many2one(
            'italy.ade.tax.nature',
            "No taxable nature"),
        'incidental charges': fields.float('Incidental Charges'),
        'rounding': fields.float('Rounding'),
        'amount_untaxed': fields.float('Amount untaxed'),
        'amount_tax': fields.float('Amount tax'),
        'payability': fields.selection([
            ('I', 'Immediate payability'),
            ('D', 'Deferred payability'),
            ('S', 'Split payment'),
        ], string="VAT payability"),
        'law_reference': fields.char(
            'Law reference', size=128),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True)
    }


class AccountInvoice(orm.Model):
    # _position = ['2.1', '2.2', '2.3', '2.4', '2.5']
    _inherit = "account.invoice"
    _columns = {
        'protocol_number': fields.char('Protocol Number', size=64),
        # 1.2 -- partner_id
        #  1.3
        'tax_representative_id': fields.many2one(
            'res.partner', string="Tax Rapresentative"),
        #  1.4 company_id
        #  1.5
        'intermediary': fields.many2one(
            'res.partner', string="Intermediary"),
        #  1.6
        'sender': fields.selection(
            [('CC', 'assignee / partner'),
             ('TZ', 'third person')], 'Sender'),
        #  2.1.1.1 FIXME
        'invoice_type_id': fields.many2one(
            'italy.ade.invoice.type', string="Document Type"),
        #  2.1.1.5
        #  2.1.1.5.1
        'ftpa_withholding_type': fields.selection(
            [('RT01', 'Natural Person'),
             ('RT02', 'Legal Person')],
            'Withholding type'
        ),
        #  2.1.1.5.2 withholding_amount in module
        #  2.1.1.5.3
        'ftpa_withholding_rate': fields.float('Withholding rate'),
        #  2.1.1.5.4
        'ftpa_withholding_payment_reason': fields.char(
            'Withholding reason', size=2),
        #  2.1.1.6
        'virtual_stamp': fields.boolean('Virtual Stamp'),
        'stamp_amount': fields.float('Stamp Amount'),
        #  2.1.1.7
        'welfare_fund_ids': fields.one2many(
            'welfare.fund.data.line', 'invoice_id',
            'Welfare Fund'
        ),
        #  2.1.1.8 FIXME
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'invoice_id',
            'Discount and Rise Price Details'
        ),
        #  2.1.2 - 2.1.6
        'related_documents': fields.one2many(
            'fatturapa.related_document_type', 'invoice_id',
            'Related Documents'
        ),
        #  2.1.7
        'activity_progress_ids': fields.one2many(
            'faturapa.activity.progress', 'invoice_id',
            'Fase of Activity Progress'
        ),
        #  2.1.8
        'ftpa_related_ddts': fields.one2many(
            'fatturapa.related_ddt', 'invoice_id',
            'Related DdT'
        ),
        #  2.1.9
        'carrier_id': fields.many2one(
            'res.partner', string="Carrier"),
        'transport_vehicle': fields.char('Vehicle', size=80),
        'transport_reason': fields.char('Reason', size=80),
        'number_items': fields.integer('number of items'),
        'description': fields.char('Description', size=100),
        'unit_weight': fields.char('Weight unit', size=10),
        'gross_weight': fields.float('Gross Weight'),
        'net_weight': fields.float('Net Weight'),
        'pickup_datetime': fields.datetime('Pick up'),
        'transport_date': fields.date('Transport Date'),
        'delivery_address': fields.text('Delivery Address'),
        'delivery_datetime': fields.datetime('Delivery Date Time'),
        'ftpa_incoterms': fields.char(string="Incoterms"),
        #  2.1.10
        'related_invoice_code': fields.char('Related invoice code'),
        'related_invoice_date': fields.date('Related invoice date'),
        #  2.2.1 invoice lines
        #  2.2.2
        'fatturapa_summary_ids': fields.one2many(
            'faturapa.summary.data', 'invoice_id',
            'FatturaPA Summary   Datas'
        ),
        #  2.3
        'Vehicle_registration': fields.date('Veicole Registration'),
        'total_travel': fields.char('Travel in hours or Km', size=15),
        #  2.4
        'fatturapa_payments': fields.one2many(
            'fatturapa.payment.data', 'invoice_id',
            'FatturaPA Payment Datas'
        ),
        #  2.5
        'fatturapa_doc_attachments': fields.one2many(
            'fatturapa.attachments', 'invoice_id',
            'FatturaPA attachments'
        ),

        # 1.2.3
        'efatt_stabile_organizzazione_indirizzo': fields.char(
            string="Indirizzo Organizzazione",
            help="Blocco da valorizzare nei casi di cedente / prestatore non "
                 "residente, con stabile organizzazione in Italia. Indirizzo "
                 "della stabile organizzazione in Italia (nome della via, piazza "
                 "etc.)",
            readonly=True),
        'efatt_stabile_organizzazione_civico': fields.char(
            string="Civico Organizzazione",
            help="Numero civico riferito all'indirizzo (non indicare se già "
                 "presente nell'elemento informativo indirizzo)",
            readonly=True),
        'efatt_stabile_organizzazione_cap': fields.char(
            string="CAP Organizzazione",
            help="Codice Avviamento Postale",
            readonly=True),
        'efatt_stabile_organizzazione_comune': fields.char(
            string="Comune Organizzazione",
            help="Comune relativo alla stabile organizzazione in Italia",
            readonly=True),
        'efatt_stabile_organizzazione_provincia': fields.char(
            string="Provincia Organizzazione",
            help="Sigla della provincia di appartenenza del comune indicato "
                 "nell'elemento informativo 1.2.3.4 <Comune>. Da valorizzare se "
                 "l'elemento informativo 1.2.3.6 <Nazione> è uguale a IT",
            readonly=True),
        'efatt_stabile_organizzazione_nazione': fields.char(
            string="Nazione Organizzazione",
            help="Codice della nazione espresso secondo lo standard "
                 "ISO 3166-1 alpha-2 code",
            readonly=True),
        # 2.1.1.10
        'efatt_rounding': fields.float(
            "Arrotondamento", readonly=True,
            help="Eventuale arrotondamento sul totale documento (ammette anche il "
                 "segno negativo)"),
        'art73': fields.boolean(
            'Art73', readonly=True,
            help="Indica se il documento è stato emesso secondo modalità e "
                 "termini stabiliti con decreto ministeriale ai sensi "
                 "dell'articolo 73 del DPR 633/72 (ciò consente al "
                 "cedente/prestatore l'emissione nello stesso anno di più "
                 "documenti aventi stesso numero)")
    }
    _defaults = {
        'virtual_stamp': False
    }
