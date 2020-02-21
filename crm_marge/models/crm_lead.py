# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmMarge(models.Model):
    _inherit = "crm.lead"

    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', track_visibility='always',
                                      readonly=True)
    cost = fields.Monetary(string="Cost", currency_field='company_currency')
    marge = fields.Monetary(string="Marge", currency_field='company_currency')
    marge_percent = fields.Float(string="Marge %")

    # def is_minimal_2_field_set(self):
    #     """
    #
    #     :return: true if 2 field is set
    #     """
    #     lst_field_1 = [a for a in (self.cost, self.marge) if a]
    #     lst_field_2 = [a for a in (self.cost, self.marge_percent) if a]
    #
    #     return len(lst_field_1) > 1 or len(lst_field_2) > 1

    @api.multi
    @api.onchange('marge', 'cost')
    def onchange_marge(self):
        """
        Update marge_percent with marge
        Influence marge_percent and planned_revenue
        """
        for lead in self:
            lead.planned_revenue = lead.marge + lead.cost

            if lead.planned_revenue:
                lead.marge_percent = 100. * lead.marge / lead.planned_revenue
            else:
                lead.marge_percent = 0.

    @api.multi
    @api.onchange('marge_percent')
    def onchange_marge_percent(self):
        """
        Update marge with marge_percent
        Influence marge and planned_revenue
        """
        for lead in self:
            # lead.planned_revenue = lead.marge + lead.cost
            if lead.marge_percent >= 100.:
                lead.marge_percent = 99.999999

            lead.marge = (lead.cost / (1 - (lead.marge_percent / 100))) - lead.cost
            lead.planned_revenue = lead.marge + lead.cost

            # lead.marge = lead.planned_revenue * (lead.marge_percent / 100.)
            # lead.cost = lead.planned_revenue - lead.marge
            #
            # if lead.planned_revenue:
            #     lead.marge = 100. * lead.marge / lead.planned_revenue
            # else:
            #     lead.marge_percent = 0.

    # @api.multi
    # @api.onchange('cost')
    # def onchange_cost(self):
    #     """
    #     Update cost
    #     Influence planned_revenue
    #     """
    #     for lead in self:
    #         lead.planned_revenue = lead.marge + lead.cost
