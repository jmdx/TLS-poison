FROM rust:1.40-slim

WORKDIR /app
COPY . .

WORKDIR /app/client-hello-poisoning/custom-tls

RUN cargo build
RUN cargo install --path .

ENV CERTS /app/rustls/test-ca/rsa/end.fullchain
ENV KEY /app/rustls/test-ca/rsa/end.rsa

CMD ["sh", "-c", "/usr/local/cargo/bin/custom-tls --verbose --certs $CERTS --key $KEY -p 443 http"]
