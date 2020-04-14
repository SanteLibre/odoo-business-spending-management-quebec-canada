# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_phone = fields.Char(string="Phone", track_visibility='onchange')
    partner_address = fields.Char(string="Address", track_visibility='onchange')
    partner_address_invoice = fields.Char(string="Invoice address",
                                          track_visibility='onchange')
    show_create_partner = fields.Boolean(compute="_compute_show_create_partner",
                                         readonly=True)

    @api.multi
    @api.depends('category_id', 'partner_id')
    def _compute_show_create_partner(self):
        data_category_join_team = self.env.ref(
            'helpdesk_join_team.helpdesk_ticket_category_join_team').id
        for val in self:
            val.show_create_partner = data_category_join_team == val.category_id.id \
                                      and not val.partner_id

    def create_res_partner(self):
        if not self.partner_name:
            raise UserError(_('The partner name need to be filled.'))

        if not self.partner_email:
            raise UserError(_('The partner email need to be filled.'))

        values = {
            "name": self.partner_name,
            "supplier": False,
            "customer": False,
            "street": self.partner_address,
            "email": self.partner_email,
            "phone": self.partner_phone,
        }

        partner_id = self.env['res.partner'].create(values)
        self.partner_id = partner_id.id
