from odoo import api, fields, models

class CustomerDetails(models.Model):
   from odoo import models, fields, api

class TicketManagement(models.Model):
    _name = 'ticket.management'
    _description = 'Ticket Management'

    name = fields.Char(string='Ticket No', required=True)
    customer_id = fields.Many2one('customer.details', string='Customer', required=True,domain=[('is_customer', '=', True)])
    event_id = fields.Many2one('event.management', string='Event', required=True)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today)
    seat_number = fields.Char(string='Seat Number')
    state = fields.Selection([('draft', 'Draft'),('booked', 'Booked'), ('cancelled', 'Cancelled')], string='Status', default='draft')

     # Optional: Auto name or validations
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('ticket.management') or 'New'
        return super(TicketManagement, self).create(vals)