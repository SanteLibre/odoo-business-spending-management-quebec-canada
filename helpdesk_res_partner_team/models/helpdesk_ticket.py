import logging
import werkzeug

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    is_employee = fields.Boolean(string="is_employee", default=False)

    def create_res_partner(self):
        if not self.partner_name:
            raise UserError(_('The partner name need to be filled.'))

        if not self.partner_email:
            raise UserError(_('The partner email need to be filled.'))

        # TODO use reference
        if self.category_id.id != 3:
            raise UserError(_('The category need to be "Joindre team".'))

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

    def create_employee(self):
        if not self.partner_id:
            raise UserError(_('The partner need to be choose.'))

        if not self.partner_id.email:
            raise UserError(_('The partner need an email.'))

        # TODO validate the user is not created and not an employee

        # TODO use reference
        if self.category_id.id != 3:
            raise UserError(_('The category need to be "Joindre team".'))

        # Create res.user
        company_id = self.env['res.company']._company_default_get('res.users').id
        user_employee = self.sudo().with_context(company_id=company_id)._create_user(
            self.partner_id.email)
        user_employee.groups_id = [
            (6, 0, [self.env.ref('base.group_user').id])
        ]
        user_employee.user_ids.partner_id.signup_prepare()
        user_sudo = user_employee.user_ids

        template = self.env.ref(
            'auth_signup.mail_template_user_signup_account_created',
            raise_if_not_found=False)
        if user_sudo and template:
            template.sudo().with_context(
                lang=user_sudo.lang,
                auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
            ).send_mail(user_sudo.id, force_send=True)

        values = {
            "user_id": user_sudo.id,
            "work_email": self.partner_email,
            "work_phone": self.partner_phone,
            # "address_home_id": self.partner_address,
            # "image": self.partner_id.image,
            "name": self.partner_name,
        }

        self.env['hr.employee'].create(values)
        self.partner_id.customer = False
        self.is_employee = True

    @api.multi
    def _create_user(self, email):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        company_id = self.env.context.get('company_id')
        return self.env['res.users'].with_context(
            no_reset_password=True)._create_user_from_template({
            'email': email,
            'login': email,
            'partner_id': self.partner_id.id,
            'company_id': company_id,
            'company_ids': [(6, 0, [company_id])],
        })
