'''
Created on Jul 3, 2018

@author: cwill327
'''
import requests, sys, time, os
from doiparser import doiparser
from webrequests import webrequests

lastRequest=None
allowance=None
interval=None
response=None
goodDOIs=[]
links=[]
etiquette='mailto:'+sys.argv[2] #Include email address to be sent to polite users pool

if __name__ == '__main__':
    if not os.path.isdir(os.path.expanduser('~/Documents/')+'articles/'):
        os.makedirs(os.path.expanduser('~/Documents/')+'articles/')
    
    #Parse DOIs and store them in a list
    parser=doiparser(sys.argv[1])
    doiList=parser.parse()
    
    webmaster=webrequests()
    
    
    #Make sure DOIs provided are CrossRef DOIs
    for doi in doiList:
        
        #Rate limit stuff
        while lastRequest and (time.time()<(lastRequest+(interval/allowance))):
            time.sleep((lastRequest+(interval/allowance))-time.time())
            
        #Make sure DOIs are CrossRef DOIs
        authResponse=webmaster.auth(doi, etiquette)
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
        metaResponse=webmaster.meta(doi, etiquette)
            
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
            
    with open('linkInfo', 'w+') as f:
        for x in links:
            for y in x:
                f.write((str)(y)+'\t')
            
    for articleInfoList in links:
        
        #Don't exceed rate limits
        while lastRequest and (time.time()<(lastRequest+(interval/allowance))):
            time.sleep((lastRequest+(interval/allowance))-time.time())
            
        lastRequest=time.time()
        
        webmaster.getArticle(link=articleInfoList[1], doi=articleInfoList[0], cRefToken=sys.argv[3])
           
    print 'All done!'       
        
        