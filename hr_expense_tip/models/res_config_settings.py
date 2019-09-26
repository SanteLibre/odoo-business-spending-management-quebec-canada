# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    refund_total_amount_tip_included_to_employee = fields.Boolean(
        string='Add tip when refund employee the expense.',
        config_parameter='hr_expense.refund_total_amount_tip_included_to_employee')
