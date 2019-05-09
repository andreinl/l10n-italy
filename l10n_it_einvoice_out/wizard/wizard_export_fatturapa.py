# -*- coding: utf-8 -*-
#
# Copyright 2014    - Davide Corio <davide.corio@lsweb.it>
# Copyright 2015    - Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
import base64
import logging

from openerp import models
from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2 import (
    FatturaElettronica,
    FatturaElettronicaHeaderType,
    DatiTrasmissioneType,
    IdFiscaleType,
    ContattiTrasmittenteType,
    CedentePrestatoreType,
    AnagraficaType,
    IndirizzoType,
    IscrizioneREAType,
    CessionarioCommittenteType,
    DatiAnagraficiCedenteType,
    DatiAnagraficiCessionarioType,
    FatturaElettronicaBodyType,
    DatiGeneraliType,
    DettaglioLineeType,
    DatiBeniServiziType,
    DatiRiepilogoType,
    DatiGeneraliDocumentoType,
    DatiDocumentiCorrelatiType,
    ContattiType,
    DatiPagamentoType,
    DettaglioPagamentoType,
    AllegatiType,
    ScontoMaggiorazioneType
)
from openerp.addons.l10n_it_einvoice_base.models.account import (
    RELATED_DOCUMENT_TYPES
)
from openerp.osv import orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
    from pyxb.exceptions_ import SimpleFacetValueError, SimpleTypeValueError
except ImportError as err:
    _logger.debug(err)

STYLESHEET = 'fatturapa_v1.2.xsl'


class WizardExportFatturapa(models.TransientModel):
    _name = "wizard.export.fatturapa"
    _description = "Export EInvoice"

    def __init__(self, cr, uid, **kwargs):
        super(WizardExportFatturapa, self).__init__(cr, uid, **kwargs)

    def saveAttachment(self, cr, uid, fatturapa, number, context=None):
        context = context or {}
        if 'company_id' in context:
            company_model = self.pool['res.company']
            company = company_model.browse(cr, uid, context['company_id'])
        else:
            user_model = self.pool['res.users']
            company = user_model.browse(cr, uid, uid).company_id
        if not company.vat:
            raise orm.except_orm(
                _('Error!'), _('Company TIN not set.'))
        attach_model = self.pool['fatturapa.attachment.out']

        invoice_xml = fatturapa.toDOM().toprettyxml(encoding="latin1").replace(
            '<?xml version="1.0" encoding="latin1"?>',
            """<?xml version="1.0" encoding="latin1"?>
<?xml-stylesheet type="text/xsl" href="{xsl}"?>""".format(xsl=STYLESHEET))

        attach_vals = {
            'name': '%s_%s.xml' % (company.vat, str(number)),
            'datas_fname': '%s_%s.xml' % (company.vat, str(number)),
            # 'datas': base64.encodestring(fatturapa.toxml("UTF-8")),
            'datas': base64.encodestring(invoice_xml),
        }
        return attach_model.create(cr, uid, attach_vals, context=context)

    def setProgressivoInvio(self, cr, uid, fatturapa, context=None):
        context = context or {}
        if 'company_id' in context:
            company_model = self.pool['res.company']
            company = company_model.browse(cr, uid, context['company_id'])
        else:
            user_model = self.pool['res.users']
            company = user_model.browse(cr, uid, uid).company_id

        sequence_model = self.pool['ir.sequence']
        fatturapa_sequence = company.fatturapa_sequence_id
        if not fatturapa_sequence:
            raise orm.except_orm(
                _('Error!'), _('FatturaPA sequence not configured.'))
        number = sequence_model.next_by_id(
            cr, uid, fatturapa_sequence.id, context=context)
        try:
            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
                ProgressivoInvio = number
        except (SimpleFacetValueError, SimpleTypeValueError) as e:
            msg = _(
                'FatturaElettronicaHeader.DatiTrasmissione.'
                'ProgressivoInvio:\n%s'
            ) % unicode(e)
            raise orm.except_orm(
                _('Error!'), _(msg))
        return number

    def _string2codeset(self, text):
        return text.encode('latin', 'ignore').decode('latin')

    def _wep_phone_number(self, phone):
        """"Remove trailing +39 and all no numeric chars"""
        wep_phone = ''
        if phone:
            if phone[0:3] == '+39':
                phone = phone[3:]
            elif phone[0] == '+':
                phone = '00' + phone[1:]
            for i in range(len(phone)):
                if phone[i].isdigit():
                    wep_phone += phone[i]
        return wep_phone

    def _setIdTrasmittente(self, cr, uid, company, fatturapa, context=None):
        context = context or {}
        if not company.country_id:
            raise orm.except_orm(
                _('Error!'), _('Company Country not set.'))
        IdPaese = company.country_id.code

        IdCodice = company.partner_id.fiscalcode
        if not IdCodice:
            IdCodice = company.vat[2:]
        if not IdCodice:
            raise orm.except_orm(
                _('Error'),
                _('Company does not have fiscal code or VAT'))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            IdTrasmittente = IdFiscaleType(
                IdPaese=IdPaese, IdCodice=IdCodice)

        return True

    def _setFormatoTrasmissione(self, cr, uid, partner, fatturapa,
                                context=None):
        context = context or {}
        if partner.is_pa:
            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
                FormatoTrasmissione = 'FPA12'
        else:
            fatturapa.FatturaElettronicaHeader.DatiTrasmissione. \
                FormatoTrasmissione = 'FPR12'

        return True

    def _setCodiceDestinatario(self, cr, uid, partner, fatturapa, context=None):
        """
        Nota sito agenzia entrate:
        Il Codice Destinatario a 7 caratteri, che può essere utilizzato solo per fatture elettroniche destinate ai
        soggetti privati, potrà essere reperito attraverso un nuovo servizio reso disponibile entro il
        9 di Gennaio 2017 sul sito www.fatturapa.gov.it, pagina Strumenti – Gestire il canale.
        Il codice potrà essere richiesto solo dai quei soggetti titolari di un canale di trasmissione già accreditato
        presso il Sistema di Interscambio per ricevere le fatture elettroniche. É possibile richiedere più codici fino
        a un massimo di 100. Per i soggetti che invece intendano ricevere le fatture elettroniche attraverso il canale
         PEC, è previsto l’uso del codice destinatario standard ‘0000000’ purché venga indicata la casella PEC di
        ricezione in fattura nel campo PecDestinatario. Vale la pena ricordare che per le fatture elettroniche
        destinate ad Amministrazioni pubbliche si continua a prevedere l’uso del codice univoco ufficio a 6 caratteri,
        purché sia censito su indice delle Pubbliche Amministrazioni (www.indicepa.gov.it )
        """

        if partner.is_pa:
            if partner.ipa_code:
                code = partner.ipa_code
            else:
                raise orm.except_orm(
                    _('Error!'),
                    _("Partner %s is PA but has not IPA code") % partner.name
                )
        else:
            code = partner.codice_destinatario
            if not code or code == '0000000':
                if partner.vat or partner.fiscalcode:
                    if partner.country_id and partner.country_id.code == 'IT':
                        code = '0000000'

                        if partner.pec_destinatario:
                            # if validate_email(pec_destinatario):
                            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.PECDestinatario = partner.pec_destinatario
                            # else:
                            #     raise orm.except_orm(_('Error!'),
                            #                          _('{pec_email} is not correct').format(pec_email=pec_destinatario))
                        elif partner.vat:
                            raise orm.except_orm(
                                _('Error!'),
                                _('No PEC find for Partner: {partner}').format(partner=partner.name))
                    elif partner.country_id and not partner.country_id.code == 'IT':
                        code = 'XXXXXXX'
                    else:
                        raise orm.except_orm(
                            _('Error!'),
                            _('No Address find for Partner: {partner}').format(partner=partner.name))
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Please set Fiscal Code or VAT for partner {}').format(partner.name))
            elif len(code) != 7:
                if ' ' in code:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Space char in Recipient Code \'{code}\'').format(code=code)
                    )
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Recipient Code {code} length is {dimension}, it should be 7').format(code=code, dimension=len(code)))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.CodiceDestinatario = code.upper()

        return True

    def _setContattiTrasmittente(self, cr, uid, company, fatturapa,
                                 context=None):
        # context = context or {}
        if not company.phone:
            raise orm.except_orm(
                _('Error!'), _('Company Telephone number not set.'))
        Telefono=self._wep_phone_number(company.phone)
        if not company.email:
            raise orm.except_orm(
                _('Error!'), _('Company Email not set.'))
        Email = company.einvoice_email or company.email
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            ContattiTrasmittente = ContattiTrasmittenteType(
                Telefono=Telefono, Email=Email)
        return True

    def setDatiTrasmissione(self, cr, uid,
                            company, partner, fatturapa, 
                            context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione = (
            DatiTrasmissioneType())
        self._setIdTrasmittente(cr, uid, company, fatturapa, context=context)
        self._setFormatoTrasmissione(cr, uid, partner, fatturapa,
                                     context=context)
        self._setCodiceDestinatario(cr, uid, partner, fatturapa,
                                    context=context)
        self._setContattiTrasmittente(cr, uid, company, fatturapa,
                                      context=context)

    def _setDatiAnagraficiCedente(self, cr, uid, CedentePrestatore,
                                  company, context=None):
        # context = context or {}
        if not company.vat:
            raise orm.except_orm(
                _('Error!'), _('Company TIN not set.'))
        CedentePrestatore.DatiAnagrafici = DatiAnagraficiCedenteType()
        fatturapa_fp = company.fatturapa_fiscal_position_id
        if not fatturapa_fp:
            raise orm.except_orm(
                _('Error!'), _('FatturaPA fiscal position not set.'))
        CedentePrestatore.DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
            IdPaese=company.country_id.code, IdCodice=company.vat[2:])
        CedentePrestatore.DatiAnagrafici.Anagrafica = AnagraficaType(
            Denominazione=company.name)

        # not using for now
        #
        # Anagrafica = DatiAnagrafici.find('Anagrafica')
        # Nome = Anagrafica.find('Nome')
        # Cognome = Anagrafica.find('Cognome')
        # Titolo = Anagrafica.find('Titolo')
        # Anagrafica.remove(Nome)
        # Anagrafica.remove(Cognome)
        # Anagrafica.remove(Titolo)

        if company.partner_id.fiscalcode:
            CedentePrestatore.DatiAnagrafici.CodiceFiscale = (
                company.partner_id.fiscalcode)
        CedentePrestatore.DatiAnagrafici.RegimeFiscale = fatturapa_fp.code
        return True

    def _setAlboProfessionaleCedente(self, cr, uid, CedentePrestatore,
                                     company, context=None):
        context = context or {}
        # TODO Albo professionale, for now the main company is considered
        # to be a legal entity and not a single person
        # 1.2.1.4   <AlboProfessionale>
        # 1.2.1.5   <ProvinciaAlbo>
        # 1.2.1.6   <NumeroIscrizioneAlbo>
        # 1.2.1.7   <DataIscrizioneAlbo>
        return True

    def _setSedeCedente(self, cr, uid, CedentePrestatore,
                        company, context=None):
        context = context or {}

        if not company.street:
            raise orm.except_orm(
                _('Error!'), _('Street not set.'))
        if not company.zip:
            raise orm.except_orm(
                _('Error!'), _('ZIP not set.'))
        if not company.city:
            raise orm.except_orm(
                _('Error!'), _('City not set.'))
        if not company.partner_id.state_id:
            raise orm.except_orm(
                _('Error!'), _('Province not set.'))
        if not company.country_id:
            raise orm.except_orm(
                _('Error!'), _('Country not set.'))
        # FIXME: manage address number in <NumeroCivico>
        # see https://github.com/OCA/partner-contact/pull/96
        CedentePrestatore.Sede = IndirizzoType(
            Indirizzo=company.street,
            CAP=company.zip,
            Comune=company.city[:60],
            Provincia=company.partner_id.state_id.code,
            Nazione=company.country_id.code)
        return True

    def _setStabileOrganizzazione(self, cr, uid, CedentePrestatore,
                                  company, context=None):
        context = context or {}
        # not handled
        return True

    def _setRea(self, cr, uid, CedentePrestatore, company, context=None):
        context = context or {}
        if company.fatturapa_rea_office and company.fatturapa_rea_number:
            CedentePrestatore.IscrizioneREA = IscrizioneREAType(
                Ufficio=(
                    company.fatturapa_rea_office and
                    company.fatturapa_rea_office.code or None),
                NumeroREA=company.fatturapa_rea_number or None,
                CapitaleSociale=(
                    company.fatturapa_rea_capital and
                    '%.2f' % company.fatturapa_rea_capital or None),
                SocioUnico=(company.fatturapa_rea_partner or None),
                StatoLiquidazione=company.fatturapa_rea_liquidation or None
            )

    def _setContatti(self, cr, uid, CedentePrestatore,
                     company, context=None):
        context = context or {}
        CedentePrestatore.Contatti = ContattiType(
            Telefono=self._wep_phone_number(company.partner_id.phone) or None,
            Fax=self._wep_phone_number(company.partner_id.fax) or None,
            Email=company.partner_id.email or None
        )

    def _setPubAdministrationRef(self, cr, uid, CedentePrestatore,
                                 company, context=None):
        context = context or {}
        if company.fatturapa_pub_administration_ref:
            CedentePrestatore.RiferimentoAmministrazione = (
                company.fatturapa_pub_administration_ref)

    def setCedentePrestatore(self, cr, uid, company, fatturapa, context=None):
        fatturapa.FatturaElettronicaHeader.CedentePrestatore = (
            CedentePrestatoreType())
        self._setDatiAnagraficiCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setSedeCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setAlboProfessionaleCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setStabileOrganizzazione(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        # FIXME: add Contacts
        self._setRea(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setContatti(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setPubAdministrationRef(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)

    def _setDatiAnagraficiCessionario(
            self, cr, uid, partner, fatturapa, context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
            DatiAnagrafici = DatiAnagraficiCessionarioType()
        if not partner.vat and not partner.fiscalcode:
            raise orm.except_orm(
                _('Error!'), _('Partner VAT and Fiscalcode not set.'))
        if partner.fiscalcode:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.CodiceFiscale = partner.fiscalcode
        if partner.vat:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                    IdPaese=partner.vat[0:2], IdCodice=partner.vat[2:])
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
            DatiAnagrafici.Anagrafica = AnagraficaType(
                Denominazione=partner.name)

        # not using for now
        #
        # Anagrafica = DatiAnagrafici.find('Anagrafica')
        # Nome = Anagrafica.find('Nome')
        # Cognome = Anagrafica.find('Cognome')
        # Titolo = Anagrafica.find('Titolo')
        # Anagrafica.remove(Nome)
        # Anagrafica.remove(Cognome)
        # Anagrafica.remove(Titolo)

        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code
        return True

    def _setSedeCessionario(self, cr, uid, partner, fatturapa, context=None):
        context = context or {}
        if not partner.street:
            raise orm.except_orm(
                _('Error!'), _('Customer street not set.'))
        if not partner.zip:
            raise orm.except_orm(
                _('Error!'), _('Customer ZIP not set.'))
        if not partner.city:
            raise orm.except_orm(
                _('Error!'), _('Customer city not set.'))
        if not partner.state_id:
            raise orm.except_orm(
                _('Error!'), _('Customer province not set.'))
        if not partner.country_id:
            raise orm.except_orm(
                _('Error!'), _('Customer country not set.'))

        # FIXME: manage address number in <NumeroCivico>
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.Sede = (
            IndirizzoType(
                Indirizzo=partner.street,
                CAP=partner.zip,
                Comune=partner.city[:60],
                Provincia=partner.state_id.code,
                Nazione=partner.country_id.code))
        return True

    def setRappresentanteFiscale(
            self, cr, uid, company, context=None):
        context = context or {}
        if company.fatturapa_tax_representative:
            # TODO: RappresentanteFiscale should be usefull for foreign
            # companies sending invoices to italian PA only
            raise orm.except_orm(
                _("Error"), _("RappresentanteFiscale not handled"))
            # partner = company.fatturapa_tax_representative

        # DatiAnagrafici = RappresentanteFiscale.find('DatiAnagrafici')

        # if not partner.fiscalcode:
            # raise orm.except_orm(
            # _('Error!'), _('RappresentanteFiscale Partner '
            # 'fiscalcode not set.'))

        # DatiAnagrafici.find('CodiceFiscale').text = partner.fiscalcode

        # if not partner.vat:
            # raise orm.except_orm(
            # _('Error!'), _('RappresentanteFiscale Partner VAT not set.'))
        # DatiAnagrafici.find(
            # 'IdFiscaleIVA/IdPaese').text = partner.vat[0:2]
        # DatiAnagrafici.find(
            # 'IdFiscaleIVA/IdCodice').text = partner.vat[2:]
        # DatiAnagrafici.find('Anagrafica/Denominazione').text = partner.name
        # if partner.eori_code:
            # DatiAnagrafici.find(
            # 'Anagrafica/CodEORI').text = partner.codiceEORI
        return True

    def setCessionarioCommittente(self, cr, uid, partner, fatturapa, context=None):
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente = (
            CessionarioCommittenteType())
        self._setDatiAnagraficiCessionario(cr, uid, partner, fatturapa,
                                           context=context)
        self._setSedeCessionario(cr, uid, partner, fatturapa, context=context)

    def setTerzoIntermediarioOSoggettoEmittente(
            self, cr, uid, company, context=None):
        context = context or {}
        if company.fatturapa_sender_partner:
            # TODO
            raise orm.except_orm(
                _("Error"),
                _("TerzoIntermediarioOSoggettoEmittente not handled"))
        return True

    def setSoggettoEmittente(self, cr, uid, context=None):
        context = context or {}
        # FIXME: this record is to be checked invoice by invoice
        # so a control is needed to verify that all invoices are
        # of type CC, TZ or internally created by the company

        # SoggettoEmittente.text = 'CC'
        return True

    def setDatiGeneraliDocumento(self, cr, uid, invoice, body, context=None):
        context = context or {}
        # TODO DatiSAL

        # TODO DatiDDT

        body.DatiGenerali = DatiGeneraliType()
        if not invoice.number:
            raise orm.except_orm(
                _('Error!'),
                _('Invoice does not have a number.'))

        TipoDocumento = 'TD01'
        if invoice.type == 'out_refund':
            TipoDocumento = 'TD04'
        ImportoTotaleDocumento = invoice.amount_total
        if invoice.split_payment:
            ImportoTotaleDocumento += invoice.amount_sp
        body.DatiGenerali.DatiGeneraliDocumento = DatiGeneraliDocumentoType(
            TipoDocumento=TipoDocumento,
            Divisa=invoice.currency_id.name,
            Data=invoice.date_invoice,
            Numero=invoice.number,
            ImportoTotaleDocumento='%.2f' % ImportoTotaleDocumento)

        # TODO: DatiRitenuta, DatiBollo, DatiCassaPrevidenziale,
        # ScontoMaggiorazione, Arrotondamento,

        if invoice.comment:
            # max length of Causale is 200
            caus_list = invoice.comment.split('\n')
            for causale in caus_list:
                # Remove non latin chars, but go back to unicode string,
                # as expected by String200LatinType
                causale = causale.encode(
                    'latin', 'ignore').decode('latin')
                body.DatiGenerali.DatiGeneraliDocumento.Causale.append(causale)

        if invoice.company_id.fatturapa_art73:
            body.DatiGenerali.DatiGeneraliDocumento.Art73 = 'SI'
        return True

    def setRelatedDocumentTypes(self, cr, uid, invoice, body,
                                context=None):
        linecount = 1
        for line in invoice.invoice_line:
            for related_document in line.related_documents:
                doc_type = RELATED_DOCUMENT_TYPES[related_document.type]
                documento = DatiDocumentiCorrelatiType()
                if related_document.name:
                    documento.IdDocumento = related_document.name
                if related_document.lineRef:
                    documento.RiferimentoNumeroLinea.append(linecount)
                if related_document.date:
                    documento.Data = related_document.date
                if related_document.numitem:
                    documento.NumItem = related_document.numitem
                if related_document.code:
                    documento.CodiceCommessaConvenzione = related_document.code
                if related_document.cup:
                    documento.CodiceCUP = related_document.cup
                if related_document.cig:
                    documento.CodiceCIG = related_document.cig
                getattr(body.DatiGenerali, doc_type).append(documento)
            linecount += 1
        for related_document in invoice.related_documents:
            doc_type = RELATED_DOCUMENT_TYPES[related_document.type]
            documento = DatiDocumentiCorrelatiType()
            if related_document.name:
                documento.IdDocumento = related_document.name
            if related_document.date:
                documento.Data = related_document.date
            if related_document.numitem:
                documento.NumItem = related_document.numitem
            if related_document.code:
                documento.CodiceCommessaConvenzione = related_document.code
            if related_document.cup:
                documento.CodiceCUP = related_document.cup
            if related_document.cig:
                documento.CodiceCIG = related_document.cig
            getattr(body.DatiGenerali, doc_type).append(documento)
        return True

    def setDatiTrasporto(self, cr, uid, invoice, body, context=None):
        context = context or {}
        return True

    def setDettaglioLinee(self, cr, uid, invoice, body, context=None):
        context = context or {}
        body.DatiBeniServizi = DatiBeniServiziType()
        # TipoCessionePrestazione not handled

        # TODO CodiceArticolo

        line_no = 1
        for line in invoice.invoice_line:
            if not line.invoice_line_tax_id:
                raise orm.except_orm(
                    _('Error'),
                    _("Invoice line %s does not have tax") % line.name)
            if len(line.invoice_line_tax_id) > 1:
                raise orm.except_orm(
                    _('Error'),
                    _("Too many taxes for invoice line %s") % line.name)
            aliquota = line.invoice_line_tax_id[0].amount * 100
            AliquotaIVA = '%.2f' % (aliquota)
            quantity_precision = dp.get_precision('Product Unit of Measure')(cr)[1]
            price_precision = dp.get_precision('Product Price')(cr)[1]
            DettaglioLinea = DettaglioLineeType(
                NumeroLinea=str(line_no),
                Descrizione=line.name.replace('\n', ' '),
                PrezzoUnitario='{price:.{precision}f}'.format(price=line.price_unit, precision=price_precision),
                Quantita="{quantity:.{precision}f}".format(quantity=line.quantity, precision=quantity_precision),
                UnitaMisura=line.uos_id and (
                    unidecode(line.uos_id.name)) or None,
                PrezzoTotale='%.2f' % line.price_subtotal,
                AliquotaIVA=AliquotaIVA)
            if line.discount:
                ScontoMaggiorazione = ScontoMaggiorazioneType(
                    Tipo='SC',
                    Percentuale='%.2f' % line.discount
                )
                DettaglioLinea.ScontoMaggiorazione.append(ScontoMaggiorazione)
            if aliquota == 0.0:
                if not line.invoice_line_tax_id[0].non_taxable_nature:
                    raise orm.except_orm(
                        _('Error'),
                        _("No 'nature' field for tax %s") %
                        line.invoice_line_tax_id[0].name)
                DettaglioLinea.Natura = line.invoice_line_tax_id[
                    0
                ].non_taxable_nature
            if line.admin_ref:
                DettaglioLinea.RiferimentoAmministrazione = line.admin_ref
            line_no += 1

            # not handled

            # el.remove(el.find('DataInizioPeriodo'))
            # el.remove(el.find('DataFinePeriodo'))
            # el.remove(el.find('Ritenuta'))
            # el.remove(el.find('AltriDatiGestionali'))

            body.DatiBeniServizi.DettaglioLinee.append(DettaglioLinea)

        return True

    def setDatiRiepilogo(self, cr, uid, invoice, body, context=None):
        context = context or {}
        tax_pool = self.pool['account.tax']
        for tax_line in invoice.tax_line:
            tax_id = self.pool['account.tax'].get_tax_by_invoice_tax(
                cr, uid, tax_line.name, context=context)
            tax = tax_pool.browse(cr, uid, tax_id, context=context)
            riepilogo = DatiRiepilogoType(
                AliquotaIVA='%.2f' % (tax.amount * 100),
                ImponibileImporto='%.2f' % tax_line.base,
                Imposta='%.2f' % tax_line.amount
            )
            if tax.amount == 0.0:
                if not tax.non_taxable_nature:
                    raise orm.except_orm(
                        _('Error'),
                        _("No 'nature' field for tax %s") % tax.name)
                riepilogo.Natura = tax.non_taxable_nature
                if not tax.law_reference:
                    raise orm.except_orm(
                        _('Error'),
                        _("No 'law reference' field for tax %s") % tax.name)
                riepilogo.RiferimentoNormativo = tax.law_reference
            if tax.payability:
                riepilogo.EsigibilitaIVA = tax.payability
            # TODO

            # el.remove(el.find('SpeseAccessorie'))
            # el.remove(el.find('Arrotondamento'))

            body.DatiBeniServizi.DatiRiepilogo.append(riepilogo)
        return True

    def setDatiPagamento(self, cr, uid, invoice, body, context=None):
        context = context or {}
        if invoice.payment_term:
            DatiPagamento = DatiPagamentoType()
            if not invoice.payment_term.fatturapa_pt_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Payment term %s does not have a linked fatturaPA '
                      'payment term') % invoice.payment_term.name)
            if not invoice.payment_term.fatturapa_pm_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Payment term %s does not have a linked fatturaPA '
                      'payment method') % invoice.payment_term.name)
            DatiPagamento.CondizioniPagamento = (
                invoice.payment_term.fatturapa_pt_id.code)
            move_line_pool = self.pool['account.move.line']
            invoice_pool = self.pool['account.invoice']
            payment_line_ids = invoice_pool.move_line_id_payment_get(
                cr, uid, [invoice.id])
            for move_line_id in payment_line_ids:
                move_line = move_line_pool.browse(
                    cr, uid, move_line_id, context=context)
                ImportoPagamento = '%.2f' % move_line.debit
                DettaglioPagamento = DettaglioPagamentoType(
                    ModalitaPagamento=(
                        invoice.payment_term.fatturapa_pm_id.code),
                    DataScadenzaPagamento=move_line.date_maturity,
                    ImportoPagamento=ImportoPagamento
                )
                if invoice.partner_bank_id:
                    DettaglioPagamento.IstitutoFinanziario = (
                        invoice.partner_bank_id.bank_name)
                    if invoice.partner_bank_id.acc_number:
                        DettaglioPagamento.IBAN = (
                            ''.join(
                                invoice.partner_bank_id.acc_number.split()
                            )
                        )
                    if invoice.partner_bank_id.bank_bic:
                        DettaglioPagamento.BIC = (
                            invoice.partner_bank_id.bank_bic)
                DatiPagamento.DettaglioPagamento.append(DettaglioPagamento)
            body.DatiPagamento.append(DatiPagamento)
        return True

    def setAttachments(self, cr, uid, invoice, body, context=None):
        context = context or {}
        if invoice.fatturapa_doc_attachments:
            for doc_id in invoice.fatturapa_doc_attachments:
                AttachDoc = AllegatiType(
                    NomeAttachment=doc_id.datas_fname,
                    Attachment=doc_id.datas
                )
                body.Allegati.append(AttachDoc)
        return True

    def setFatturaElettronicaHeader(self, cr, uid,
                                    company, partner, fatturapa,
                                    context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader = (
            FatturaElettronicaHeaderType())
        self.setDatiTrasmissione(cr, uid, company, partner, fatturapa,
                                 context=context)
        self.setCedentePrestatore(cr, uid, company, fatturapa, context=context)
        self.setRappresentanteFiscale(cr, uid, company, context=context)
        self.setCessionarioCommittente(
            cr, uid, partner, fatturapa, context=context)
        self.setTerzoIntermediarioOSoggettoEmittente(
            cr, uid, company, context=context)
        self.setSoggettoEmittente(cr, uid, context=context)

    def setFatturaElettronicaBody(
        self, cr, uid, inv, FatturaElettronicaBody, context=None
    ):
        context = context or {}
        self.setDatiGeneraliDocumento(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setRelatedDocumentTypes(cr, uid, inv, FatturaElettronicaBody,
                                     context=context)
        self.setDatiTrasporto(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDettaglioLinee(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDatiRiepilogo(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDatiPagamento(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setAttachments(
            cr, uid, inv, FatturaElettronicaBody, context=context)

    def getPartnerCompanyId(self, cr, uid, invoice_ids, context=None):
        context = context or {}
        invoice_model = self.pool['account.invoice']
        partner = False
        company = False
        invoices = invoice_model.browse(cr, uid, invoice_ids, context=context)
        for invoice in invoices:
            if not partner:
                partner = invoice.partner_id
            if invoice.partner_id != partner:
                raise orm.except_orm(
                    _('Error!'),
                    _('Invoices must belong to the same partner'))
            if not company:
                company = invoice.company_id
            if invoice.company_id != company:
                raise orm.except_orm(
                    _('Error!'),
                    _('Invoices must belong to the same company'))
        return company, partner

    def exportFatturaPA(self, cr, uid, ids, context=None):
        context = context or {}
        # self.setNameSpace()
        model_data_model = self.pool['ir.model.data']
        invoice_model = self.pool['account.invoice']

        invoice_ids = context.get('active_ids', False)
        company, partner = self.getPartnerCompanyId(cr, uid, invoice_ids,
                                                    context=context)
        if partner.is_pa:
            fatturapa = FatturaElettronica(versione='FPA12')
        else:
            fatturapa = FatturaElettronica(versione='FPR12')
        context_partner = context.copy()
        context_partner.update({'lang': partner.lang,
                                'company_id': company.id})
        try:
            self.setFatturaElettronicaHeader(cr, uid, 
                                             company, partner, fatturapa,
                                             context=context_partner)
            for invoice_id in invoice_ids:
                inv = invoice_model.browse(
                    cr, uid, invoice_id, context=context_partner)
                if inv.fatturapa_attachment_out_id:
                    raise orm.except_orm(
                        _("Error"),
                        _("Invoice %s has E-Fattura Export File already") % (
                            inv.number))
                invoice_body = FatturaElettronicaBodyType()
                self.setFatturaElettronicaBody(
                    cr, uid, inv, invoice_body, context=context_partner)
                fatturapa.FatturaElettronicaBody.append(invoice_body)
                # TODO DatiVeicoli
            number = self.setProgressivoInvio(cr, uid, fatturapa,
                                              context=context_partner)
        except (SimpleFacetValueError, SimpleTypeValueError) as e:
            raise orm.except_orm(
                _("XML SDI validation error"),
                (unicode(e)))

        attach_id = self.saveAttachment(cr, uid, fatturapa, number,
                                        context=context_partner)

        for invoice_id in invoice_ids:
            inv = invoice_model.browse(cr, uid, invoice_id)
            inv.write({'fatturapa_attachment_out_id': attach_id})

        view_rec = model_data_model.get_object_reference(
            cr, uid, 'l10n_it_einvoice_out',
            'view_fatturapa_out_attachment_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Export EInvoice",
            'view_id': [view_id],
            'res_id': attach_id,
            'view_mode': 'form',
            'res_model': 'fatturapa.attachment.out',
            'type': 'ir.actions.act_window',
            'context': context
        }
