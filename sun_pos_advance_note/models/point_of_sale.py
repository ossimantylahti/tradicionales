from openerp import models, fields, api, _

class pos_order(models.Model):
    _inherit = "pos.order"

    def _order_fields(self,ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        res.update({
            'note': ui_order.get('order_note') or False
        })
        return res

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_order_note = fields.Boolean('POS Order Note')
    enable_product_note = fields.Boolean('POS Product Note')
    is_ordernote_receipt = fields.Boolean('POS Order Note on Receipt')
    is_productnote_receipt = fields.Boolean('POS Product Note on Receipt')

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    line_note = fields.Char('Product Note', size=512)
