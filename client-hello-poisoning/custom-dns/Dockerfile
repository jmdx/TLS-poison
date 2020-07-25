FROM python:3.7-slim-buster

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 53

CMD ["python", "alternate-dns.py", "ssltest.jmaddux.com,127.0.0.1"]
