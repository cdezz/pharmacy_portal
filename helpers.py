import contextlib
from OpenSSL import crypto
import tempfile
import requests

@contextlib.contextmanager
def pfx_to_pem(pfx_path: str, pfx_password: str) -> str:
    ''' Decrypts the .pfx file to be used with requests. '''
    with tempfile.NamedTemporaryFile(suffix='.pem') as t_pem:
        f_pem = open(t_pem.name, 'wb')
        pfx = open(pfx_path, 'rb').read()
        p12 = crypto.load_pkcs12(pfx, pfx_password)
        f_pem.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey()))
        f_pem.write(crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate()))
        ca = p12.get_ca_certificates()
        if ca is not None:
            for cert in ca:
                f_pem.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        f_pem.close()
        yield t_pem.name

url = 'https://secure.sspcrs.ie/portal/secure-checker-web/sec/check'
url1 = 'https://portal/secure-checker-web/sec/check'
'''
with pfx_to_pem('pcrs_cert.pfx', b'6Nations!') as cert:
    data = {'schemeId': '1G91711A'}
    r = requests.Session()
    res = r.get(url, cert=cert)
    res1 = r.post(url1, data=data, cert=cert)
    print(res1.status_code)
'''