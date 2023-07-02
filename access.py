import requests
# from bs4 import BeautifulSoup
import re
# from db import insert_notification
# from OpenSSL import crypto


def local_handler():
    url = 'https://secure.sspcrs.ie/secure/hthubweb/sec/pharm/notifications'
    
    # path to your certificate and private key
    cert_file_path = "cert2.pem"
    key_file_path = "key2.pem"

    # cert = "pcrs_cert.pem"    
    client = requests.session()
    # if you work with a .pem file, you simply use 'cert='/myPEMFile.pem' after dumping the key/cert data in the .pem file

    c = client.get(url, cert=(cert_file_path, key_file_path))
    # c = client.get(url, cert=cert)
    # print ('Body: ' + c.text)
    # print (c.cookies)
    print('First request status: ' + str(c.status_code))

local_handler()
