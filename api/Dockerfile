FROM python:3-alpine

RUN apk add --update tesseract-ocr build-base python-dev jpeg-dev zlib-dev wkhtmltopdf
RUN pip3 install pipenv
RUN pip3 install gunicorn

WORKDIR /usr/src/app

COPY . .
RUN pipenv install

EXPOSE 8080

CMD [ "pipenv", "run", "gunicorn", "-b", ":8080", "main:app" ]
