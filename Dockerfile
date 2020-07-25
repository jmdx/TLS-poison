FROM rust:1.37-slim

WORKDIR /app
COPY . .

WORKDIR /app/client-hello-poisoning/custom-tls

RUN cargo build
RUN cargo install --path .

CMD ["/usr/local/cargo/bin/custom-tls", "--verbose", "--certs", "/app/rustls/test-ca/rsa/end.fullchain", "--key", "/app/rustls/test-ca/rsa/end.rsa", "-p", "8443", "http"]
