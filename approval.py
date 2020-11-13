# Script to check if patients have phased approval and any special drug approvals e.g Versatis
# feed list of scheme id's into main function

import helpers
from typing import List, Dict
import pprint
import requests
from bs4 import BeautifulSoup


# main module function
def check_patients(phased_patients: List[str] = None, special_drug_patients: List[str] = None):
    """
    phased patients --> all patients you want to check if they have phased approval
    special_drug_patients --> all patients you want to check if they have any special drug approvals
    """

    if not phased_patients and not special_drug_patients:
        return 'No Patients to check'
    elif phased_patients and special_drug_patients:
        return {**check_phased_status(phased_patients), **check_special_drug_approval_status(special_drug_patients)}
    elif phased_patients:
        return check_phased_status(phased_patients)
    else:
        return check_special_drug_approval_status(special_drug_patients)


def check_phased_status(patients: List[str]) -> Dict:
    url = 'https://secure.sspcrs.ie/portal/secure-checker-web/sec/check'

    # dict to hold phased status
    status = dict()

    for patient in patients:

        with helpers.pfx_to_pem('pcrs_cert.pfx', b'secret-key') as cert:

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

            phased_status, special_drug_status = approvals
            if 'NOT' in phased_status:
                status[patient] = 'Not Approved for Phased Dispensing'
            else:
                status[patient] = 'Approved for Phased Dispensing'

    # nested dict to make it easier when pprinting
    phased = dict()
    phased['phased_patients'] = status
    return phased


def check_special_drug_approval_status(patients: List[str]) -> Dict:

    url = 'https://secure.sspcrs.ie/portal/secure-checker-web/sec/check'

    status = dict()

    for patient in patients:

        with helpers.pfx_to_pem('pcrs_cert.pfx', b'secret-key') as cert:

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

            phased_status, special_drug_status = approvals
            status[patient] = special_drug_status
    # another nested dict for ease of viewing
    special_approvals = dict()
    special_approvals['Special Drug Approvals'] = status
    return special_approvals


if __name__ == '__main__':
    # pts = ['1234567A', ..... ]
    pprint.pprint(check_patients(special_drug_patients=pts, phased_patients=pts))


