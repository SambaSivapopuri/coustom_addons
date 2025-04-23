from odoo import http
from odoo.http import request

class EventWebsiteController(http.Controller):

    @http.route('/event_webform', type='http', auth='public', website=True)
    def event_webformevents(self, **kw):
        print("Execution Here............")
        return request.render('sports_zone.create_event_template')

    @http.route('/create_webevent', type='http', auth='public', website=True)
    def event_webform(self, **kw):
        if request.httprequest.method == 'POST':
            try:
                # Create the event with submitted form data
                request.env['event.management'].sudo().create({
                    'name': kw.get('name'),
                    'no_seats': int(kw.get('no_seats', 0)),
                    'price': kw.get('price'),
                    'discount': float(kw.get('discount', 0)),
                    'category': kw.get('category'),
                })
                return request.render('sports_zone.create_event_template', {'success': True})
            except Exception as e:
                return request.render('sports_zone.create_event_template', {
                    'error': str(e),
                    'success': False
                })

        # GET request - show form
        request.render('sports_zone.create_event_template')
