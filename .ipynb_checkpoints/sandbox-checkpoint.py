import requests

base_url = 'https://www.fincaraiz.com.co/'

r = requests.get(base_url)
print(r.text)