This is a minimal django application that uses memcached.  You can use it to replicate the browser-image-tag-based CSRF-to-RCE phishing demo. 
It may seem somewhat contrived, but you can find plenty of apps that make similar calls to `django.core.cache` around Github.

Credit goes [here](https://github.com/rnevius/minimal-django) for getting me started quickly.
