from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    workcenter_id = fields.One2many(comodel_name='mrp.workcenter',
                                    inverse_name='helpdesk_id',
                                    string="Helpdesk ticket")

    def create_supplier(self):
        status = super(HelpdeskTicket, self).create_supplier()

        partner_id = self.partner_id

        self.workcenter_id.partner_id = partner_id.id
        self.workcenter_id.is_approved = True

        self.workcenter_id.last_partner_approval = self.env.user

        return status
