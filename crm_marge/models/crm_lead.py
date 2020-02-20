# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmMarge(models.Model):
    _inherit = "crm.lead"

    marge = fields.Monetary(string="Marge", currency_field='company_currency')
    marge_percent = fields.Float(string="Marge %")

    @api.multi
    @api.onchange('marge')
    def onchange_marge(self):
        """
        Update marge_percent
        """
        for lead in self:
            if lead.planned_revenue:
                lead.marge_percent = 100. * lead.marge / lead.planned_revenue
            else:
                lead.marge_percent = 0.

    @api.multi
    @api.onchange('marge_percent', 'planned_revenue')
    def onchange_marge_percent(self):
        """
        Update marge
        """
        for lead in self:
            lead.marge = lead.planned_revenue * (lead.marge_percent / 100.)
