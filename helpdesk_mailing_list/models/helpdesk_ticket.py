import json

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.multi
    def add_mailing_list(self):
        if self.partner_name:
            name = self.partner_name
        elif self.partner_id and self.partner_id.name:
            name = self.partner_id.name
        else:
            raise UserError(
                _('The name partner of ticket or the partner need to be set.'))

        if self.partner_email:
            email = self.partner_email
        elif self.partner_id and self.partner_id.email:
            email = self.partner_id.email
        else:
            raise UserError(_('The email of ticket or the partner need to be set.'))

        action = self.env.ref(
            'helpdesk_mailing_list.mass_mailing_schedule_date_action').read()[0]
        action['context'] = dict(self.env.context, email=email, name=name)
        return action
