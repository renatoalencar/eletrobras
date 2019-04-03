import os
import datetime

import pdfkit
from flask import Flask, request, jsonify, make_response

from cepisa import get_billings, get_bill_html


app = Flask(__name__)

@app.route('/bills')
def bills():
    cu = request.args.get('cu')
    cpf = request.args.get('cpf')

    retries = 0
    while True:
      try:
        bills = get_billings(cu, cpf)

        return jsonify(bills)
      except IndexError as e:
        if retries >= 3:
          raise e
        else:
          retries += 1

@app.route('/bills/<string:uc>-<string:reference>.pdf')
def bill_pdf(uc, reference):
    ref = datetime.datetime.strptime(reference, '%m/%Y')

    html = get_bill_html(uc, ref)

    response = make_response(pdfkit.from_string(html, False), 200)
    response.headers['Content-Type'] = 'application/pdf'

    return response


if __name__ == '__main__':
    app.run(
      host='0.0.0.0',
      port=os.environ.get('PORT', 5000),
      debug=os.environ.get('ENVIRONMENT', 'production') == 'development'
    )