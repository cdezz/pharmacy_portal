Configuration
Python 3.7

git clone https://github.com/cdezz/pharmacy_portal.git

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

move .pfx cert to directory

run fetch_claims.py

### To split pfx file to key and cert. Needed for requests library
```bash
openssl pkcs12 -in file.pfx -out file.pem -nodes
# extract the private key
openssl rsa -in file.pem -out key.pem
# extract the certificate
openssl x509 -in file.pem -out cert.pem
```
