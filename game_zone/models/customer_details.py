from odoo import api, fields, models

from odoo import models, fields

class CustomerDetails(models.Model):
    _name = 'customer.details'
    _description = 'Customer Details'  # ✅ Add this line
    _inherit = 'mail.thread'
    _rec_name = 'mobile_no'

    mobile_no = fields.Char(string='Mobile Number', required=True, tracking=True)
    name = fields.Char(string='Full Name', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', required=True, tracking=True)
    address = fields.Text(string='Address', tracking=True)

    _sql_constraints = [
        ('unique_mobile_no', 'unique(mobile_no)', 'Mobile number must be unique!'),
    ]


@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals['reference'] == 'New':
            vals ['reference'] = self.env['ir.sequence'].next_by_code('customer.details')

    return super().create(vals_list)

@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)

