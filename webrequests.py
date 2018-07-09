'''
Created on Jul 3, 2018

@author: cwill327
'''
import requests, re

class webrequests():
    '''
    classdocs
    '''


    def __init__(self, doi=None, etiquette=None, link=None):
        '''
        Constructor
        '''
        self.doi=doi
        self.etiquette=etiquette
        self.link=link
        
    def auth(self):
        
        response = requests.head('https://api.crossref.org/works/'+self.doi+'/agency?'+self.etiquette)
        
        self.authResponse={'Status':response.status_code, 
                           'Limit':int(filter(str.isdigit, response.headers.get('X-Rate-Limit-Limit'))),
                           'Interval':int(filter(str.isdigit, response.headers.get('X-Rate-Limit-Interval')))}
        
        return self.authResponse
    
    def meta(self):
        self.publisher=None
        self.link=None
        self.license=None
        
        response = requests.get('https://api.crossref.org/works/'+self.doi+'?'+self.etiquette)
        
        if response.status_code == requests.codes.ok:
            try:
                self.publisher=re.search('publisher.{3}([^"]*)', response.content).group(1)
                
            #if self.publisher != None:
            #   self.publisher = self.publisher.group(1)
        
                if 'xml' in response.content:
                    self.link=re.search('URL":"(http[^\}\]"]*xml)', response.content).group(1).replace('\\','').replace('PII:','pii/').replace('http:','https:')
                elif 'pdf' in response.content:
                    self.link=re.search('link.{5}URL.{3}(http[^"]*pdf[^"]+)', response.content).group(1).replace('\\','').replace('PII:','pii/').replace('http:','https:')
                else:
                    self.link=re.search('link.{5}URL.{3}(http[^"]+)', response.content).group(1).replace('\\','').replace('PII:','pii/').replace('http:','https:')
                
                self.license=re.search('[lL]icense.+URL.{3}(http[^"]*)', response.content)
                if self.license==None:
                    self.license='N/A'
                else:
                    self.license.group(1).replace('\\','').replace('PII:','pii/').replace('http:','https:')
                
                return {'Status':response.status_code,
                    'Publisher':self.publisher,
                    'Link':self.link,
                    'License':self.license,
                    'Limit':int(filter(str.isdigit, response.headers['X-Rate-Limit-Limit'])),
                    'Interval':int(filter(str.isdigit, response.headers['X-Rate-Limit-Interval']))}
            except StandardError as error:
                return (str)(response.content)+'\n '+self.doi+'\n'+(str)(error)
                
        else:
            return {'Status':response.status_code,
                'Limit' : int(filter(str.isdigit, response.headers['X-Rate-Limit-Limit'])),
                'Interval' : int(filter(str.isdigit, response.headers['X-Rate-Limit-Interval']))}
            '''
    def elsevier(self, cRefToken, link, apiKey, doi):   
        
        if apiKey != None:
            headers={'X-ELS-APIKey':apiKey,'CR-Clickthrough-Client-Token':cRefToken}
        else:
            headers={'CR-Clickthrough-Client-Token':cRefToken}
            
        response=requests.get(link, headers=headers)
        
        if response.status_code == requests.codes.ok:
            with open(doi.replace('/', '_')+'.xml', 'w+') as f:
                f.write(response.content)
        else:
            print 'Bad Elsevier request: '+response.status_code+'\n'+response.content
            '''
    def getArticle(self, cRefToken, link, doi, apiKey):
        
        print 'Got to the last method'
        
        if apiKey != None:
            headers={'X-ELS-APIKey':apiKey,'CR-Clickthrough-Client-Token':cRefToken}
        else:
            headers={'CR-Clickthrough-Client-Token':cRefToken}
            
        response=requests.get(link, headers=headers)
        
        if response.status_code == requests.codes.ok:
            if 'xml' in link:
                with open(doi.replace('/', '_')+'.xml', 'w+') as f:
                    f.write(response.content) 
            else:
                with open(doi.replace('/', '_')+'.pdf', 'w+') as f:
                    f.write(response.content)
        else:
            print 'Bad request:  '+response.status_code+'\n'+response.content
            
        #sdkfgjbhkl
        
        
        
        
        
