#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Busiada_Boarding'))

django.setup()

from django.template.loader import render_to_string

payment_methods = [
    {
        'title': 'M-Pesa',
        'label': 'MOBILE',
        'value': '522533',
        'description': 'Send via M-Pesa Paybill',
        'tooltip': 'Pay via M-Pesa',
        'icon': 'fa-solid fa-mobile-screen',
        'accent': '#00a82e',
        'accent_bg': 'rgba(0, 168, 46, 0.14)',
        'accent_border': 'rgba(0, 168, 46, 0.25)'
    },
    {
        'title': 'Card',
        'label': 'VISA/MASTER',
        'value': 'Online',
        'description': 'Pay by card via secure gateway.',
        'tooltip': 'Pay online',
        'icon': 'fa-solid fa-credit-card',
        'accent': '#ff8800',
        'accent_bg': 'rgba(255, 136, 0, 0.14)',
        'accent_border': 'rgba(255, 136, 0, 0.25)'
    },
    {
        'title': 'PayPal',
        'label': 'PAYPAL',
        'value': 'PayPal',
        'description': 'Pay via PayPal',
        'tooltip': 'Pay with PayPal',
        'icon': 'fa-brands fa-paypal',
        'accent': '#0070ba',
        'accent_bg': 'rgba(0, 112, 186, 0.14)',
        'accent_border': 'rgba(0, 112, 186, 0.25)'
    },
    {
        'title': 'Bank Transfer',
        'label': 'DIRECT',
        'value': 'Account details on request',
        'description': 'Direct bank transfer',
        'tooltip': 'Bank transfer',
        'icon': 'fa-solid fa-building-columns',
        'accent': '#4A90C8',
        'accent_bg': 'rgba(74, 144, 200, 0.14)',
        'accent_border': 'rgba(74, 144, 200, 0.25)'
    }
]

ctx = {
    'page': {
        'title': 'Fee Payment',
        'category': 'Admissions'
    },
    'payment_methods': payment_methods
}

html = render_to_string('boarding/fee_payment.html', ctx)
with open('fee_payment_updated.html', 'w') as f:
    f.write(html)

print('Fee payment page rendered successfully to fee_payment_updated.html')
