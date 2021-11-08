FROM python:3.7-slim-buster

# This should be the IP of the custom-TLS box
ENV INITIAL_IP 127.0.0.1
# This should be the domain you own with the NS record
ENV DOMAIN ssltest.jmaddux.com
# This will be 127.0.0.1 or something internal to the machine
# you're SSRF'ing.  If you're just testing that a TLS client
# persists sessions, you can set this to a public box with
# netcat or similar exposed.
ENV TARGET_IP 127.0.0.1

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 53/udp

CMD ["sh", "-c", "python alternate-dns.py ${DOMAIN},${TARGET_IP} -b 0.0.0.0 -t ${INITIAL_IP} -d 8.8.8.8"]
