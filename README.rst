
===============================
|Zeroincombenze| l10n-italy 8.0
===============================

|Maturity| |Build Status| |Coverage Status| |Codecov Status| |license gpl| |Tech Doc| |Help| |Try Me|

.. contents::


Overview / Panoramica
=====================

|en| Italian Localization

|it| Localizzazione Italiana

La localizzazione italiana comprende moduli per la gestione delle principali
incombenze fiscali che le imprese italiane devono gestire.

Sono coperte le aree:

* Stampa registri IVA
* Stampa libro giornale
* Liquidazione IVA Elettronica
* Comunicazione IVA Elettronica (ex Spesometro)
* Registrazione fatture fornitori con RA
* Emissione parcelle attive
* FatturaPA
* Fattura Elettronica B2B
* Gestione DdT
* Data di registrazione fatture fornitori
* Gestione Ricevute Bancarie
* Split payment
* Documenti con Reverse Charge

Avaiable Addons / Moduli disponibili
------------------------------------

+--------------------------------------+------------+------------+----------------------------------------------------+
| Name / Nome                          | Version    | OCA Ver.   | Description / Descrizione                          |
+--------------------------------------+------------+------------+----------------------------------------------------+
| account_central_journal              | 8.0.0.1.0  | |no_check| | account_central_journal                            |
+--------------------------------------+------------+------------+----------------------------------------------------+
| account_fiscal_year_closing          | |halt|     | |halt|     | Fiscal Year Closing                                |
+--------------------------------------+------------+------------+----------------------------------------------------+
| account_invoice_entry_date           | 8.0.0.1.0  | |same|     | Account Invoice entry Date                         |
+--------------------------------------+------------+------------+----------------------------------------------------+
| account_invoice_sequential_dates     | 8.0.1.0.1  | 8.0.1.0.0  | Check invoice date consistency                     |
+--------------------------------------+------------+------------+----------------------------------------------------+
| account_vat_period_end_statement     | 8.0.3.0.5  | 8.0.3.0.0  | Period End VAT Statement                           |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_CEE_balance_generic          | 8.0.0.1    | |halt|     | Italy - 4th EU Directive - Consolidation Chart of  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_abicab                       | 8.0.1.0.0  | |same|     | Base Bank ABI/CAB codes                            |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_account                      | 8.0.1.0.0  | |same|     | Italian Localization - Account                     |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_account_stamp                | |no_check| | 8.0.1.0.0  | Tax stamp automatic management                     |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_account_tax_kind             | |no_check| | 8.0.1.0.0  | Italian Localisation - Natura delle aliquote IVA   |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ade                          | 8.0.0.1.10 | |no_check| | Codice con le definizioni dei file xml Agenzia del |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ateco                        | 8.0.1.0.0  | |same|     | Ateco codes                                        |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_base                         | 8.0.0.2.15 | 8.0.0.1.0  | Italian Localisation - Base                        |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_base_crm                     | |halt|     | |halt|     | Italian Localisation - CRM                         |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_base_location_geonames_impor | |halt|     | |same|     | Import base_location entries (provinces) from Geon |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_bill_of_entry                | |halt|     | |halt|     | Italian Localisation - Bill of Entry               |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_causali_pagamento            | 8.0.1.0.0  | |same|     | Aggiunge la tabella delle causali di pagamento da  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_central_journal              | 8.0.2.0.1  | 8.0.2.0.0  | Italy: Account central journal                     |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_codici_carica                | |no_check| | 8.0.1.0.0  | Aggiunge la tabella dei codici carica da usare nei |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_corrispettivi                | 8.0.1.0.0  | |same|     | Italian Localization - Corrispettivi               |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ddt                          | 8.0.1.0.0  | 8.0.1.0.1  | Documento di Trasporto                             |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ddt_delivery                 | 8.0.1.0.0  | |same|     | Copy carrier from picking and from sale order      |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_einvoice_base                | 8.0.2.1.1  | |no_check| | Infrastructure for Italian Electronic Invoice + Fa |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_einvoice_export_zip          | 8.0.1.0.0  | |no_check| | Esportazione di file XML di fatture elettroniche i |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_einvoice_in                  | |halt|     | |no_check| | Electronic invoices reception                      |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_einvoice_out                 | 8.0.3.2.2  | |no_check| | Electronic invoices emission                       |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_einvoice_stamp               | 8.0.1.0.1  | |no_check| | Tax stamp automatic management                     |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_esigibilita_iva              | |no_check| | 8.0.1.0.0  | Esigibilità IVA                                    |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa                    | |no_check| | 8.0.2.2.5  | Electronic invoices                                |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_export_zip         | |no_check| | 8.0.1.0.0  | Permette di esportare in uno ZIP diversi file XML  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_in                 | |no_check| | 8.0.1.1.6  | Electronic invoices reception                      |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_out                | |no_check| | 8.0.3.3.0  | Electronic invoices emission                       |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_out_ddt            | |no_check| | 8.0.1.0.0  | Modulo ponte tra emissione fatture elettroniche e  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_out_stamp          | |no_check| | 8.0.1.0.0  | Modulo ponte tra emissione fatture elettroniche e  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_out_wt             | |no_check| | 8.0.1.0.0  | Modulo ponte tra emissione fatture elettroniche e  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fatturapa_pec                | |no_check| | 8.0.1.3.0  | Send electronic invoices via PEC                   |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fiscal                       | 8.0.0.2    | |no_check| | Italy - Fiscal localization by zeroincombenze(R)   |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fiscal_document_type         | |no_check| | 8.0.1.1.0  | Italian Localization - Tipi di documento fiscale p |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fiscal_ipa                   | 8.0.1.1.0  | |no_check| | IPA Code and Destination Code in Partner Record    |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fiscal_payment_term          | 8.0.1.0.0  | 8.0.0.0.0  | Electronic invoices payment                        |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_fiscalcode                   | 8.0.0.2.0  | 8.0.0.1.1  | Italian Localisation - Fiscal Code                 |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ipa                          | |no_check| | 8.0.2.0.0  | IPA Code (IndicePA)                                |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_partially_deductible_vat     | |halt|     | |halt|     | Italy - Partially Deductible VAT                   |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_pec                          | 8.0.0.1.0  | |same|     | Pec Mail                                           |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_prima_nota_cassa             | |halt|     | |halt|     | Italian Localisation - Prima Nota Cassa            |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_rea                          | 8.0.1.0.1  | 8.0.0.1.0  | Manage fields for  Economic Administrative catalog |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_regions                      | |no_check| | 8.0.1.0.1  | Import Italian regions from Geonames               |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_reverse_charge               | 8.0.2.0.0  | |same|     | Reverse Charge for Italy                           |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_ricevute_bancarie            | 8.0.1.3.0  | 8.0.1.3.1  | Ricevute Bancarie                                  |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_sdi_channel                  | |no_check| | 8.0.1.1.0  | Aggiunge il canale di invio/ricezione dei file XML |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_sepa_bonifici                | |no_check| | 8.0.1.0.0  | Banking SEPA Italian Credit Transfer CBI           |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_split_payment                | 8.0.1.0.0  | |same|     | Split Payment                                      |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_vat_communication            | 8.0.0.1.12 | |no_check| | Comunicazione periodica IVA                        |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_vat_registries               | 8.0.2.0.0  | |same|     | Italian Localization - VAT Registries              |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_withholding_tax              | 8.0.3.0.0  | |same|     | Italian Withholding Tax                            |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_withholding_tax_causali      | |no_check| | 8.0.1.0.0  | Causali pagamento per ritenute d'acconto           |
+--------------------------------------+------------+------------+----------------------------------------------------+
| l10n_it_withholding_tax_payment      | 8.0.2.0.0  | |same|     | Italian Withholding Tax Payment                    |
+--------------------------------------+------------+------------+----------------------------------------------------+
| multibase_plus                       | 8.0.0.1.2  | |no_check| | Enhanced Odoo Features                             |
+--------------------------------------+------------+------------+----------------------------------------------------+


OCA comparation / Confronto con OCA
-----------------------------------

+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Description / Descrizione            | Odoo Italia      | OCA             | Notes / Note                                                                         |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Coverage                             | |Codecov Status| | |OCA Codecov|   |                                                                                      |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Gestione evoluta anagrafiche         | |check|          | |no_check|      | `l10n_it_base <https://github.com/zeroincombenze/l10n-italy/tree/8.0/l10n_it_base>__ |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Piano dei conti evoluto              | |check|          | |no_check|      |                                                                                      |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Codici IVA completi                  | |check|          | |no_check|      |                                                                                      |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| FatturaPA                            | v1.2.1           | v1.2.1          |                                                                                      |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+
| Validazione Codice Fiscale           | |check|          | |no_check|      |                                                                                      |
+--------------------------------------+------------------+-----------------+--------------------------------------------------------------------------------------+



Getting started / Come iniziare
===============================

|Try Me|


Prerequisites / Prerequisiti
----------------------------


* python2.7+
* postgresql 9.2+

Installation / Installazione
----------------------------

+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instruction are just an   | Istruzioni di esempio valide solo per    |
| example to remember what        | distribuzioni Linux CentOS 7, Ubuntu 14+ |
| you have to do on Linux.        | e Debian 8+                              |
|                                 |                                          |
| Installation is built with:     | L'installazione è costruita con:         |
+---------------------------------+------------------------------------------+
| `Zeroincombenze Tools <https://github.com/zeroincombenze/tools>`__         |
+---------------------------------+------------------------------------------+
| Suggested deployment is:        | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| /opt/odoo/8.0/l10n-italy/                                                  |
+----------------------------------------------------------------------------+

::

    cd $HOME
    git clone https://github.com/zeroincombenze/tools.git
    cd ./tools
    ./install_tools.sh -p
    export PATH=$HOME/dev:$PATH
    odoo_install_repository l10n-italy -b 8.0 -O zero
    for pkg in os0 z0lib; do
        pip install $pkg -U
    done
    sudo manage_odoo requirements -b 8.0 -vsy -o /opt/odoo/8.0


Upgrade / Aggiornamento
-----------------------

+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| When you want upgrade and you   | Per aggiornare, se avete installato con  |
| installed using above           | le istruzioni di cui sopra:              |
| statements:                     |                                          |
+---------------------------------+------------------------------------------+

::

    odoo_install_repository l10n-italy -b 8.0 -O zero -U
    # Adjust following statements as per your system
    sudo systemctl restart odoo


Support / Supporto
------------------


|Zeroincombenze| This module is maintained by the `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__



Get involved / Ci mettiamo in gioco
===================================

Bug reports are welcome! You can use the issue tracker to report bugs,
and/or submit pull requests on `GitHub Issues
<https://github.com/zeroincombenze/l10n-italy/issues>`_.

In case of trouble, please check there if your issue has already been reported.

Proposals for enhancement
-------------------------


|en| If you have a proposal to change this module, you may want to send an email to <cc@shs-av.com> for initial feedback.
An Enhancement Proposal may be submitted if your idea gains ground.

|it| Se hai proposte per migliorare questo modulo, puoi inviare una mail a <cc@shs-av.com> per un iniziale contatto.

Credits / Titoli di coda
========================

Copyright
---------

Odoo is a trademark of `Odoo S.A. <https://www.odoo.com/>`__ (formerly OpenERP)


----------------


|en| **zeroincombenze®** is a trademark of `SHS-AV s.r.l. <https://www.shs-av.com/>`__
which distributes and promotes ready-to-use **Odoo** on own cloud infrastructure.
`Zeroincombenze® distribution of Odoo <https://wiki.zeroincombenze.org/en/Odoo>`__
is mainly designed to cover Italian law and markeplace.

|it| **zeroincombenze®** è un marchio registrato di `SHS-AV s.r.l. <https://www.shs-av.com/>`__
che distribuisce e promuove **Odoo** pronto all'uso sullla propria infrastuttura.
La distribuzione `Zeroincombenze® è progettata per le esigenze del mercato italiano.


|chat_with_us|


|

Last Update / Ultimo aggiornamento: 2019-03-20

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alfa
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/l10n-italy.svg?branch=8.0
    :target: https://travis-ci.org/zeroincombenze/l10n-italy
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/9.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/l10n-italy/badge.svg?branch=8.0
    :target: https://coveralls.io/github/zeroincombenze/l10n-italy?branch=8.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/l10n-italy/branch/8.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/l10n-italy/branch/8.0
    :alt: Codecov
.. |OCA project| image:: Unknown badge-OCA
    :target: https://github.com/OCA/l10n-italy/tree/8.0
    :alt: OCA
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-8.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/8.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-8.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/8.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-8.svg
    :target: https://erp8.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov Status| image:: https://codecov.io/gh/OCA/l10n-italy/branch/8.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/l10n-italy/branch/8.0
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
