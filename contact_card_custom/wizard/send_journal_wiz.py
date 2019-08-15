# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class SendJournalWiz(models.TransientModel):
    _name = 'send.journal.wiz'

    @api.model
    def get_start_date(self):
        first_day = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT) + relativedelta(day=1)
        return first_day

    @api.model
    def get_last_date(self):
        last_day = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT) + relativedelta(day=1, months=+1, days=-1)
        return last_day

    start_date = fields.Date(string="Start Date", default=get_start_date)
    end_date = fields.Date(string="End Date", default=get_last_date)

    @api.multi
    def send_email(self):
        context = dict(self.env.context)
        for partner in self.env['res.partner'].browse(context.get('active_ids')):
            move_line_ids = self.env['account.move.line'].search([('partner_id', '=', partner.id), ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
            template_id = self.env.ref('contact_card_custom.email_template_partner_journal')
            if template_id and partner.email and move_line_ids:
                template_id.with_context({'move_line_ids': move_line_ids}).send_mail(partner.id, force_send=True, raise_exception=False)