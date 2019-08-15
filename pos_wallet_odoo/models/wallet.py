# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime

class res_partner(models.Model):
    _inherit = 'res.partner'

    wallet_balance = fields.Float('Wallet Balance')

    wallet_transaction_count = fields.Integer(compute='_compute_wallet_transaction_count', string="Wallet")

    @api.multi
    def _compute_wallet_transaction_count(self):
        wallet_data = self.env['pos.wallet.transaction'].search([('partner_id', 'in', self.ids)])
        for partner in self:
            partner.wallet_transaction_count = len(wallet_data)
            

class account_journal(models.Model):
    _inherit = 'account.journal'

    wallet = fields.Boolean(string='Wallet Journal')
    
            
class pos_wallet_transaction(models.Model):
    _name='pos.wallet.transaction'
    _order = 'id desc'


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('pos.wallet.transaction') or 'New'
        res = super(pos_wallet_transaction, self).create(vals)
        return res


    @api.one
    def wallet_recharge(self, partner_id, wallet, journal):

        wallet_transaction_obj = self.env['pos.wallet.transaction']
        
        partner = self.env['res.partner'].browse(partner_id['id'])
        vals = {
            'wallet_type': 'credit',
            'partner_id': partner.id,
            #'pos_order_id' : order_id,
            'reference' : 'manual',
            'amount' : wallet,
            'currency_id' : partner.property_product_pricelist.currency_id.id,
            'status': 'done'
        }
        wallet_create = wallet_transaction_obj.sudo().create(vals)

        account_payment_obj = self.env['account.payment']
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')

        if journal == 'cash':
    	    cash_journal_ids = self.env['account.journal'].search([('type','=','cash')])
    	    if cash_journal_ids:
    	        journal = cash_journal_ids[0].id

        if journal == 'check':
    	    bank_journal_ids = self.env['account.journal'].search([('type','=','bank')])
    	    if bank_journal_ids:
    	        journal = bank_journal_ids[0].id
    	
        if journal == 'bank':
    	    bank_journal_ids = self.env['account.journal'].search([('type','=','bank')])
    	    if bank_journal_ids:
    	        journal = bank_journal_ids[0].id
    	                
        values = {
            'name' : self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code('account.payment.customer.invoice'),
            'payment_type' : "inbound",
            'amount' : wallet,
            'communication' : "Wallet Recharge",
            'payment_date' : datetime.now().date(),
            'journal_id' : journal,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': partner.id,
        }
        payment_create = account_payment_obj.sudo().create(values)
        payment_create.post() # Confirm Account Payment
                
        total_amount = partner.wallet_balance + float(wallet) # Total Amount
        
        partner.write({'wallet_balance': total_amount })	
                    
        return True
        
        
    name = fields.Char('Name')
    wallet_type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')
        ], string='Type', default='credit')
    partner_id = fields.Many2one('res.partner', 'Customer')
    pos_order_id = fields.Many2one('pos.order', 'POS Order')
    #sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    #wallet_id = fields.Many2one('res.partner', 'Wallet')
    reference = fields.Selection([
        ('manual', 'Manual'),
        ('pos_order', 'POS Order')
        ], string='Reference', default='manual')
    amount = fields.Char('Amount')
    currency_id = fields.Many2one('res.currency', 'Currency')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
        ], string='Status', readonly=True, default='draft')

            
    

class pos_order(models.Model):
    _inherit = 'pos.order'
    
    wallet_used = fields.Float('Wallet Amount Used')
    wallet_transaction_id = fields.Many2one('pos.wallet.transaction', 'Wallet Transaction')

    @api.model
    def create_from_ui(self, orders):
        
        wallet_transaction_obj = self.env['pos.wallet.transaction']
        
        order_ids = super(pos_order, self).create_from_ui(orders)
        
        for order_id in order_ids:
            pos_order_id = self.browse(order_id)
            #print "**************************pos_order_id",pos_order_id
            for pos_wallet in pos_order_id.statement_ids:
                if pos_wallet.journal_id.wallet == True:
                    vals = {
                        'wallet_type': 'debit',
                        'partner_id': pos_order_id.partner_id.id,
                        'pos_order_id' : order_id,
                        'reference' : 'pos_order',
                        'amount' : pos_wallet.amount,
                        'currency_id' : pos_order_id.pricelist_id.currency_id.id,
                        'status': 'done'
                    }
                    wallet_create = wallet_transaction_obj.sudo().create(vals)
                    
                    pos_order_id.write({'wallet_used':pos_wallet.amount, 'wallet_transaction_id':wallet_create.id })		
                
        return order_ids
                
class WalletRecharge(models.TransientModel):
    _name = 'wallet.recharge'
    
    recharge_amount = fields.Float('Recharge Amount',required="True")
    journal_id = fields.Many2one('account.journal', 'Payment Journal',required="True")
    
    @api.multi
    def post(self):
        context = self._context
        active_ids = context.get('active_ids')
        account_payment_obj = self.env['account.payment']
        partner_wallet_id = self.env['res.partner'].browse(active_ids[0])
        wallet_transaction_obj = self.env['pos.wallet.transaction']
        
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')
        
        vals = {}
        
        vals = {
            'name' : self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code('account.payment.customer.invoice'),
            'payment_type' : "inbound",
            'amount' : self.recharge_amount,
            'communication' : "Wallet Recharge",
            'payment_date' : datetime.now().date(),
            'journal_id' : self.journal_id.id,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': partner_wallet_id.id,
        }
        payment_create = account_payment_obj.sudo().create(vals)
        payment_create.post() # Confirm Account Payment
        value = {
            'wallet_type' : 'credit',
            'reference' : 'manual',
	        'amount' : self.recharge_amount,
	        'partner_id': partner_wallet_id.id,
	        'currency_id' : partner_wallet_id.property_product_pricelist.currency_id.id,
	        'payment_refer' : payment_create.id,
            'status': 'done',
        }
        wallet_obj = wallet_transaction_obj.sudo().create(value)
        
        total_amount = partner_wallet_id.wallet_balance + self.recharge_amount
        
        partner_wallet_id.write({'wallet_balance': total_amount })
        
        return
               
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
