from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class CustomerManagement(models.Model):
    _name = 'customer.management'
    _inherit = 'mail.thread'
    _description = 'Customer Details'

    name = fields.Char(string='Name', required=True, tracking=True)
    mobile_no = fields.Char(string='Mobile Number', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', tracking=True)
    city = fields.Text(string='City', tracking=True)

    _sql_constraints = [
        ('unique_mobile_no', 'unique(mobile_no)', '🚫 Mobile number already exists! Please use a unique number.'),
    ]

    @api.onchange('mobile_no')
    def _onchange_mobile_no(self):
        if self.mobile_no and not re.match(r'^[6-9]\d{9}$', self.mobile_no):
            return {
                'warning': {
                    'title': "📱 Invalid Mobile Number",
                    'message': "Mobile number must be 10 digits and start with 6, 7, 8, or 9."
                }
            }

    @api.onchange('email')
    def _onchange_email(self):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if self.email and not re.match(email_regex, self.email):
            return {
                'warning': {
                    'title': "📧 Invalid Email",
                    'message': "Please enter a valid email address, like example@exp.com."
                }
            }

    def find_all(self, keyword):
        """Search for customers by name, mobile number, or email."""
        domain = ['|', '|',
            ('name', 'ilike', keyword),
            ('mobile_no', 'ilike', keyword),
            ('email', 'ilike', keyword)
        ]
        results = self.search(domain)
        if not results:
            raise ValidationError(f"🔍 No customers found matching '{keyword}'. Try a different name, number, or email.")
        return results
