# import contextlib
# from OpenSSL import crypto
# import tempfile
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import pprint

# @contextlib.contextmanager
# def pfx_to_pem(pfx_path: str, pfx_password: str) -> str:
#     ''' Decrypts the .pfx file to be used with requests. '''
#     with tempfile.NamedTemporaryFile(suffix='.pem') as t_pem:
#         f_pem = open(t_pem.name, 'wb')
#         pfx = open(pfx_path, 'rb').read()
#         p12 = crypto.load_pkcs12(pfx, pfx_password)
#         f_pem.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey()))
#         f_pem.write(crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate()))
#         ca = p12.get_ca_certificates()
#         if ca is not None:
#             for cert in ca:
#                 f_pem.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#         f_pem.close()
#         yield t_pem.name

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import contextlib
import tempfile

@contextlib.contextmanager
def pfx_to_pem(pfx_path: str, pfx_password: str) -> str:
    ''' Decrypts the .pfx file to be used with requests. '''
    with tempfile.NamedTemporaryFile(suffix='.pem') as t_pem:
        with open(t_pem.name, 'wb') as f_pem, open(pfx_path, 'rb') as f_pfx:
            pfx = f_pfx.read()
            private_key, certificate, additional_certificates = load_key_and_certificates(pfx, bytes(pfx_password, 'utf-8'))
            
            # write private key
            f_pem.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

            # write the certificate
            f_pem.write(
                certificate.public_bytes(serialization.Encoding.PEM)
            )

            # write additional certificates
            if additional_certificates is not None:
                for cert in additional_certificates:
                    f_pem.write(
                        cert.public_bytes(serialization.Encoding.PEM)
                    )

        yield t_pem.name


url = 'https://secure.sspcrs.ie/portal/secure-checker-web/sec/check'



def check_phased_status(patients: List[str]) -> Dict:
    status = dict()

    for patient in patients:

        with pfx_to_pem('pcrs_cert.pfx', '6Nations!') as cert:

            data = {'schemeId': patient}
            sesh = requests.Session()
            res = sesh.get(url, cert=cert)

            print(res.status_code)

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

if __name__ == '__main__':
    patients = ['12345678A', '12345678B', '12345678C', '12345678D']
    status = check_phased_status(patients)
    pprint.pprint(status)

