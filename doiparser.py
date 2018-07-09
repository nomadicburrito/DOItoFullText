'''
Created on Jul 3, 2018

@author: cwill327
'''

class doiparser():
    '''
    classdocs
    '''
    
    

    def __init__(self, doiFile):
        '''
        Constructor
        '''
        self.fileName=doiFile
        self.doiList=[]
        
    def parse(self):
        with open(self.fileName, 'r') as x:
            for line in x:
                self.doiList.append(line.strip())
                
                
        return self.doiList
            