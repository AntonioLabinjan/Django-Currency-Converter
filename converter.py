import os, sys, django, requests
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.core.management import execute_from_command_line
from django import forms

settings.configure(
    DEBUG=True,
    SECRET_KEY='devkey',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE=[],
    INSTALLED_APPS=['django.forms'],
    TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates','DIRS':[]}],
    FORM_RENDERER='django.forms.renderers.DjangoTemplates',
)

django.setup()

CURRENCY_CHOICES = [
    ('EUR', 'EUR'),
    ('USD', 'USD'),
    ('GBP', 'GBP'),
    ('JPY', 'JPY'),
    ('AUD', 'AUD'),
    ('CAD', 'CAD'),
    ('CHF', 'CHF'),
]

class CurrencyForm(forms.Form):
    amount = forms.FloatField(label='Amount')
    from_currency = forms.ChoiceField(label='From', choices=CURRENCY_CHOICES)
    to_currency = forms.ChoiceField(label='To', choices=CURRENCY_CHOICES)

def convert(request):
    result = None
    form = CurrencyForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        amount = form.cleaned_data['amount']
        from_cur = form.cleaned_data['from_currency']
        to_cur = form.cleaned_data['to_currency']

        if from_cur == to_cur:
            result = round(amount, 2)
        else:
            url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_cur}&to={to_cur}"
            try:
                resp = requests.get(url)
                data = resp.json()
                rates = data.get('rates')
                if rates and to_cur in rates:
                    result = round(rates[to_cur], 2)
                else:
                    result = "Invalid conversion"
            except Exception as e:
                result = f"Error: {e}"

    result_html = f"<h2>Result: {result}</h2>" if result is not None else ""

    return HttpResponse(f"""
    <html><head><title>Currency Converter</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:40px;">
        <h1>Currency Converter </h1>
        <form method="post">
            {form.as_p()}
            <button type="submit">Convert</button>
        </form>
        {result_html}
    </body></html>
    """)

urlpatterns = [path('', convert)]

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','__main__')
    execute_from_command_line([sys.argv[0],'runserver','8000'])
