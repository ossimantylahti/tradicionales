# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PartnerEmailWiz(models.TransientModel):
    _name = 'partner.email.wiz'

    @api.multi
    def send_email(self):
        context = dict(self.env.context)
        for partner in self.env['res.partner'].browse(context.get('active_ids')):
            template_id = self.env.ref('contact_card_custom.email_template_partner_barcode')
            if template_id and partner.email:
                template_id.send_mail(partner.id, force_send=True, raise_exception=False)