from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def send_join_team_mail(self):
        if self.partner_email:
            self.env.ref('helpdesk_join_team.join_team_email_template'). \
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
                'helpdesk_join_team.helpdesk_ticket_category_join_team').id:
            res.send_join_team_mail()

        return res
