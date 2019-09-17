# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp


class TipFeesManagement(models.Model):
    _inherit = 'hr.expense'

    unit_amount_compute = fields.Float("Unit Price Compute", compute='_compute_unit_amount_compute',
                                       digits=dp.get_precision('Product Price'), store=False)

    tip = fields.Float("Tip", readonly=True, required=False,
                       states={'draft': [('readonly', False)], 'reported': [('readonly', False)],
                               'refused': [('readonly', False)]}, digits=dp.get_precision('Product Price'))

    total_amount_with_tip = fields.Float("Total with tip", readonly=True, compute='_compute_amount',
                                         digits=dp.get_precision('Product Price'))

    total_amount_with_tip_entry = fields.Float("Total with tip entry", readonly=True, required=False,
                                               states={'draft': [('readonly', False)],
                                                       'reported': [('readonly', False)],
                                                       'refused': [('readonly', False)]},
                                               digits=dp.get_precision('Product Price'), description="This field ")

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id', 'tip', 'total_amount_with_tip_entry')
    def _compute_unit_amount_compute(self):
        for expense in self:
            # Don't compute if missing total_amount_with_tip_entry
            if not expense.total_amount_with_tip_entry:
                continue

            if not expense.unit_amount and expense.tip:
                # Sequence (tax,total_amount_with_tip_entry,tip)
                # Support unit amount without taxes! Recompute when taxes is chosen
                expense.unit_amount_compute = expense.tip
                subtotal = expense.total_amount_with_tip_entry - expense.tip

                # Find the magic number of taxes
                magic_number = 1000000
                taxes = expense.tax_ids.compute_all(magic_number, None, 1.0, expense.product_id,
                                                    expense.employee_id.user_id.partner_id)
                calculated_magic_taxes = taxes.get("total_included", 1.) / magic_number

                expense.unit_amount = subtotal / calculated_magic_taxes
            elif not expense.unit_amount and not expense.tip:
                # Sequence (total_amount_with_tip_entry,tax or no tax)
                # Nothing to compute with only one number
                continue
            elif not expense.tip and expense.unit_amount:
                # Sequence (total_amount_with_tip_entry,(tax,unit_amount|unit_amount,tax))
                expense.tip = expense.total_amount_with_tip_entry - expense.total_amount

    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id', 'tip', 'total_amount_with_tip_entry')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity,
                                                expense.product_id, expense.employee_id.user_id.partner_id)
            expense.total_amount = taxes.get('total_included')
            expense.total_amount_with_tip = expense.total_amount + expense.tip
