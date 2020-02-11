# Introduction

This documentation primarily aims to explain design decisions taken in rustls.
It does this from a few aspects: how rustls attempts to avoid construction vulnerabilities
that occured in other TLS libraries, how rustls attempts to avoid past TLS
protocol vulnerabilities, and assorted advice for achieving common tasks with rustls.

This is a separate concern from API documentation, which can be viewed on [docs.rs](https://docs.rs/rustls/).

