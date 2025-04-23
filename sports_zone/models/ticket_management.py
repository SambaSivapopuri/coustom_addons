from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import qrcode
import logging

_logger = logging.getLogger(__name__)


class TicketManagement(models.Model):
    _name = 'ticket.management'
    _inherit = ['mail.thread']
    _description = 'Ticket Management'

    ticket_number = fields.Char(string='Ticket Number', readonly=True, copy=False, default='New')
    customer_id = fields.Many2one('customer.management', string='Customer', required=True, tracking=True)
    mobile_no = fields.Char(related='customer_id.mobile_no', string="Mobile Number", store=False, readonly=True)
    category = fields.Selection([
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('combo', 'Combo')
    ], string="Category", required=True)
    event_id = fields.Many2one(
        'event.management', string='Event', required=True, domain="[('category', '=', category)]")
    booking_date = fields.Date(string='Booking Date', default=fields.Date.today)
    no_tickets = fields.Integer(string='Number of Tickets',)
    price = fields.Float(string='Price per Ticket', required=True, default=0.0, readonly=True)
    discount = fields.Float(string='Discount (%)', default=0.0, readonly=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total', store=True)
    qr_code = fields.Binary("QR Code")
    notes = fields.Text(string="Internal Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.onchange('category')
    def _onchange_category(self):
        self.event_id = False

    @api.onchange('event_id')
    def _onchange_event_id(self):
      if not self.category:
        # No warning is returned anymore, just simply return nothing
        return



    @api.model
    def create(self, vals):
        if isinstance(vals.get('state'), bool):
            vals['state'] = 'draft' if vals.get('state') else 'cancelled'

        if not vals.get('customer_id') and vals.get('mobile_no'):
            customer = self.env['customer.management'].search([('mobile_no', '=', vals.get('mobile_no'))], limit=1)
            if customer:
                vals['customer_id'] = customer.id

        if vals.get('event_id'):
            event = self.env['event.management'].browse(vals['event_id'])
            vals.setdefault('price', event.price)
            vals.setdefault('discount', event.discount)
            seq = self.env['ir.sequence'].next_by_code('ticket.management')
            event_name_clean = event.name.replace(' ', '').replace('/', '')
            seq_clean = seq.split('/')[1] if '/' in seq else seq
            vals['ticket_number'] = f"{event_name_clean}-{seq_clean}"
        else:
            vals['ticket_number'] = self.env['ir.sequence'].next_by_code('ticket.management')

        record = super().create(vals)
        record.generate_qr_code()
        return record
    def action_confirm(self):
        for rec in self:
            rec.state = 'booked'
    def write(self, vals):
        res = super().write(vals)
        if 'qr_code' not in vals:
            self.generate_qr_code()
        return res

    def generate_qr_code(self):
        for rec in self:
            qr_binary = rec._generate_qr_binary()
            rec.qr_code = base64.b64encode(qr_binary)

    def _generate_qr_binary(self):
        qr_data = (
            f"Ticket Number: {self.ticket_number}\n"
            f"Customer: {self.customer_id.name or ''}\n"
            f"Mobile: {self.mobile_no or ''}\n"
            f"Event: {self.event_id.name or ''}\n"
            f"Category: {self.category or ''}\n"
            f"Booking Date: {self.booking_date.strftime('%Y-%m-%d') if self.booking_date else ''}\n"
            f"No. of Tickets: {self.no_tickets or 0}\n"
            f"Price per Ticket: ₹{self.price:.2f}\n"
            f"Discount: {self.discount:.2f}%\n"
            f"Total Amount: ₹{self.total_amount:.2f}"
        )
        img = qrcode.make(qr_data).convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def _get_ticket_data(self):
        return {
            'Ticket No.': self.ticket_number or '',
            'Customer': self.customer_id.name if self.customer_id else '',
            'Mobile': self.mobile_no or '',
            'Event': self.event_id.name if self.event_id else '',
            'Category': self.category or '',
            'Booking Date': self.booking_date.strftime('%Y-%m-%d') if self.booking_date else '',
            'Tickets': str(self.no_tickets or 0),
            'Price per Ticket': f"₹{self.price:.2f}",
            'Discount': f"{self.discount:.2f}%",
            'Total Amount': f"₹{self.total_amount:.2f}",
            'QR': self.qr_code or ''
        }

    def action_generate_jpeg(self):
        for record in self:
            ticket_data = record._get_ticket_data()
            jpeg_data = record._convert_to_jpeg(ticket_data)

            attachment = self.env['ir.attachment'].create({
                'name': f"{record.ticket_number}_ticket.jpeg",
                'type': 'binary',
                'datas': jpeg_data,
                'res_model': self._name,
                'res_id': record.id,
                'mimetype': 'image/jpeg',
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }

    def _convert_to_jpeg(self, ticket_data):
        img = Image.new('RGB', (750, 400), color='white')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        # Draw headers and rows
        x_start, y_start = 10, 10
        row_height = 25
        for i, (key, value) in enumerate(ticket_data.items()):
            if key == 'QR':
                continue
            draw.text((x_start, y_start + i * row_height), f"{key:<20}: {value}", fill='black', font=font)

        # Paste QR
        if ticket_data['QR']:
            qr_img = Image.open(BytesIO(base64.b64decode(ticket_data['QR']))).resize((130, 130))
            img.paste(qr_img, (600, 10))

        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def action_print_ticket_pdf(self):
        self.ensure_one()
        return self.env.ref('sports_zone.ticket_report').report_action(self)

    @api.depends('event_id', 'no_tickets')
    def _compute_total(self):
     for record in self:
        if not record.event_id:
            record.total_amount = 0.0
            continue

        event = record.event_id
        price = float(event.price or 0.0)
        discount = float(event.discount or 0.0)
        no_tickets = int(record.no_tickets or 0)

        subtotal = price * no_tickets
        discount_amt = (discount / 100.0) * subtotal
        record.total_amount = subtotal - discount_amt

        # Optionally update record fields to reflect current event pricing
        record.price = price
        record.discount = discount

