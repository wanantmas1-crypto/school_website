import os
import sys
# Ensure the Django project package (inner folder) is on sys.path so `config.settings` is importable
project_dir = os.path.join(os.path.dirname(__file__), 'Busiada_Boarding')
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.template.loader import get_template


t = get_template('boarding/fee_payment.html')
# sample payment methods with distinct colors
payment_methods = [
    {'icon':'fa-solid fa-mobile-screen-button','title':'Mobile Money','label':'M-Pesa','value':'Paybill: 123456','description':'Use your mobile wallet to pay quickly.','tooltip':'Copy details','accent':'#0ea5e9','accent_bg':'rgba(14,165,233,0.12)','accent_border':'rgba(14,165,233,0.22)'},
    {'icon':'fa-solid fa-university','title':'Bank Transfer','label':'Bank','value':'A/C: 00112233','description':'Use bank transfer with the reference.','tooltip':'Bank details','accent':'#16a34a','accent_bg':'rgba(16,163,127,0.08)','accent_border':'rgba(16,163,127,0.18)'},
    {'icon':'fa-solid fa-credit-card','title':'Card','label':'Visa/Master','value':'Online','description':'Pay by card via secure gateway.','tooltip':'Pay online','accent':'#f97316','accent_bg':'rgba(249,115,22,0.08)','accent_border':'rgba(249,115,22,0.18)'},
    {'icon':'fa-brands fa-paypal','title':'PayPal','label':'PayPal','value':'PayPal','description':'Pay via PayPal','tooltip':'Pay with PayPal','accent':'#6366f1','accent_bg':'rgba(99,102,241,0.08)','accent_border':'rgba(99,102,241,0.18)'},
]
ctx = {'page': {'title': 'Fee Payment', 'category': 'Admissions'}, 'payment_methods': payment_methods}
html = t.render(ctx)
out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tmp_fee_payment_render.html'))
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('WROTE', out_path)
