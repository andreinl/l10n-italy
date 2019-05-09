# -*- coding: utf-8 -*-
#
# Copyright 2014    - Davide Corio <davide.corio@lsweb.it>
# Copyright 2015    - Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
# Copyright 2018-19 - Odoo Italia Associazione <https://www.odoo-italia.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
import re
import base64
import logging
from xml.sax.saxutils import escape

from openerp import fields, models, api
from openerp.tools.translate import _
from openerp.osv import orm
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp

from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2 import (
    AllegatiType,
    AnagraficaType,
    CedentePrestatoreType,
    CessionarioCommittenteType,
    ContattiTrasmittenteType,
    ContattiType,
    CodiceArticoloType,
    DatiAnagraficiCedenteType,
    DatiAnagraficiCessionarioType,
    DatiAnagraficiRappresentanteType,
    DatiAnagraficiTerzoIntermediarioType,
    DatiBeniServiziType,
    DatiDocumentiCorrelatiType,
    DatiGeneraliDocumentoType,
    DatiGeneraliType,
    DatiPagamentoType,
    DatiRiepilogoType,
    DatiTrasmissioneType,
    DettaglioLineeType,
    DettaglioPagamentoType,
    FatturaElettronica,
    FatturaElettronicaBodyType,
    FatturaElettronicaHeaderType,
    IdFiscaleType,
    IndirizzoType,
    IscrizioneREAType,
    RappresentanteFiscaleType,
    RappresentanteFiscaleCessionarioType,
    ScontoMaggiorazioneType,
    TerzoIntermediarioSoggettoEmittenteType,)
from openerp.addons.l10n_it_einvoice_base.models.account import (
    RELATED_DOCUMENT_TYPES
)


_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
    from pyxb.exceptions_ import SimpleFacetValueError, SimpleTypeValueError
except ImportError as err:
    _logger.debug(err)

STYLESHEET = 'fatturapa_v1.2.xsl'
CODE_NONE_IT = '0000000'
CODE_NONE_EU = 'XXXXXXX'
PAYTYPE_BNK_CUSTOMER = ('MP11', 'MP12', 'MP16', 'MP17', 'MP19', 'MP20', 'MP21')
PAYTYPE_BNK_COMPANY = ('MP05', 'MP07', 'MP08', 'MP13', 'MP18')
XML_ESCAPE = {
    u'\'': u' ',
    u'\n': u' ',
    u'\r': u' ',
    u'\t': u' ',
    u'€': u'EUR',
    u'©': u'(C)',
    u'®': u'(R)',
    # u'à': u'&agrave;',
    # u'á': u'&aacute;',
    # u'è': u'&egrave;',
    # u'é': u'&eacute;',
    # u'ì': u'&igrave;',
    # u'í': u'&iacute;',
    # u'ò': u'&ograve;',
    # u'ó': u'&oacute;',
    # u'ù': u'&ugrave;',
    # u'ú': u'&uacute;',
    # u'°': u'&deg;',
    u'«': u'&laquo;',
    u'»': u'&raquo;',
    u'Ø': u'&Oslash;',
    u'ø': u'&oslash;',
    u'ß': u'&szlig;',
}
IBAN_PATTERN = re.compile('[A-Z]{2}[0-9]{2}[A-Z][0-9A-Z]+')
INHERITED_FLDS = ['codice_destinatario', 'name']


class WizardExportFatturapa(models.TransientModel):
    _name = "wizard.export.fatturapa"
    _description = "Export E-invoice"

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
            raise UserError(
                _('Company %s TIN not set.') % company.name)
        if (
            company.fatturapa_sender_partner and not
            company.fatturapa_sender_partner.vat
        ):
            raise UserError(
                _('Partner %s TIN not set.')
                % company.fatturapa_sender_partner.name
            )
        vat = company.vat
        if company.fatturapa_sender_partner:
            vat = company.fatturapa_sender_partner.vat
        vat = self.__wep_vat(vat)
        attach_model = self.pool['fatturapa.attachment.out']

        invoice_xml = fatturapa.toDOM().toprettyxml(encoding="latin1").replace(
            '<?xml version="1.0" encoding="latin1"?>',
            """<?xml version="1.0" encoding="latin1"?>
<?xml-stylesheet type="text/xsl" href="{xsl}"?>""".format(xsl=STYLESHEET))

        attach_vals = {
            'name': '%s_%s.xml' % (vat, str(number)),
            'datas_fname': '%s_%s.xml' % (vat, str(number)),
            'datas': base64.encodestring(invoice_xml)
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

        fatturapa_sequence = company.fatturapa_sequence_id
        if not fatturapa_sequence:
            raise UserError(
                _('FatturaPA sequence not configured.'))
        sequence_model = self.pool['ir.sequence']
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
            raise UserError(msg)
        return number

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
        return wep_phone.strip()

    def _wep_text(self, text):
        """"Do xml escape to avoid error StringLatinType"""
        # text.encode('latin', 'ignore').decode('latin')
        if text:
            return escape(unidecode(text), XML_ESCAPE).strip()
        return text

    def __wep_vat(self, vat):
        if vat:
            return vat.replace(
                ' ', '').replace('.', '').replace('-', '').upper()
        return vat

    def _get_partner_field(self, cr, uid, partner, parent, field):
        value = False
        if field == 'company_type':
            if partner.name:
                value = partner.is_company or (parent and parent.is_company)
            else:
                value = (parent and parent.is_company) or True
            if value:
                value = 'company'
            else:
                value = 'person'
        elif field in partner:
            value = partner[field] or (parent and parent[field])
        return value

    def _setIdTrasmittente(self, cr, uid, company, fatturapa, context=None):
        if not company.country_id:
            raise UserError(
                _('Company Country not set.'))
        IdPaese = company.country_id.code

        IdCodice = company.partner_id.fiscalcode
        if not IdCodice and company.vat:
            IdCodice = company.vat[2:]
        if not IdCodice:
            raise UserError(
                _('Company does not have fiscal code or VAT number.'))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            IdTrasmittente = IdFiscaleType(
                IdPaese=IdPaese, IdCodice=IdCodice)

        return True

    def _getFormatoTrasmissione(self, cr, uid, partner, parent):
        if self._get_partner_field(cr, uid, partner, parent, 'is_pa'):
            return 'FPA12'
        else:
            return 'FPR12'

    def _setFormatoTrasmissione(self, cr, uid, partner, parent, fatturapa,
                                context=None):
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
                FormatoTrasmissione = self._getFormatoTrasmissione(cr, uid,
                                                                   partner,
                                                                   parent)
        return True

    def _setCodiceDestinatario(self, cr, uid, partner, parent, fatturapa,
                               context=None):
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

        if self._get_partner_field(cr, uid, partner, parent, 'is_pa'):
            code = self._get_partner_field(
                cr, uid, partner, parent, 'ipa_code')
            if not code:
                raise UserError(_(
                    "Partner %s is PA but has no IPA code"
                ) % partner.name)
        else:
            code = self._get_partner_field(
                cr, uid, partner, parent, 'codice_destinatario')
            if not code or code == '0000000':
                vat = self._get_partner_field(cr, uid, partner, parent, 'vat')
                fiscalcode = self._get_partner_field(
                    cr, uid, partner, parent, 'fiscalcode')

                if vat or fiscalcode:
                    if partner.country_id and partner.country_id.code == 'IT':
                        code = '0000000'
                        pec_destinatario = self._get_partner_field(
                            cr, uid, partner, parent, 'pec_destinatario')
                        if pec_destinatario:
                            # if validate_email(pec_destinatario):
                            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.PECDestinatario = pec_destinatario
                            # else:
                            #     raise orm.except_orm(_('Error!'),
                            #                          _('{pec_email} is not correct').format(pec_email=pec_destinatario))
                        elif vat:
                            raise UserError(
                                _('No PEC find for Partner: {partner}').format(partner=partner.name))
                    elif partner.country_id and not partner.country_id.code == 'IT':
                        code = 'XXXXXXX'
                    else:
                        raise UserError(
                            _('No Address find for Partner: {partner}').format(partner=partner.name))
                else:
                    raise UserError(
                        _('Please set Fiscal Code or VAT for partner {}').format(partner.name))
            elif len(code) != 7:
                if ' ' in code:
                    raise UserError(
                        _('Space char in Recipient Code \'{code}\'').format(code=code)
                    )
                else:
                    raise UserError(
                        _('Recipient Code {code} length is {dimension}, it should be 7').format(code=code, dimension=len(code)))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.CodiceDestinatario = code.upper()

        return True

    def _setContattiTrasmittente(self, cr, uid, company, fatturapa,
                                 context=None):
        # context = context or {}
        if not company.phone:
            raise UserError(
                _('Company Telephone number not set.'))
        Telefono = self._wep_phone_number(company.phone)

        if not company.email:
            raise UserError(
                _('Company Email not set.'))

        Email = company.einvoice_email or company.email

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            ContattiTrasmittente = ContattiTrasmittenteType(
                Telefono=Telefono, Email=Email)
        return True

    def setDatiTrasmissione(self, cr, uid,
                            company, partner, parent, fatturapa, 
                            context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione = (
            DatiTrasmissioneType())
        self._setIdTrasmittente(cr, uid, company, fatturapa, context=context)
        self._setFormatoTrasmissione(cr, uid, partner, parent, fatturapa,
                                     context=context)
        self._setCodiceDestinatario(cr, uid, partner, parent, fatturapa,
                                    context=context)
        self._setContattiTrasmittente(cr, uid, company, fatturapa,
                                      context=context)

    def _setDatiAnagraficiCedente(self, cr, uid, CedentePrestatore,
                                  company, context=None):
        # context = context or {}
        if not company.vat:
            raise UserError(
                _('Company TIN not set.'))
        CedentePrestatore.DatiAnagrafici = DatiAnagraficiCedenteType()
        fatturapa_fp = company.fatturapa_fiscal_position_id
        if not fatturapa_fp:
            raise UserError(
                _('E-invoice fiscal position not set.'))
        CedentePrestatore.DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
            IdPaese=company.country_id.code, IdCodice=company.vat[2:])
        CedentePrestatore.DatiAnagrafici.Anagrafica = AnagraficaType(
            Denominazione=company.name)

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
            raise UserError(
                    _('Your company Street is not set.'))
        if not company.zip:
            raise UserError(
                _('Your company ZIP is not set.'))
        if not company.city:
            raise UserError(
                _('Your company City is not set.'))
        if not company.partner_id.state_id:
            raise UserError(
                _('Province not set.'))
        if not company.country_id:
            raise UserError(
                _('Your company Country is not set.'))
        # TODO: manage address number in <NumeroCivico>
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
        # if company.fatturapa_stabile_organizzazione:
        if False:
            stabile_organizzazione = company.fatturapa_stabile_organizzazione
            if not stabile_organizzazione.street:
                raise UserError(
                    _('Street is not set for %s.') %
                    stabile_organizzazione.name)
            if not stabile_organizzazione.zip:
                raise UserError(
                    _('ZIP is not set for %s.') %
                    stabile_organizzazione.name)
            if not stabile_organizzazione.city:
                raise UserError(
                    _('City is not set for %s.') %
                    stabile_organizzazione.name)
            if not stabile_organizzazione.country_id:
                raise UserError(
                    _('Country is not set for %s.') %
                    stabile_organizzazione.name)
            CedentePrestatore.StabileOrganizzazione = IndirizzoType(
                Indirizzo=stabile_organizzazione.street,
                CAP=stabile_organizzazione.zip,
                Comune=stabile_organizzazione.city,
                Nazione=stabile_organizzazione.country_id.code)
            if stabile_organizzazione.state_id:
                CedentePrestatore.StabileOrganizzazione.Provincia = (
                    stabile_organizzazione.state_id.code)
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

    def setCedentePrestatore(
            self, cr, uid, company, partner, parent, fatturapa, context=None):
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
            self, cr, uid, partner, parent, fatturapa, context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
            DatiAnagrafici = DatiAnagraficiCessionarioType()
        vat = self._get_partner_field(cr, uid, partner, parent, 'vat')
        fiscalcode = self._get_partner_field(cr, uid, partner, parent, 'fiscalcode')
        if vat:
            vat = self.__wep_vat(vat)
            if vat[0:3] != 'IT9':
                fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                    DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                        IdPaese=vat[0:2],
                        IdCodice=vat[2:])
        else:
            vat = ''
        if fiscalcode:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.CodiceFiscale = fiscalcode
        elif vat[0:3] == 'IT9':
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.CodiceFiscale = vat[2:]

        company_type = self._get_partner_field(cr, uid,
                                               partner, parent, 'company_type')
        if company_type == 'company':
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.Anagrafica = AnagraficaType(
                    Denominazione=self._get_partner_field(
                        cr, uid, partner, parent, 'name'))
        elif company_type == 'person':
            if not partner.lastname or not partner.firstname:
                raise UserError(
                    _("Partner %s must have name and surname.") %
                    partner.name)
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.Anagrafica = AnagraficaType(
                    Cognome=partner.lastname,
                    Nome=partner.firstname
                )
        eori_code = self._get_partner_field(cr, uid, partner, parent, 'eori_code')
        if eori_code:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.Anagrafica.CodEORI = eori_code

        return True

    def _setDatiAnagraficiRappresentanteFiscale(
            self, partner, parent, fatturapa):
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale = (
            RappresentanteFiscaleType())
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
            DatiAnagrafici = DatiAnagraficiRappresentanteType()
        if not partner.vat and not partner.fiscalcode:
            raise UserError(
                _('VAT number and fiscal code are not set for %s.') %
                partner.name)
        if partner.fiscalcode:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.CodiceFiscale = partner.fiscalcode
        if partner.vat:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                    IdPaese=partner.vat[0:2], IdCodice=partner.vat[2:])
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
            DatiAnagrafici.Anagrafica = AnagraficaType(
                Denominazione=partner.name)
        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code
        return True

    def _setTerzoIntermediarioOSoggettoEmittente(
            self, partner, parent, fatturapa):
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente = (
                TerzoIntermediarioSoggettoEmittenteType()
            )
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente.\
            DatiAnagrafici = DatiAnagraficiTerzoIntermediarioType()
        if not partner.vat and not partner.fiscalcode:
            raise orm.except_orm(E,
                _('Partner VAT number and fiscal code are not set.'))
        if partner.fiscalcode:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.CodiceFiscale = partner.fiscalcode
        if partner.vat:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                    IdPaese=partner.vat[0:2], IdCodice=partner.vat[2:])
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente.\
            DatiAnagrafici.Anagrafica = AnagraficaType(
                Denominazione=partner.name)
        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code
        fatturapa.FatturaElettronicaHeader.SoggettoEmittente = 'TZ'
        return True

    def _setSedeCessionario(self, cr, uid, partner, parent, fatturapa,
                            context=None):
        context = context or {}

        country_id = self._get_partner_field(
            cr, uid, partner, parent, 'country_id')
        if not country_id:
            raise orm.except_orm(E,
                _('Customer country is not set.'))
        street = self._get_partner_field(cr, uid, partner, parent, 'street')
        zip = self._get_partner_field(cr, uid, partner, parent, 'zip')
        city = self._get_partner_field(cr, uid, partner, parent, 'city')
        state_id = self._get_partner_field(cr, uid, partner, parent, 'state_id')
        if not street:
            raise orm.except_orm(E,
                _('Customer street is not set.'))
        codice_destinatario = self._get_partner_field(
            cr, uid, partner, parent, 'codice_destinatario')
        if codice_destinatario != 'XXXXXXX' and not zip:
            raise orm.except_orm(E,
                _('Customer ZIP is not set.'))
        if not city:
            raise orm.except_orm(E,
                _('Customer city is not set.'))
        if codice_destinatario != 'XXXXXXX' and not state_id:
            raise orm.except_orm(E,
                _('Customer province is not set.'))

        if codice_destinatario != 'XXXXXXX':
            zip = zip
        else:
            zip = '00000'
        if codice_destinatario != 'XXXXXXX':
            province = state_id.code
        else:
            province = 'EE'
        # TODO: manage address number in <NumeroCivico>
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.Sede = (
            IndirizzoType(
                Indirizzo=street,
                CAP=zip,
                Comune=city[:60],
                Provincia=province,
                Nazione=country_id.code))
        return True

    def setRappresentanteFiscale(
            self, cr, uid, company, fatturapa, context=None):
        context = context or {}
        if company.fatturapa_tax_representative:
            self._setDatiAnagraficiRappresentanteFiscale(
                company.fatturapa_tax_representative, fatturapa)
        return True

    def setCessionarioCommittente(self, cr, uid, partner, parent, fatturapa,
                                  context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente = (
            CessionarioCommittenteType())
        self._setDatiAnagraficiCessionario(cr, uid, partner, parent, fatturapa,
                                           context=context)
        self._setSedeCessionario(cr, uid, partner, parent, fatturapa, context=context)

    def setTerzoIntermediarioOSoggettoEmittente(
            self, cr, uid, company, fatturapa, context=None):
        context = context or {}
        if company.fatturapa_sender_partner:
            self._setTerzoIntermediarioOSoggettoEmittente(
                company.fatturapa_sender_partner, fatturapa)
        return True

    def setTipoDocumento(self, invoice):
        if invoice.invoice_type_id:
            TipoDocumento = invoice.invoice_type_id.code
        elif invoice.type == 'out_refund':
            TipoDocumento = 'TD04'
        else:
            TipoDocumento = 'TD01'
        return TipoDocumento

    def setDatiGeneraliDocumento(self, cr, uid, invoice, body, context=None):
        context = context or {}
        # TODO DatiSAL

        # TODO DatiDDT

        body.DatiGenerali = DatiGeneraliType()
        if not invoice.number:
            raise UserError(
                _('Invoice does not have a number.'))

        TipoDocumento = self.setTipoDocumento(invoice)
        ImportoTotaleDocumento = invoice.amount_total
        # /!\ OCA split payment has total_amount w/o VAT e amount_sp positive
        # OIA split payment has total_amount with VTA and amount_sp negative
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
                if not causale:
                    continue
                # Remove non latin chars, but go back to unicode string,
                # as expected by String200LatinType
                # causale = causale.encode(
                #     'latin', 'ignore').decode('latin')
                causale = self._wep_text(causale)
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

    def setDatiDDT(self, invoice, body):
        return True

    def _get_prezzo_unitario(self, line):
        res = line.price_unit
        if (
            line.invoice_line_tax_id and
            line.invoice_line_tax_id[0].price_include
        ):
            res = line.price_unit / (
                1 + (line.invoice_line_tax_id[0].amount / 100))
        return res

    def setDettaglioLinee(self, cr, uid, invoice, body, context=None):
        context = context or {}
        body.DatiBeniServizi = DatiBeniServiziType()
        # TipoCessionePrestazione not handled

        # TODO CodiceArticolo

        line_no = 1
        uom_precision = max(2, dp.get_precision('Product Unit of Measure')(cr)[1])
        quantity_precision = dp.get_precision('Product Unit of Measure')(cr)[1]
        price_precision = dp.get_precision('Product Price')(cr)[1]
        for line in invoice.invoice_line:
            if not line.invoice_line_tax_id:
                raise UserError(
                    _("Invoice line %s does not have tax") % line.name)
            if len(line.invoice_line_tax_id) > 1:
                raise UserError(
                    _("Too many taxes for invoice line %s") % line.name)

            aliquota = line.invoice_line_tax_id[0].amount * 100
            AliquotaIVA = '%.2f' % (aliquota)
            prezzo_unitario = self._get_prezzo_unitario(line)

            DettaglioLinea = DettaglioLineeType(
                NumeroLinea=str(line_no),
                Descrizione=self._wep_text(line.name.replace('\n', ' ')),
                PrezzoUnitario='{price:.{precision}f}'.format(price=prezzo_unitario, precision=price_precision),
                Quantita="{quantity:.{precision}f}".format(quantity=line.quantity, precision=quantity_precision),
                UnitaMisura=line.uos_id and (
                    unidecode(line.uos_id.name)) or None,
                PrezzoTotale='%.2f' % line.price_subtotal,
                AliquotaIVA=AliquotaIVA
            )
            if line.discount:
                ScontoMaggiorazione = ScontoMaggiorazioneType(
                    Tipo='SC',
                    Percentuale='%.2f' % line.discount
                )
                DettaglioLinea.ScontoMaggiorazione.append(ScontoMaggiorazione)
            if aliquota == 0.0:
                if not line.invoice_line_tax_id[0].non_taxable_nature:
                    raise UserError(
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
                cr, uid, tax_line, context=context)
            tax = tax_pool.browse(cr, uid, tax_id, context=context)
            riepilogo = DatiRiepilogoType(
                AliquotaIVA='%.2f' % (tax.amount * 100),
                ImponibileImporto='%.2f' % tax_line.base,
                Imposta='%.2f' % tax_line.amount
            )
            if tax.amount == 0.0:
                if not tax.non_taxable_nature:
                    raise UserError(
                        _("No 'nature' field for tax %s") % tax.name)
                riepilogo.Natura = tax.non_taxable_nature
                if not tax.law_reference:
                    raise UserError(
                        _("No 'law reference' field for tax %s") % tax.name)
                riepilogo.RiferimentoNormativo = tax.law_reference
            if tax.payability:
                riepilogo.EsigibilitaIVA = tax.payability
            # TODO

            # el.remove(el.find('SpeseAccessorie'))
            # el.remove(el.find('Arrotondamento'))

            body.DatiBeniServizi.DatiRiepilogo.append(riepilogo)
        return True

    def setDatiBanca(self, DettaglioPagamento, bank_id, company=None):
        if not bank_id and company:
            for bank in company.partner_id.bank_ids:
                if bank.acc_number and IBAN_PATTERN.match(bank.acc_number):
                    bank_id = bank
                    break
        if bank_id:
            if bank_id.bank_name:
                DettaglioPagamento.IstitutoFinanziario = (
                    bank_id.bank_name)
            if bank_id.acc_number:
                DettaglioPagamento.IBAN = (
                    bank_id.acc_number.replace(' ', '')
                )
            if bank_id.bank_bic:
                DettaglioPagamento.BIC = (
                    bank_id.bank_bic)
        return DettaglioPagamento

    def setDatiPagamento(self, cr, uid, invoice, body, context=None):
        context = context or {}
        if invoice.payment_term:
            DatiPagamento = DatiPagamentoType()
            if not invoice.payment_term.fatturapa_pt_id:
                raise UserError(
                    _('Payment term %s does not have a linked fatturaPA '
                      'payment term') % invoice.payment_term.name)
            if not invoice.payment_term.fatturapa_pm_id:
                raise UserError(
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
                                    company, partner, parent, fatturapa,
                                    context=None):
        context = context or {}
        fatturapa.FatturaElettronicaHeader = (
            FatturaElettronicaHeaderType())
        self.setDatiTrasmissione(cr, uid, company, partner, parent, fatturapa,
                                 context=context)
        self.setCedentePrestatore(cr, uid, company, partner, parent, fatturapa,
                                  context=context)
        self.setRappresentanteFiscale(cr, uid, company, fatturapa,
                                      context=context)
        self.setCessionarioCommittente(
            cr, uid, partner, parent, fatturapa, context=context)
        self.setTerzoIntermediarioOSoggettoEmittente(
            cr, uid, company, fatturapa, context=context)
        self.setTerzoIntermediarioOSoggettoEmittente(
            cr, uid, company, fatturapa, context=context)

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
        parent = False
        company = False
        invoices = invoice_model.browse(cr, uid, invoice_ids, context=context)
        for invoice in invoices:
            if not partner:
                partner = invoice.partner_id
            if invoice.partner_id != partner:
                raise UserError(
                    _('Invoices must belong to the same partner'))
            if not company:
                company = invoice.company_id
            if invoice.company_id != company:
                raise UserError(
                    _('Invoices must belong to the same company'))
        if partner and partner.type == 'invoice':
            parent = partner.parent_id
        return company, partner, parent

    def group_invoices_by_partner(self, cr, uid, context=None):
        context = context or {}
        invoice_ids = context.get('active_ids', False)
        res = {}
        for invoice in self.pool['account.invoice'].browse(cr, uid,
                                                           invoice_ids):
            if invoice.partner_id.id not in res:
                res[invoice.partner_id.id] = []
            res[invoice.partner_id.id].append(invoice.id)
        return res

    def exportFatturaPA(self, cr, uid, ids, context=None):
        context = context or {}
        model_data_model = self.pool['ir.model.data']
        invoice_model = self.pool['account.invoice']

        invoices_by_partner = self.group_invoices_by_partner(
            cr, uid, context=context)
        # attachments = self.pool['fatturapa.attachment.out']
        for partner_id in invoices_by_partner:
            invoice_ids = invoices_by_partner[partner_id]
            company, partner, parent = self.getPartnerCompanyId(
                cr, uid, invoice_ids)
            fatturapa = FatturaElettronica(
                versione=self._getFormatoTrasmissione(cr, uid,
                                                      partner,
                                                      parent))
            context_partner = context.copy()
            context_partner.update({'lang': partner.lang,
                                    'company_id': company.id})
            try:
                self.setFatturaElettronicaHeader(cr, uid, 
                                                 company, partner, parent, fatturapa,
                                                 context=context_partner)
                for invoice_id in invoice_ids:
                    inv = invoice_model.browse(
                        cr, uid, invoice_id, context=context_partner)
                    if inv.fatturapa_attachment_out_id:
                        raise orm.except_orm(E,
                            _("Invoice %s has e-invoice export file already.") % (
                                inv.number))
                    invoice_body = FatturaElettronicaBodyType()
                    self.setFatturaElettronicaBody(
                        cr, uid, inv, invoice_body, context=context_partner)
                    fatturapa.FatturaElettronicaBody.append(invoice_body)
                    # TODO DatiVeicoli

                number = self.setProgressivoInvio(cr, uid, fatturapa,
                                                  context=context_partner)
            except (SimpleFacetValueError, SimpleTypeValueError) as e:
                raise UserError(
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
