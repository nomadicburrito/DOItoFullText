'''
Created on Jul 3, 2018

@author: cwill327
'''
import requests, re, os

class webrequests():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.session=requests.Session()
        
    def auth(self, doi=None, etiquette=None):
        
        self.doi=doi
        self.etiquette=etiquette
        
        response = self.session.head('https://api.crossref.org/works/'+self.doi+'/agency?'+self.etiquette)
        
        self.authResponse={'Status':response.status_code, 
                           'Limit':int(filter(str.isdigit, response.headers.get('X-Rate-Limit-Limit'))),
                           'Interval':int(filter(str.isdigit, response.headers.get('X-Rate-Limit-Interval')))}
        
        return self.authResponse
    
    def meta(self, doi=None, etiquette=None):
        
        self.doi=doi
        self.etiquette=etiquette
        self.publisher=None
        self.link=None
        self.license=None
        
        response = self.session.get('https://api.crossref.org/works/'+self.doi+'?'+self.etiquette)
        
        if response.status_code == requests.codes.ok:
            try:
                self.publisher=re.search('publisher.{3}([^"]*)', response.content).group(1)
                
            #if self.publisher != None:
            #   self.publisher = self.publisher.group(1)
        
                if 'xml' in response.content:
                    self.link=re.search(r'URL":"(https?[^\}\]"]+xml[^"]*)', response.content).group(1).replace('\\','').replace('PII:','pii/')
                elif 'pdf' in response.content:
                    self.link=re.search(r'link.{5}URL.{3}(https?[^"]+pdf[^"]*)', response.content).group(1).replace('\\','').replace('PII:','pii/')
                elif 'link' in response.content:
                    self.link=re.search(r'link.{5}URL.{3}(https?[^"]+)', response.content).group(1).replace('\\','').replace('PII:','pii/')
                else:
                    self.link=re.search(r'URL.{3}(https?[:\\/]+dx.doi[^"]+)', response.content).group(1).replace('\\','').replace('PII:','pii/')
                
                self.license=re.search(r'[lL]icense.+URL.{3}(https?[^"]+)', response.content)
                if self.license==None:
                    self.license='N/A'
                else:
                    self.license.group(1).replace('\\','')
                
                return {'Status':response.status_code,
                    'Publisher':self.publisher,
                    'Link':self.link,
                    'License':self.license,
                    'Limit':int(filter(str.isdigit, response.headers['X-Rate-Limit-Limit'])),
                    'Interval':int(filter(str.isdigit, response.headers['X-Rate-Limit-Interval']))}
            except StandardError as error:
                return (str)(response.content)+'\n '+self.doi+'\n'+(str)(error)+'\nhttps://api.crossref.org/works/'+self.doi+'?'+self.etiquette
                
        else:
            return {'Status':response.status_code,
                'Limit' : int(filter(str.isdigit, response.headers['X-Rate-Limit-Limit'])),
                'Interval' : int(filter(str.isdigit, response.headers['X-Rate-Limit-Interval']))}

    def getArticle(self, cRefToken, link, doi):
        
        headers={'CR-Clickthrough-Client-Token':cRefToken, 'Accept':'application/xml, text/xml, application/xhtml+xml; q=.7, application/pdf', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}#'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}          
        
        try:
            
            session=requests.Session()
            
            if 'plos' in link or 'pone' in link:
                response=session.get(link, headers=headers)
                response=session.get(response.url.replace('http://journals.plos.org/plosone/article', 'http://journals.plos.org/plosone/article/file')+'&type=manuscript', headers=headers, allow_redirects=False)
            elif 'springer' in link:
                response=session.get('https://link.springer.com/'+doi+r'.pdf')
            else:
                response=session.get(link, headers=headers)
        
            if response.status_code == requests.codes.ok:
                #if 'xml' in link:
                ending=re.search(r'Content-Type.{4}[^/]+/([a-zA-Z]+)', (str)(response.headers)).group(1)
                with open(os.path.expanduser('~/Documents/articles/')+doi.replace('/', '_')+'.'+ending, 'w+') as f:
                    f.write(response.content) 
            else:
                print 'Bad request:  '+(str)(response.status_code)+'\t'+doi+'\n'+link+'\n'+(str)(response.history)
        except requests.exceptions.Timeout as e:
            print 'Could not get article due to timeout:\n'+link+'\n'+(str)(e)
        except requests.exceptions.ConnectionError as e:
            print 'Could not connect to host\n'+link+'\n'+(str)(e)