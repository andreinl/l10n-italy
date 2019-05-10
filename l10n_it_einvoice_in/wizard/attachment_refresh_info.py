# -*- coding: utf-8 -*-

import base64
import io
import zipfile
from datetime import datetime
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class WizardAttachmentInRefresh(models.TransientModel):
    _name = "wizard.attachment.in.refresh"

    @api.multi
    def refresh_info(self):
        self.ensure_one()
        attachments = self.env[self.env.context['active_model']].browse(
            self.env.context['active_ids'])
        attachments._compute_xml_data()

        return True


class WizardAttachmentInDuedate(models.TransientModel):
    _name = "wizard.attachment.in.duedate"

    @api.multi
    def refresh_duedate(self):
        self.ensure_one()
        attachments = self.env[self.env.context['active_model']].browse(
            self.env.context['active_ids'])
        attachments.revaluate_due_date()

        return True
