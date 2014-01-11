'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''

class IMDBCsv(object):
    '''
    Csv content holder
    '''


    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        
    def protected(self):
        return self.username is not None and self.password is not None
        