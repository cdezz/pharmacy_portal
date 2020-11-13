import contextlib
from OpenSSL import crypto
import tempfile
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import pprint

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



def check_phased_status(patients: List[str]) -> Dict:
    status = dict()

    for patient in patients:

        with pfx_to_pem('pcrs_cert.pfx', b'6Nations!') as cert:

            data = {'schemeId': patient}
            sesh = requests.Session()
            res = sesh.get(url, cert=cert)

            soup = BeautifulSoup(res.text, 'html.parser')
            csrf_token = soup.find('input', {'name': '_csrf'}).get('value')
            data['_csrf'] = csrf_token

            res1 = sesh.post(url, cert=cert, data=data)

            soup_1 = BeautifulSoup(res1.text, "html.parser")
            div = soup_1.find_all('span', {'class': 'col-6 col-md-9 d-flex align-items-end'})[-2:]
            approvals = [element.get_text().strip() for element in div]

            phased_approval = 'Approved for phased dispensing under reason'
            no_phased_approval = 'Patient is NOT approved for phased dispensing'
            special_drug_approvals = ''
            no_special_drug_approvals = 'This Patient has no Special Drug Approvals'

            phased_status, special_drug_status = approvals
            if 'NOT' in phased_status:
                status[patient] = 'Not Approved for Phased Dispensing'
            else:
                status[patient] = 'Approved for Phased Dispensing'

    return status


