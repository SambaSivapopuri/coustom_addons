from odoo import api, models, fields

class Eventmanagement(models.Model):
    _name = 'event.management'
    _inherit = 'mail.thread'
    _description = 'Event Happening'

    name = fields.Char(string='Name', required=True, tracking=True)
    no_seats = fields.Integer(string='Number of Seats', required=True, tracking=True)
    price = fields.Char(string='Price', required=True, tracking=True)
    discount = fields.Float(string='Discount', default=0.0, tracking=True)
    category = fields.Selection(
        selection=[
            ('child', 'Child'),
            ('adult', 'Adult'),
            ('combo', 'Combo'),
        ],
        string='Category',
        required=True,
        default='adult',
        tracking=True
    )



    def find_all(self, keyword):
        return self.search(['|', ('name', 'ilike', keyword), ('no_seat', '=', int(keyword), ('price', 'ilike', keyword)) if keyword.isdigit() else ('id', '=', 0)])
