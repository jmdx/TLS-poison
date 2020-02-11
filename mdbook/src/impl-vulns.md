# A review of implementation vulnerabilities

An important part of engineering involves studying and learning from the mistakes of the past.
It would be tremendously unfortunate to spend effort re-discovering and re-fixing the same
vulnerabilities that were discovered in the past.

## Memory safety

Being written entirely in the safe-subset of Rust immediately offers us freedom from the entire
class of memory safety vulnerabilities.  There are too many to exhaustively list, and there will
certainly be more in the future.

Examples:

- Heartbleed [CVE-2014-0160](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160) (OpenSSL)
- Memory corruption in ASN.1 decoder [CVE-2016-2108](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-2108) (OpenSSL)
- Buffer overflow in read_server_hello [CVE-2014-3466](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-3466) (GnuTLS)

## `goto fail`

This is the name of a vulnerability in Apple Secure Transport [CVE-2014-1266](https://nvd.nist.gov/vuln/detail/CVE-2014-1266).
This boiled down to the following code, which validates the server's signature on the key exchange:

```
    if ((err = SSLHashSHA1.update(&hashCtx, &serverRandom)) != 0)
        goto fail;
    if ((err = SSLHashSHA1.update(&hashCtx, &signedParams)) != 0)
        goto fail;
>       goto fail;
    if ((err = SSLHashSHA1.final(&hashCtx, &hashOut)) != 0)
        goto fail;
```

The marked line was duplicated, likely accidentally during a merge.  This meant
the remaining part of the function (including the actual signature validation)
was unconditionally skipped.

Ultimately the one countermeasure to this type of bug is basic testing: that a
valid signature returns success, and that an invalid one does not.  rustls
has such testing, but this is really table stakes for security code.

Further than this, though, we could consider that the *lack* of an error from
this function is a poor indicator that the signature was valid.  rustls, instead,
has zero-size and non-copyable types that indicate a particular signature validation
has been performed.  These types can be thought of as *capabilities* originated only
by designated signature verification functions -- such functions can then be a focus
of manual code review.  Like capabilities, values of these types are otherwise unforgeable,
and are communicable only by Rust's move semantics.

Values of these types are threaded through the protocol state machine, leading to terminal
states that look like:

```
struct ExpectTraffic {
   (...)
    _cert_verified: verify::ServerCertVerified,
    _sig_verified: verify::HandshakeSignatureValid,
    _fin_verified: verify::FinishedMessageVerified,
}
```

Since this state requires a value of these types, it will be a compile-time error to
reach that state without performing the requisite security-critical operations.

This approach is not infallable, but it has zero runtime cost.

## State machine attacks: EarlyCCS and SKIP


