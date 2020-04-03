from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def create_supplier(self):
        if not self.partner_name:
            raise UserError(_('The partner name need to be filled.'))

        if not self.partner_email:
            raise UserError(_('The partner email need to be filled.'))

        # TODO use reference
        if self.category_id.id != 4:
            raise UserError(_('The category need to be "Joindre fournisseur".'))

        values = {
            "name": self.partner_name,
            "supplier": True,
            "customer": False,
            "street": self.partner_address,
            "email": self.partner_email,
            "phone": self.partner_phone,
        }

        partner_id = self.env['res.partner'].create(values)
        self.partner_id = partner_id.id
