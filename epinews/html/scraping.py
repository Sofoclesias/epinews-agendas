import requests as rq
import re
from bs4 import BeautifulSoup as bs


def known_bad_sites(url):    
    resp = rq.get(url,headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0'})
    soup = bs(resp.content.decode('utf-8'),'html.parser')
    
    if 'gob' in url:
        title = soup.find('h1').get_text()
        body = []
        for div in soup.find('div',attrs={'class':'description feed-content'}).children:
            try:
                body.append(div.get_text())
            except AttributeError as e:
                pass
        body = ' '.join(body)
        
        keywords = None
        tags = None
    elif 'larepublica' in url:
        title = soup.find('h1').get_text()
        body = ' '.join(x.get_text() for x in soup.find_all('p')[:-3])
        keywords = soup.find('meta',{'name':'keywords'}).get('content')
        tags = None
    elif 'elpopular' in url:
        title = soup.find('h1').get_text()
        body = ' '.join([x.get_text() for x in list(soup.find('div',{'class':'MainContent_main__body__LUkri'}).children) if x.name not in ['div','aside','style','script']])
        keywords = soup.find('meta',{'name':'keywords'}).get('content')
        tags = None
    else:
        raise ConnectionRefusedError('URL malo.')
    
    return title, body, keywords, tags, None

class title:
    def __init__(self, doc):
        self.doc = doc
        
class body:
    def __init__(self, doc):
        self.doc = doc
        
class keywords:
    def __init__(self, doc):
        self.doc = doc




    