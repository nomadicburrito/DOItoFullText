'''
Created on Jul 3, 2018

@author: cwill327
'''
import requests, sys, time
from doiparser import doiparser
from webrequests import webrequests

lastRequest=None
allowance=None
interval=None
response=None
goodDOIs=[]
links=[]
etiquette='mailto:'+sys.argv[2] #Include email address to be sent to polite users pool
elsevierApiKey=None #Elsevier wants you to use an api key, but not necessary with cross ref

if len(sys.argv)>4: #if we have a elsevier key, use it
    elsevierApiKey=sys.argv[4]

if __name__ == '__main__':
    
    #Parse DOIs and store them in a list
    parser=doiparser(sys.argv[1])
    doiList=parser.parse()
    
    
    #Make sure DOIs provided are CrossRef DOIs
    for doi in doiList:
        
        #Rate limit stuff
        while lastRequest and (time.time()<(lastRequest+(interval/allowance))):
            time.sleep((lastRequest+(interval/allowance))-time.time())
            
        #Make sure DOIs are CrossRef DOIs
        authenticator=webrequests(doi, etiquette)
        authResponse=authenticator.auth()
        lastRequest=time.time()
       # print lastRequest
        
        #Update Rate limits
        allowance=authResponse.get('Limit')
        interval=authResponse.get('Interval')
        
        #if DOI is a CrossRef DOI, add it to the list of good DOIs
        if authResponse.get('Status') == requests.codes.ok:
            goodDOIs.append(doi)
        else:
            print 'DOI is not a CrossRef DOI: '+doi
            
    
    print 'Working on metadata'
    #Query CrossRef for metadata of all of the good DOIs
    for doi in goodDOIs:
        
        #Don't exceed rate limits
        while lastRequest and (time.time()<(lastRequest+(interval/allowance))):
            time.sleep((lastRequest+(interval/allowance))-time.time())
        
        #Make requests for metadata
        meta=webrequests(doi, etiquette)
        metaResponse=meta.meta()
            
        if type(metaResponse)!=dict:
            print metaResponse
            sys.exit()
            
        lastRequest=time.time()
        
        #Update Rate limits
        allowance=metaResponse.get('Limit')
        interval=metaResponse.get('Interval')
        
        if metaResponse.get('Status') == requests.codes.ok:
            links.append([doi, metaResponse['Link'],metaResponse['Publisher'], metaResponse['License']])
        else:
            print 'Bad metadata request: '+doi
            
            
    for articleInfoList in links:
        
        #Don't exceed rate limits
        while lastRequest and (time.time()<(lastRequest+(interval/allowance))):
            time.sleep((lastRequest+(interval/allowance))-time.time())
            
        lastRequest=time.time()
        
        articles=webrequests()
        articles.getArticle(link=articleInfoList[1], doi=articleInfoList[0], cRefToken=sys.argv[3], apiKey=elsevierApiKey)
        
            
            #sadjkfhkdk
    
            
    print links        
        
        