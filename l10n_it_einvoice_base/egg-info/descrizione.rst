Fattura Elettronica + FatturaPA
-------------------------------

Questo modulo gestisce l'infrastruttura per generare il file xml della Fattura 
Elettronica e della FatturaPA, versione 1.2.1, da trasmettere al sistema di interscambio SdI.

In anagrafica clienti i dati per la fattura elettronica sono inseribili nella scheda "Agenzia delle Entrate".
Le casistiche previste sono:

::

    Fattura elettronica a soggetto IVA

Si tratta della casistica più comune. Selezionare "Soggetto a fattura elettronica"
e compilare il "Codice destinatario" o la "PEC".
La partita IVA è un dato obligatorio ai fini dell'invio.
L'eventuale invio di una fattura in formato PDF è una fattura di cortesia e non
ha valore legale.

::

    Fattura elettronica a PA

Questa casistica è attiva già dal 2016. Impostare "Pubblica Amministrazione"
e compilare il "Codice ufficio".

::

    Fattura elettronica a privato senza partita IVA

La legge non prevede l'obbligo di emissione della fattura elettronica ma è
ammessa l'emissione a condizione che venga inviata una fattura in formato PDF
al cliente. Inserire il valore "0000000" nel codice destinatario
e il codice fiscale.

::

    Fattura elettronica a soggetto IVA senza Codice Destinatario ne PEC

Casistica in cui un cliente con partita IVA non ha fornito
ne il proprio Codice Destinatario ne la propria PEC. Si riconduce al caso
precedente, inserendo il valore "0000000" nel codice destinatario ed il
codice fiscale. Anche in questo caso è obbligatorio inviare una fattura in
formato PDF al cliente.

::

    Fattura elettronica a rappresentante fiscale in Italia

Casistica di aziende estere con rappresentanza fiscale in Italia.
Inserire nei contatti un indirizzo di fatturazione di tipo "Rappresentante fiscale"
con la partita IVA italiana ed i dati per la fatturazione elettronica.
La fattura va emessa al rappresentante fiscale.

::

    Fattura elettronica a stabile organizzazione

Casistica di aziende estere con stabile organizzazione in Italia.
Inserire nei contatti un indirizzo di fatturazione di tipo "Stabile organizzazione"
con la partita IVA italiana ed i dati per la fatturazione elettronica.
La fattura va emessa alla stabile organizzazione.

::

    Fattura elettronica a soggetto estero

Inserire il valore XXXXXXX nel codice destinatario. Il file XML viene generato
con le opportune correzione per la validazioni dell'Agenzia delle Entrate.
Anche in questo caso è obbligatorio inviare una fattura in
formato PDF al cliente.

::

Configurare le imposte riguardo a "Natura non imponibile",
"Riferimento legislativo" ed "Esigibilità IVA"

Configurare i dati della fattura elettronica nella configurazione della contabilità, dove necessario

::

    Destinatari:

Il modulo è destinato a tutte le aziende che dal 2019 dovranno emettere fattura elettronica


::

    Normativa:

Le leggi inerenti la fattura elettronica sono numerose. Potete consultare la `normativa fattura elettronica <https://www.fatturapa.gov.it/export/fatturazione/it/normativa/norme.htm>`__
