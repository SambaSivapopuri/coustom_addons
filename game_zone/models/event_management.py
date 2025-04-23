from odoo import api, fields, models

class EventManagement(models.Model):
    _name = 'event.management'
    _inherit = 'mail.thread'
    _description = 'Event Management'

    name = fields.Char(string="Event Name", tracking=True)
    no_seats = fields.Integer(string="Numder of Seats", tracking=True)
