###################################################
# Usage:
# 1. Export SHA certificate from web browser as .pfx file
# 2. Move it to this working directory
# 3. Pulling most recent claim file is default setting
# -> claims = FetchClaims(pfx_path='pcrs_cert.pfx', pfx_password='your_private_key')
# -> this will fetch most recent GMS and DPS pdf files and download them to working dir
# 4. More than one month, make sure to write in string format e.g '202005' :
# -> claims = FetchClaims(pfx_path='pcrs_cert.pfx', pfx_password='your_private_key',
#                         first_month='202007', last_month='202002')
# -> This should fetch pdfs from February 2020 to July 2020


from helpers import pfx_to_pem
import os
import requests
from bs4 import BeautifulSoup
from typing import List


class FetchClaims:

    default_options = {
        'first_month': 'current',
        'last_month': None,
        'pfx_path': None,
        'pfx_password': None
    }

    def __init__(self, **kwargs):
        '''
        Fetches all claims in a specified date range
        :param kwargs: date range or defaults to most recent month
        '''
        self.options = {**FetchClaims.default_options, **kwargs}
        self.validate()

        with pfx_to_pem(self.options['pfx_path'], (self.options['pfx_password'].encode())) as cert:
            self.cert = cert
            # full list of urls in PCRS site
            all_claim_files = self.fetch_all_claim_files()
            # list reduced to files requested to be downloaded
            user_requested_files = self.filter_requested_files(all_claim_files)
            # downloads pdfs to cwd
            self.download_requested_files(user_requested_files)

    def __getitem__(self, key):
        return self.options[key]

    def fetch_all_claim_files(self):
        '''
        Gathers all urls to pdfs on PCRS website
        :return: list of urls
        '''
        claims_url = 'https://secure.sspcrs.ie/secure/listings/sec/pharmacy/' \
                     'list/gms?backLink=/portal/pharmsuite/sec/reporting&backLinkDesc=Pharmacy%20Suite'

        r = requests.Session()
        res = r.get(claims_url, cert=self.cert)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.findAll('a')
        links = [link.get('href') for link in links if link.get('href').endswith('pdf')]
        links = sorted(links, key=lambda x: x.split('/')[-1], reverse=True)
        return links

    def filter_requested_files(self, all_claim_files: List[str]) -> List[str]:
        '''
        Will filter url list to default (most recent month or a specified date range
        :param all_claim_files: list of all PCRS urls
        :return: filtered list of months to download
        '''
        if self.options['first_month'] == 'current' and not self.options['last_month']:
            current_month = all_claim_files[:1]
        # default
            return current_month

        else:
            # gets indexes of files requested
            index_1 = 0
            for i, link in enumerate(all_claim_files):
                if self.options['first_month'] in link:
                    index_1 = i
                if self.options['last_month'] in link:
                    index_2 = i + 1
            filtered_claim_files = all_claim_files[index_1:index_2]
            return filtered_claim_files

    def download_requested_files(self, user_requested_files: List[str]):
        '''
        Iterates through list and downloads pdfs
        :param user_requested_files: urls to be downloaded
        :return:
        '''
        for link in user_requested_files:
            gms_link = 'https://secure.sspcrs.ie' + link
            res = requests.get(gms_link, cert=self.cert)
            with open(f"{gms_link.split('=')[-1]}", 'wb') as f:
                f.write(res.content)
            dps_link = gms_link.replace('gms', 'dps')
            res = requests.get(dps_link, cert=self.cert)
            with open(f"{dps_link.split('=')[-1].replace('statement', 'statement(1)')}", 'wb') as f:
                f.write(res.content)


    def validate(self):
        '''
        Validates keyword arguments are valid.
        :return: Nothing if kwargs are valid exception otherwise
        '''
        if not os.path.exists(self.options['pfx_path']):
            raise Exception('This path is not valid. Move .pfx file to current working directory')
        if not self.options['pfx_password']:
            raise Exception('You must enter a password for your certificate')
        if self.options['first_month'] != 'current' and int(self.options['first_month']) < int(self.options['last_month']):
            raise Exception("First month must always be more recent than last_month")


if __name__ == '__main__':
    claims = FetchClaims(pfx_path='pcrs_cert.pfx', pfx_password='6Nations!', first_month='202007', last_month='202005')