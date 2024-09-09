
import os
import shutil
import time
from datetime import datetime
import pandas as pd
import requests

price_regex = '\$?(?:(?:[1-9][0-9]{0,2})(?:,[0-9]{3})+|[1-9][0-9]*|0)(?:[\.,][0-9][0-9]?)?(?![0-9]+)'
currency_regex = '\b(?:[BS]/\.|R(?:D?\$|p))| \b(?:[TN]T|[CJZ])\$|Дин\.|\b(?:Bs|Ft|Gs|K[Mč]|Lek|B[Zr]|k[nr]|[PQLSR]|лв|ден|RM|MT|lei|zł|USD|GBP|EUR|JPY|CHF|SEK|DKK|NOK|SGD|HKD|AUD|TWD|NZD|CNY|KRW|INR|CAD|VEF|EGP|THB|IDR|PKR|MYR|PHP|MXN|VND|CZK|HUF|PLN|TRY|ZAR|ILS|ARS|CLP|BRL|RUB|QAR|AED|COP|PEN|CNH|KWD|SAR)\b|\$[Ub]'
# price_regex = '(?:\b(?:[BS]/\.|R(?:D?\$|p))|\b(?:[TN]T|[CJZ])\$|Дин\.|\b(?:Bs|Ft|Gs|K[Mč]|Lek|B[Zr]|k[nr]|[PQLSR]|лв|ден|RM|MT|lei|zł|USD|GBP|EUR|JPY|CHF|SEK|DKK|NOK|SGD|HKD|AUD|TWD|NZD|CNY|KRW|INR|CAD|VEF|EGP|THB|IDR|PKR|MYR|PHP|MXN|VND|CZK|HUF|PLN|TRY|ZAR|ILS|ARS|CLP|BRL|RUB|QAR|AED|COP|PEN|CNH|KWD|SAR)|\$[Ub]|[\p{Sc}ƒ])\s?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{1,2})?(?!\.?\d)'

date = datetime.today().strftime('%Y-%m')

def export_to_xlsx(data, filename = "DATAFILE" ):
    df_json = pd.DataFrame(data)
    df_json.to_excel(f"{filename}_{date}.xlsx")

def parse_url(url):
    baseurl = "https://ico.org.uk"
    if('ico.org.uk' in url): print('ico in url. using empty baseurl.')
    if('ico.org.uk' in url): baseurl = ""
    return [baseurl, url]

def get_item_text(item):
    if(item):
        return item.text
    return ""

def downloadfiles(files, folder_name = ""):
    foldername = f"{folder_name}_{date}_files"

    if not os.path.isdir(foldername):
        os.makedirs(foldername)

    for file in files:
        download_file(file, foldername)
    

def download_file(url, folder_name):
    local_filename = url.split('/')[-1]
    path = os.path.join("./{}/{}".format(folder_name, local_filename))
    
    header = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

    if not os.path.isfile(path):
        print(f'downloading file: {url}')
        try:
            with requests.get(url, stream=True, headers=header) as r:
                    with open(path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            time.sleep(5) # try and stop it looking like DoS

        except Exception as e:
            print(e.message)
            return
  