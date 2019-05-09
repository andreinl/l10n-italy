# -*- coding: utf-8 -*-
#
# Copyright 2018-19 - SHS-AV s.r.l. <https://www.zeroincombenze.it>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError
import openerp.release as release

CAUSALE_CODE = '?'
CAUSALE_NAME = 'Please, do not use this record!'
CAUSALE_NAME2 = 'Please, delete this record!'


class TestCausali(TransactionCase):

    def env612(self, model):
        """Return model pool"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model)
        return self.env[model]

    def ref612(self, model):
        """Return reference id"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.ref(model)
        return self.env.ref(model).id

    def search612(self, model, *args):
        """Search record ids - Syntax search(model, *args)
        Warning! Do not use with Odoo 7.0: result may fails!"""
        return self.registry(model).search(self.cr, self.uid, *args)

    def browse612(self, model, id):
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).browse(self.cr, self.uid, id)
        return self.env[model].browse(id)

    def write612(self, model, id, values):
        """Write existent record [7.0]"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.registry(model).write(self.cr, self.uid, [id], values)
        return self.env[model].search([('id', '=', id)]).write(values)

    def write_ref(self, xid, values):
        """Browse and write existent record"""
        return self.browse_ref(xid).write(values)

    def create612(self, model, values):
        """Create a new record for test"""
        if int(release.major_version.split('.')[0]) < 8:
            return self.env612(model).create(self.cr,
                                             self.uid,
                                             values)
        return self.env612(model).create(values).id

    def setUp(self):
        super(TestCausali, self).setUp()
        # self.causale_model = self.env['causale.pagamento']
        # self.causale_b = self.env.ref('l10n_it_causali_pagamento.b')

    def test_causali(self):
        model_name = 'causale.pagamento'
        self.codice_carica_id = self.create612(
            model_name,
            {'code': CAUSALE_CODE,
             'name': CAUSALE_NAME})
        rec = self.browse612(model_name, self.codice_carica_id)
        self.assertEqual(rec.name, CAUSALE_NAME)
        self.write612(model_name, self.codice_carica_id,
                      {'name': CAUSALE_NAME2})
        rec = self.browse612(model_name, self.codice_carica_id)
        self.assertEqual(rec.name, CAUSALE_NAME2)

        name = self.env.ref('l10n_it_causali_pagamento.b').name_get()
        self.assertEqual(name, [(
            self.env.ref('l10n_it_causali_pagamento.b').id,
            u"B - Utilizzazione economica, da parte dell'autore ..."
        )])
