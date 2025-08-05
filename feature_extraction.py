import re
import socket
import urllib
from urllib.parse import urlparse
from datetime import datetime
import whois
import requests

def count_special_chars(url, char):
    return url.count(char)

def extract_features_from_url(url):
    features = []

    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''

    features.append(len(url))
    features.append(len(hostname))

    try:
        socket.inet_aton(hostname)
        features.append(1)
    except:
        features.append(0)

    features.extend([
        url.count('.'),
        url.count('-'),
        url.count('@'),
        url.count('?'),
        url.count('&'),
        url.count('='),
        url.count('_'),
        url.count('~'),
        url.count('%'),
        url.count('/'),
        url.count('*'),
        url.count(':'),
        url.count(','),
        url.count(';'),
        url.count('$'),
        url.count(' '),
        url.lower().count('www'),
        url.lower().count('.com'),
        url.lower().count('//')
    ])

    features.append(1 if 'http' in path else 0)
    features.append(1 if 'https' in url[8:] else 0)

    digits_url = sum(c.isdigit() for c in url)
    features.append(digits_url / len(url) if len(url) > 0 else 0)
    digits_host = sum(c.isdigit() for c in hostname)
    features.append(digits_host / len(hostname) if len(hostname) > 0 else 0)

    features.append(1 if 'xn--' in url else 0)
    features.append(1 if parsed.port else 0)
    features.append(1 if re.search(r'\.[a-z]{2,}$', path) else 0)
    features.append(1 if re.search(r'\.[a-z]{2,}$', hostname.split('.')[0]) else 0)
    features.append(1 if len(hostname.split('.')) > 3 else 0)
    features.append(len(hostname.split('.')))
    features.append(1 if '-' in hostname else 0)
    features.append(1 if re.match(r'[a-z0-9]{10,}\.com', hostname) else 0)
    features.append(1 if any(s in url for s in ['bit.ly', 'tinyurl.com', 'goo.gl']) else 0)
    features.append(1 if '.' in path else 0)

    features.append(url.count('//') - 1)
    features.append(1 if re.match(r'https?://[^/]*//', url) else 0)

    words = re.split(r'\W+', url)
    host_words = hostname.split('.')
    path_words = path.split('/')

    features.append(len(words))
    features.append(1 if re.search(r'(.)\1{3,}', url) else 0)
    features.append(min([len(w) for w in words if w] + [0]))
    features.append(min([len(w) for w in host_words if w] + [0]))
    features.append(min([len(w) for w in path_words if w] + [0]))
    features.append(max([len(w) for w in words if w] + [0]))
    features.append(max([len(w) for w in host_words if w] + [0]))
    features.append(max([len(w) for w in path_words if w] + [0]))
    features.append(sum(len(w) for w in words) / (len(words) or 1))
    features.append(sum(len(w) for w in host_words) / (len(host_words) or 1))
    features.append(sum(len(w) for w in path_words) / (len(path_words) or 1))

    features.append(url.lower().count("phish"))
    features.append(1 if "domain" in hostname else 0)
    features.append(1 if "brand" in hostname else 0)
    features.append(1 if "brand" in path else 0)
    features.append(1 if hostname.endswith(".tk") else 0)

    # Whois info (3 features)
    try:
        domain = whois.whois(hostname)
        features.append(1 if domain.domain_name else 0)
        exp = domain.expiration_date
        upd = domain.updated_date
        if isinstance(exp, list):
            exp = exp[0]
        if isinstance(upd, list):
            upd = upd[0]
        reg_length = (exp - upd).days if exp and upd else 0
        features.append(reg_length if reg_length > 0 else 0)

        creation = domain.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        age = (datetime.now() - creation).days if creation else 0
        features.append(age if age > 0 else 0)
    except:
        features.extend([0, 0, 0])

    # Web traffic, DNS, Google index, Page rank
    features.append(0)  # web_traffic dummy
    features.append(1)  # dns_record
    features.append(1)  # google_index
    features.append(0)  # page_rank dummy

    return features

