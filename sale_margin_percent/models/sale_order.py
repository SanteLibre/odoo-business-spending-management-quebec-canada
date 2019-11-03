from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_percent = fields.Float(compute='_product_margin_percent', digits=dp.get_precision('Product Price'),
                                  store=False)

    @api.depends('margin')
    def _product_margin_percent(self):
        for line in self:
            line.margin_percent = (line.margin / line.price_subtotal) * 100.
