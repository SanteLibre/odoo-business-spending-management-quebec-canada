# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp


class TipFeesManagement(models.Model):
    _inherit = 'hr.expense'

    tip = fields.Float("Tip", readonly=True, required=False,
                       states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                               'refused': [('readonly', False)]}, digits=dp.get_precision('Product Price'))

    total_amount_with_tip = fields.Float("Total with tip", readonly=True, compute='_compute_amount',
                                         digits=dp.get_precision('Product Price'))

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id', 'tip')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity,
                                                expense.product_id, expense.employee_id.user_id.partner_id)
            expense.total_amount = taxes.get('total_included')
            expense.total_amount_with_tip = expense.total_amount + expense.tip
