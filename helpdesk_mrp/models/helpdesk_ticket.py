from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    workcenter_id = fields.One2many(comodel_name='mrp.workcenter',
                                    inverse_name='helpdesk_id',
                                    string="Machines")
    show_create_supplier_mrp = fields.Boolean(
        compute="_compute_show_create_supplier_mrp",
        readonly=True)

    @api.multi
    @api.depends('category_id')
    def _compute_show_create_supplier_mrp(self):
        data_category = self.env.ref(
            'helpdesk_supplier.helpdesk_ticket_category_supplier_applicant').id
        for val in self:
            val.show_create_supplier_mrp = data_category == val.category_id.id and \
                                           not val.partner_id or \
                                           not val.partner_id.supplier

    def create_supplier(self):
        status = super(HelpdeskTicket, self).create_supplier()

        partner_id = self.partner_id

        self.workcenter_id.partner_id = partner_id.id
        self.workcenter_id.is_approved = True

        self.workcenter_id.last_partner_approval = self.env.user

        return status
