# -*- coding: utf-8 -*-
#    Copyright (C) 2017    SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# [2017: SHS-AV s.r.l.] First version
{
    'name': 'Comunicazione periodica IVA',
    'version': '7.0.0.1.12',
    'category': 'Generic Modules/Accounting',
    'author': 'SHS-AV s.r.l., Odoo Italia Associazione',
    'website': 'https://odoo-italia.org',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_ade',
        'l10n_it_fiscalcode',
        'account_invoice_entry_date',
        'l10n_it_vat_registries',
        # 'l10n_it_account'
    ],
    'data': ['views/add_period.xml',
             'views/remove_period.xml',
             'views/account_view.xml',
             'views/wizard_export_view.xml',
             'security/ir.model.access.csv',
             'communication_workflow.xml',
             ],
    'installable': True,
    'external_dependencies': {
        'python': ['pyxb', 'unidecode'],
    },
    'description': r'''
Overview / Panoramica
=====================

|en| Generate xml file for sending to Agenzia delle Entrate, kwnown as Spesometro.

|

|it| Gestisce la Comunicazione periodica IVA con l'elenco delle fatture emesse e
ricevute e genera il file da inviare all'Agenzia delle Entrate.
Questo obbligo è conosciuto anche come Spesometro light 2018 e sostistuisce i
precedenti obbblighi chiamati Spesometro e Spesometro 2017.

Il softwware permette di operare in modalità 2017 per rigenerare eventuali file
in formato 2017. Per eseguire questa funzione, prima di avviare Odoo eseguire
la seguente istruzione:

::

     export SPESOMETRO_VERSION=2.0

|

Features / Caratteristiche
--------------------------

+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Feature / Funzione                                | Status     | Notes / Note                                                        |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture clienti e fornitori detraibili            | |check|    | Fatture ordinarie                                                   |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture fornitori indetraibili                    | |check|    | Tutte le percentuali di indetraibilità                              |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture a privati senza Partita IVA               | |check|    | Necessario codice fiscale                                           |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture semplificata                              | |check|    | Per clienti senza PI ne CF                                          |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture senza IVA                                 | |check|    | Fatture esenti, NI, escluse, eccetera                               |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Escludi importi Fuori Campo IVA                   | |check|    | Totale fattura in Comunicazione può essere diverso da registrazione |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Controlla CAP e provincia Italia in comunicazione | |check|    | Da nazione, oppure da partita IVA oppure Italia                     |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Converti CF no Italia in comunicazione            | |check|    | Da nazione, oppure da partita IVA oppure Italia                     |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Controlli dati anagrafici                         | |check|    | Controlli Agenzia Entrate                                           |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Conversione utf-8                                 | |check|    | Lo Spesometro 2017 richiedeva ISO-Latin1                            |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| IVA differita                                     | |check|    | Da codice imposte                                                   |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| IVA da split-payment                              | |check|    | Da codice imposte                                                   |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Ignora autofatture                                | |check|    | Esclusione tramite sezionale                                        |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Ignora corrispettivi                              | |check|    | Esclusione tramite sezionale                                        |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Ignora avvisi di parcella                         | |check|    | Esclusione tramite sezionale                                        |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Identificazione Reverse Charge                    | |check|    | Da codice imposte                                                   |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture vendita UE                                | |check|    | Inserite in spesometro                                              |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture vendita extra-UE                          | |check|    | Inserite in spesometro                                              |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture acq. intra-UE beni                        | |no_check| | In fase di rilascio                                                 |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Fatture acq. intra-UE servizi                     | |check|    | Tutte le fatture EU (provvisoriamente)                              |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Rettifica dichiarazione                           | |no_check| | In fase di rilascio                                                 |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Nomenclatura del file                             | |check|    |                                                                     |
+---------------------------------------------------+------------+---------------------------------------------------------------------+
| Dimensioni del file                               | |no_check| | Nessuna verifica anche futura                                       |
+---------------------------------------------------+------------+---------------------------------------------------------------------+


|

Certifications / Certificazioni
-------------------------------

+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+------------+-----------------------------------------------------------+
| Logo                                                                                                                                                                                                                      | Ente/Certificato                                                                                                                                                                                              | Data inizio | Da fine    | Note                                                      |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+------------+-----------------------------------------------------------+
| [![xml_schema](https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/icons/xml-schema.png)](https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md)                      | [ISO + Agenzia delle Entrate](http://www.agenziaentrate.gov.it/wps/content/Nsilib/Nsi/Strumenti/Specifiche+tecniche/Specifiche+tecniche+comunicazioni/Fatture+e+corrispettivi+ST/)                            | 01-10-2017  | 31-12-2018 | Validazione contro schema xml                             |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+------------+-----------------------------------------------------------+
| [![DesktopTelematico](https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/icons/DesktopTelematico.png)](https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/DesktopTelematico.md) | [Agenzia delle Entrate](http://www.agenziaentrate.gov.it/wps/content/nsilib/nsi/schede/comunicazioni/dati+fatture+%28c.d.+nuovo+spesometro%29/software+di+controllo+dati+fatture+%28c.d.+nuovo+spesometro%29) | 01-03-2018  | 31-12-2018 | Controllo tramite s/w Agenzia delle Entrate               |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+------------+-----------------------------------------------------------+
| [![xml_schema](https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/icons/fatturapa.png)](https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md)                        | [Agenzia delle Entrate](http://www.agenziaentrate.gov.it/wps/content/Nsilib/Nsi/Strumenti/Specifiche+tecniche/Specifiche+tecniche+comunicazioni/Fatture+e+corrispettivi+ST/)                                  | 05-10-2017  | 31-12-2018 | File accettati da portale fatturaPA Agenzia delle Entrate |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+------------+-----------------------------------------------------------+


|

Usage / Utilizo
---------------

* |menu| Contabilità > Configurazione > Sezionali > Sezionali :point_right: Impostare sezionali autofatture
* |menu| Contabilità > Configurazione > Imposte > Imposte :point_right: Impostare natura codici IVA
* |menu| Contabilità > Clienti > Clienti :point_right: Impostare nazione, partita IVA, codice fiscale e Cognome/nome
* |menu| Contabilità > Fornitori > Fornitori :point_right: Impostare nazione, partita IVA, codice fiscale e Cognome/nome
* |menu| Contabilità > Elaborazione periodica > Fine periodo > Comunicazione :point_right: Gestione Comunicazione e scarico file xml

|
|

Support / Supporto
------------------


|Zeroincombenze| This module is maintained by the `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__ and free support is supplied through `Odoo Italia Associazione Forum <https://odoo-italia.org/index.php/kunena/recente>`__


|
|

Credits / Titoli di coda
========================

Copyright
---------

Odoo is a trademark of `Odoo S.A. <https://www.odoo.com/>`__ (formerly OpenERP)


|

Authors / Autori
-----------------

* `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__
* `Didotech srl <http://www.didotech.com>`__

Contributors / Collaboratori
----------------------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
* Andrei Levin <andrei.levin@didotech.com>

|

----------------


|en| **zeroincombenze®** is a trademark of `SHS-AV s.r.l. <https://www.shs-av.com/>`__
which distributes and promotes ready-to-use **Odoo** on own cloud infrastructure.
`Zeroincombenze® distribution of Odoo <https://wiki.zeroincombenze.org/en/Odoo>`__
is mainly designed to cover Italian law and markeplace.

|it| **zeroincombenze®** è un marchio registrato di `SHS-AV s.r.l. <https://www.shs-av.com/>`__
che distribuisce e promuove **Odoo** pronto all'uso sullla propria infrastuttura.
La distribuzione `Zeroincombenze® è progettata per le esigenze del mercato italiano.

|

Last Update / Ultimo aggiornamento: 2018-12-01

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/l10n-italy.svg?branch=7.0
    :target: https://travis-ci.org/zeroincombenze/l10n-italy
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/l10n-italy/badge.svg?branch=7.0
    :target: https://coveralls.io/github/zeroincombenze/l10n-italy?branch=7.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/l10n-italy/branch/7.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/l10n-italy/branch/7.0
    :alt: Codecov
.. |OCA project| image:: Unknown badge-OCA
    :target: https://github.com/OCA/l10n-italy/tree/7.0
    :alt: OCA
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-7.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/7.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-7.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/7.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-7.svg
    :target: https://erp7.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov Status| image:: https://codecov.io/gh/OCA/l10n-italy/branch/7.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/l10n-italy/branch/7.0
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/groups/openerp.italia/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/groups/openerp.italia/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b
''',
    'maintainer': 'Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>',
}
