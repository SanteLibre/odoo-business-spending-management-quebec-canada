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

    def send_supplier_applicant_mail(self):
        if self.partner_email:
            self.env.ref('helpdesk_supplier.assignment_supplier_applicant_email_template'). \
                send_mail(self.id, email_values={}, force_send=True)

    def create(self, vals):
        # if vals.get('number', '/') == '/':
        #     seq = self.env['ir.sequence']
        #     if 'company_id' in vals:
        #         seq = seq.with_context(force_company=vals['company_id'])
        #     vals['number'] = seq.next_by_code(
        #         'helpdesk.ticket.sequence') or '/'
        res = super().create(vals)

        if res and vals.get('category_id') == self.env.ref(
                'helpdesk_supplier.helpdesk_ticket_category_supplier_applicant').id:
            res.send_supplier_applicant_mail()

        return res
