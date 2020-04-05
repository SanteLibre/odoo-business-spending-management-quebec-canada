from odoo import fields, models, api


class MassMailingScheduleDate(models.TransientModel):
    _name = 'helpdesk.mass.mailing'
    _description = 'Helpdesk add email to Mass Mailing'

    @api.model
    def default_get(self, lst_fields):
        result = super(MassMailingScheduleDate, self).default_get(lst_fields)
        if 'email' in lst_fields:
            result['email'] = self._context.get('email', "")
        if 'name' in lst_fields:
            result['name'] = self._context.get('name', "")
        return result

    email = fields.Char(string="Email")
    name = fields.Char(string="Name")

    mass_mailing_list = fields.Many2one(
        comodel_name='mail.mass_mailing.list',
        string='Mailing list',
        domain=[('active', '=', True)]
    )

    @api.onchange('mass_mailing_list')
    def onchange_mass_mailing_list(self):
        # mass_mailing_list domain exclude actual mail
        lst_mml_id_all = set(
            [a.id for a in self.env["mail.mass_mailing.list"].search([])])
        lst_mml_id_diff = set(
            [a.id for a in self.env["mail.mass_mailing.list"].search([])
             for b in a.subscription_contact_ids if b.contact_id.email == self.email])
        lst_mml_id = list(lst_mml_id_all - lst_mml_id_diff)

        res = {'domain': {
            'mass_mailing_list': [('id', 'in', lst_mml_id)],
        }
        }
        return res

    def set_mailing_list(self):
        for contact in self.mass_mailing_list.subscription_contact_ids:
            # Already exist
            if contact.contact_id.email == self.email:
                # contact_id = contact
                return
        for contact in self.env['mail.mass_mailing.contact'].search([]):
            if contact.email == self.email:
                contact_id = contact
                break
        else:
            values = {
                "email": self.email,
                "name": self.name
            }
            contact_id = self.env['mail.mass_mailing.contact'].create(values)

        values = {
            "opt_out": False,
            "list_id": self.mass_mailing_list.id,
            "unsubscription_date": False,
            "contact_id": contact_id.id,
        }
        self.env['mail.mass_mailing.list_contact_rel'].create(values)
