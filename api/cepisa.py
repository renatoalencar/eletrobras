# -*- encoding: utf-8 -*-

import sys
import tempfile
from datetime import datetime

import requests
import pytesseract
from PIL import Image
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
  'User-Agent': 'Mozilla/5.0'
}

def decode_catpcha(filename):
    captcha = Image.open(filename).convert('L')
    captcha.putdata(list(map(lambda x: 255 if x > 0 else 0, captcha.getdata())))

    result = pytesseract.image_to_string(captcha)
    result = result.replace('0', 'a').replace(u'®', '0')

    return result.lower()

def get_bill_html(uc, reference):
    return requests.post(
      'http://www.cepisa.com.br/segundavia/fatura.php',
      headers=DEFAULT_HEADERS,
      data={
        'uc': cu,
        'mes_ano': reference.strftime('%m/%Y'),
        'fd': '0'
      }
    ).text

def get_billing_code(cu, reference):
    response = get_bill_html(cu, reference)

    soup = BeautifulSoup(response, 'html.parser')

    return soup.find_all(class_='tamanho14')[1].get_text()

def parse_billing(cu, soup):
    billings = []

    for i in soup:
        reference, due, value, status = i.find_all('td')

        reference = datetime.strptime(reference.get_text(), '%m/%Y')
        status = len(status.find_all('form')) == 0
        
        bill_code = None
        if not status:
          bill_code = get_billing_code(cu, reference)

        billings.append({
          'reference': reference,
          'due': datetime.strptime(due.get_text(), '%d-%b-%y'),
          'value': float(value.get_text().replace('R$ ', '').replace(',', '.')),
          'status': {
              'paid': status,
              'bill_code': bill_code
          }
        })
    
    return billings

def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')

    address = soup.find_all('tr')[4]
    cu, name = soup.find_all('tr')[2].find_all('td')
    billings = parse_billing(cu.get_text(), soup.find_all('tr')[5].table.find_all('tr')[1:])

    return {
      'cu': cu.get_text(),
      'name': name.get_text(),
      'address': address.get_text().replace('\n', ''),
      'billings': billings
    }

def get_billings(cu, cpf):
    captcha_response = requests.get('http://www.cepisa.com.br/segundavia/captcha.php', headers=DEFAULT_HEADERS)
    captcha = tempfile.TemporaryFile()
    captcha.write(captcha_response.content)

    captcha_code = decode_catpcha(captcha)

    response = requests.post(
      'http://www.cepisa.com.br/segundavia/listafaturas.php',
      headers=DEFAULT_HEADERS,
      cookies=captcha_response.cookies,
      data={
        'uc': cu,
        'cpf': cpf,
        'captcha': captcha_code
      }
    )

    return parse_response(response.text)
