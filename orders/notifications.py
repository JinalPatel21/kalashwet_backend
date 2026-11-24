import logging
from decimal import Decimal
from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _rupees(value):
    return f"₹{int(Decimal(str(value or 0))):,}"


def _email_context(order, intro):
    items = []
    for raw in order.items or []:
        item = dict(raw)
        quantity = max(1, int(item.get('quantity') or 1))
        unit_price = Decimal(str(item.get('unit_price') or 0))
        item['name'] = str(item.get('name') or item.get('product_slug') or 'Jewellery item')
        item['quantity'] = quantity
        item['line_total_display'] = _rupees(unit_price * quantity)
        item['image'] = item.get('image') or ''
        description = [item.get('purity'), item.get('metal'), f"Size {item['size']}" if item.get('size') else None]
        item['variant_description'] = ' · '.join(str(part) for part in description if part) or 'Kalashwet design'
        items.append(item)

    address = order.shipping_address or {}
    address_lines = [
        address.get('full_name'), address.get('line1'), address.get('line2'),
        ', '.join(str(part) for part in (address.get('city'), address.get('state')) if part),
        address.get('pincode'), address.get('phone'),
    ]
    return {
        'order': order,
        'customer_name': (getattr(order.user, 'name', '') if order.user_id else '') or 'there',
        'status_label': order.get_status_display(),
        'payment_label': order.payment_method.replace('_', ' ').title(),
        'intro': intro,
        'items': items,
        'address_lines': [str(line) for line in address_lines if line],
        'subtotal_display': _rupees(order.subtotal),
        'discount_display': _rupees(order.discount),
        'shipping_display': _rupees(order.shipping),
        'total_display': _rupees(order.total),
    }


def send_order_email(order, event='status'):
    """Send a branded receipt or order update without interrupting checkout."""
    recipient = getattr(order.user, 'email', None) if order.user_id else None
    if not recipient:
        logger.info('Skipping order email for %s: customer has no email address.', order.number)
        return False

    status_label = order.get_status_display()
    if event == 'placed':
        subject = f"We've received order {order.number}"
        intro = 'Thank you for your order. Here is your itemized order summary.'
        if order.status == 'pending_payment':
            intro += ' Payment is pending. We will send another update when it is confirmed.'
        template = 'orders/emails/order_placed'
    else:
        subject = f'Order {order.number} update: {status_label}'
        intro = f'Your order status is now {status_label}.'
        template = 'orders/emails/order_status'

    try:
        context = _email_context(order, intro)
        message = EmailMultiAlternatives(
            subject=subject,
            body=render_to_string(f'{template}.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        message.attach_alternative(render_to_string(f'{template}.html', context), 'text/html')

        logo_path = finders.find('orders/emails/kalashwet-logo.png')
        if logo_path:
            with open(logo_path, 'rb') as logo_file:
                logo = MIMEImage(logo_file.read(), _subtype='png')
            logo.add_header('Content-ID', '<kalashwet-logo>')
            logo.add_header('Content-Disposition', 'inline', filename='kalashwet-logo.png')
            message.attach(logo)

        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception('Could not send customer email for order %s.', order.number)
        return False
