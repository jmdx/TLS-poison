# A review of protocol vulnerabilities

## CBC MAC-then-encrypt ciphersuites

Back in 2000 [Bellare and Namprempre](https://eprint.iacr.org/2000/025) discussed how to make authenticated
encryption by composing separate encryption and authentication primitives.  That paper included this table:

| Composition Method | Privacy || Integrity ||
|--------------------|---------||-----------||
|| IND-CPA | IND-CCA | NM-CPA | INT-PTXT | INT-CTXT |
| Encrypt-and-MAC | insecure | insecure | insecure | secure | insecure |
| MAC-then-encrypt | secure | insecure | insecure | secure | insecure |
| Encrypt-then-MAC | secure | secure | secure | secure | secure |

One may assume from this fairly clear result that encrypt-and-MAC and MAC-then-encrypt compositions would be quickly abandoned
in favour of the remaining proven-secure option.  But that didn't happen, not in TLSv1.1 (2006) nor in TLSv1.2 (2008).  Worse,
both RFCs included incorrect advice on countermeasures for implementors, suggesting that the flaw was "not believed to be large
enough to be exploitable".

[Lucky 13](http://www.isg.rhul.ac.uk/tls/Lucky13.html) (2013) exploited this flaw and affected all implementations, including
those written [after discovery](https://aws.amazon.com/blogs/security/s2n-and-lucky-13/). OpenSSL even had a
[memory safety vulnerability in the fix for Lucky 13](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-2107), which
gives a flavour of the kind of complexity required to remove the side channel.

rustls does not implement CBC MAC-then-encrypt ciphersuites for these reasons.  TLS1.3 removed support for these
ciphersuites in 2018.

There are some further rejected options worth mentioning: [RFC7366](https://tools.ietf.org/html/rfc7366) defines
Encrypt-then-MAC for TLS, but unfortunately cannot be negotiated without also supporting MAC-then-encrypt
(clients cannot express "I offer CBC, but only EtM and not MtE").

## BEAST

## CRIME

## Logjam

## SWEET32

## FREAK

## DROWN

## Poodle

## GCM nonces

## 3SHAKE / Renegotiation

## RSA PKCS#1 encryption
