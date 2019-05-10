# -*- coding: utf-8 -*-

import lxml.etree as ET
import xml.etree.ElementTree as etree
import re
import binascii
import logging
from io import BytesIO
from openerp import models, api, fields
from openerp.modules import get_module_resource
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

try:
    from asn1crypto import cms
except (ImportError, IOError) as err:
    _logger.debug(err)

re_base64 = re.compile(
    br'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$')


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    ftpa_preview_link = fields.Char(
        "Preview link", readonly=True, compute="_compute_ftpa_preview_link"
    )

    @api.multi
    def _compute_ftpa_preview_link(self):
        for att in self:
            att.ftpa_preview_link = '/fatturapa/preview/%s' % att.id

    @staticmethod
    def remove_xades_sign(xml):
        # Recovering parser is needed for files where strings like
        # xmlns:ds="http://www.w3.org/2000/09/xmldsig#&quot;"
        # are present: even if lxml raises
        # {XMLSyntaxError}xmlns:ds:
        # 'http://www.w3.org/2000/09/xmldsig#"' is not a valid URI
        # such files are accepted by SDI
        recovering_parser = ET.XMLParser(recover=True)
        root = ET.XML(xml, parser=recovering_parser)
        for elem in root.iter('*'):
            if elem.tag.find('Signature') > -1:
                elem.getparent().remove(elem)
                break
        return ET.tostring(root)

    @staticmethod
    def strip_xml_content(xml):
        recovering_parser = ET.XMLParser(recover=True)
        root = ET.XML(xml, parser=recovering_parser)
        for elem in root.iter('*'):
            if elem.text is not None:
                elem.text = elem.text.strip()
        return ET.tostring(root)

    @staticmethod
    def remove_additional_namespaces(xml):
        root = etree.fromstring(xml)
        return etree.tostring(root)

    @staticmethod
    def sanitize_lines(xml):
        root = ET.XML(xml)

        for line in root.find('FatturaElettronicaBody').find('DatiBeniServizi').findall('DettaglioLinee'):
            elem = line.find('UnitaMisura')
            if elem is not None and not elem.text:
                line.remove(elem)

            elem = line.find('Descrizione')
            if elem is not None and not elem.text:
                elem.text = '---'

        return ET.tostring(root)

    @staticmethod
    def remove_empty_attachment(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('Allegati') > -1:
                attachment_elem = elem.find('Attachment')
                if attachment_elem is not None and not attachment_elem.text:
                    elem.getparent().remove(elem)

        return ET.tostring(root)

    @staticmethod
    def remove_empty_id_document(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('DatiOrdineAcquisto') > -1:
                document_elem = elem.find('IdDocumento')
                if document_elem is not None and not document_elem.text:
                    # IdDocument can't be empty
                    document_elem.text = 'IdDocumento'

        return ET.tostring(root)

    @staticmethod
    def set_fake_address(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('CedentePrestatore') > -1:
                sede_elem = elem.find('Sede')
                address_elem = sede_elem.find('Indirizzo')
                if address_elem is not None and not address_elem.text:
                    address_elem.text = '-'

                municipality_elem = sede_elem.find('Comune')
                if municipality_elem is not None and not municipality_elem.text:
                    municipality_elem.text = '-'

        return ET.tostring(root)

    def sanitize(self, xml_string):
        xml_string = self.remove_additional_namespaces(xml_string)
        xml_string = self.remove_xades_sign(xml_string)
        xml_string = self.strip_xml_content(xml_string)
        xml_string = self.sanitize_lines(xml_string)
        xml_string = self.set_fake_address(xml_string)
        xml_string = self.remove_empty_attachment(xml_string)
        xml_string = self.remove_empty_id_document(xml_string)

        return xml_string

    @staticmethod
    def extract_cades(data):
        info = cms.ContentInfo.load(data)
        return info['content']['encap_content_info']['content'].native

    def get_xml_string(self):
        try:
            data = self.datas.decode('base64')
        except binascii.Error as e:
            raise UserError(
                _(
                    'Corrupted attachment %s.'
                ) % e.args
            )

        if re_base64.match(data) is not None:
            try:
                data = data.decode('base64')
            except binascii.Error as e:
                raise UserError(
                    _(
                        'Base64 encoded file %s.'
                    ) % e.args
                )

        # Amazon sends xml files without <?xml declaration,
        # so they cannot be easily detected using a pattern.
        # We first try to parse as asn1, if it fails we assume xml

        # asn1crypto parser will raise ValueError
        # if the asn1 cannot be parsed
        # KeyError is raised if one of the needed key is not
        # in the asn1 structure (info->content->encap_content_info->content)
        try:
            data = self.extract_cades(data)
        except (ValueError, KeyError):
            pass

        try:
            return self.sanitize(data)
        # cleanup_xml calls root.iter(), but root is None if the parser fails
        # Invalid xml 'NoneType' object has no attribute 'iter'
        except AttributeError as e:
            raise UserError(
                _(
                    'Invalid xml %s.'
                ) % e.args
            )

    def get_fattura_elettronica_preview(self):
        xsl_path = get_module_resource(
            'l10n_it_fatturapa', 'data', 'fatturaordinaria_v1.2.1.xsl')
        xslt = ET.parse(xsl_path)
        xml_string = self.get_xml_string()
        xml_file = BytesIO(xml_string)
        recovering_parser = ET.XMLParser(recover=True)
        dom = ET.parse(xml_file, parser=recovering_parser)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        return ET.tostring(newdom, pretty_print=True)
