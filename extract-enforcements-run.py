from bs4 import BeautifulSoup
import requests
import re
from dateparser.search import search_dates
from helpers import downloadfiles, parse_url, export_to_xlsx, get_item_text, price_regex, currency_regex

def get_links_from_list(list, baseurl):
    links = []
    if list:
        for a in list.find_all('a', href=True):
            # print(a)
            if(a.get('href')):
                if(a.get('href').endswith('.pdf')):
                    links.append(f'{baseurl}{a.get("href")}')
    return links

def get_subpage_items(subpage_url):
    [baseurl, url] = parse_url(subpage_url)
    fullurl = f'{baseurl}{url}'
    print(f'getting subpage items for: {fullurl}')
    
    response = requests.get(fullurl, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")

    description = ''
    links = []

    maincolumn = content.find('div', attrs={'class': 'maincolumn'})
    if not maincolumn: return [description, links]
    
    content = maincolumn.find('div', attrs={'class': 'article-content'})
    aside = maincolumn.find('aside', attrs={'class': 'aside-further'})
    if not content and not aside: return [description, links]

    for d in content.find_all('p'):
        description+=str(d)

    filelist = []
    if content is not None:
        filelist = get_links_from_list(maincolumn.find('ul'), baseurl)
    
    asidelist = []
    # print('aside? ' + aside)
    if aside is not None:
        asidelist = get_links_from_list(aside.find('ul'), baseurl)

    links = filelist + asidelist

    return [description, links]

def scrape_page(url_to_scrape):
    response = requests.get(url_to_scrape, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")

    list = content.find('div', attrs={'class': 'resultlist'})
    if not list:
        print('nothing to scrape')
        exit
    
    page_data = []
    
    for itemlink in list.findAll('div', { 'class': 'itemlink'}):

        item = itemlink.find('a', { 'class': 'itemlink-content'})
        if not item:
            print('no itemlink-content found')
            continue

        url = item.get('href')
        tagline = get_item_text(item.find('p', attrs={"class": "text-small"}))
        title = get_item_text(item.find('h2', attrs={"class": "h3"}))

        [description, files] = get_subpage_items(url)

        # TODO: work on stopping it looking like DoS
        downloadfiles(files, "ENFORCEMENTS")

        price_search = re.findall(price_regex, description)
        # currency_search = re.findall(currency_regex, description)
        has_price = 1 if (len(price_search) == 1) else 0
        tagline_date = search_dates(tagline)[0][0]
        
        listObject = {
            "title": title,
            "tagline": tagline,
            "description": description,
            "date": tagline_date,
            "categories": tagline.lstrip(tagline_date).lstrip(' , '),
            "amount": price_search[0] if has_price else None,
            "reviewed": 0,
            "files": ", ".join(files)
        }
        
        page_data.append(listObject)

    return page_data


enforcement_data = scrape_page('https://ico.org.uk/action-weve-taken/enforcement?facet_date=last_year')
export_to_xlsx(enforcement_data, "ENFORCEMENTS")