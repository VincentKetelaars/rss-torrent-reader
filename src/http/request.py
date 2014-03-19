'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''
import zlib
from urllib2 import HTTPHandler, HTTPSHandler, HTTPErrorProcessor, HTTPRedirectHandler, HTTPCookieProcessor, build_opener
from urllib import urlencode
from cookielib import CookieJar
from collections import OrderedDict

from src.logger import get_logger
from httplib import IncompleteRead
logger = get_logger(__name__)

IMDBLOGIN = "https://secure.imdb.com/register/login?ref_=nv_usr_lgin_3"

class Request(object):
    '''
    This class takes a string that represents a URL and obtains the content
    '''

    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
    
    def imdb_csv_request(self):
        if not self.username or not self.password or not "imdb.com" in self.url:
            return None
        
        form = OrderedDict([("49e6c", "378"), ("login", self.username), ("password",  self.password)])
        
        content = None
        try:
            cj = CookieJar()
            opener = build_opener(HTTPHandler(), HTTPSHandler(), HTTPErrorProcessor(), 
                         HTTPRedirectHandler(), HTTPCookieProcessor(cj))
            params = urlencode(form)
            response = opener.open(IMDBLOGIN, params)
            
            # cookies automatically sent
            response2 = opener.open(self.url)
            if response2.getcode() == 200:
                content = response2.read()
            else:
                logger.debug("Got code %d and %s for %s", response2.getcode(), response2.read(), self.url)
        except:
            logger.exception("Can't retrieve CSV page %s", self.url)
        finally:
            try: # response, or response2 might not exist
                response.close()
                response2.close()
            except:
                pass
        
        if content is not None:
            logger.info("Request for %s returns content of length %d", self.url, len(content))
        return content
    
    def request(self):
        content = None
        try:
            opener = build_opener(HTTPHandler(), HTTPErrorProcessor(), HTTPRedirectHandler())
            opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Spoof User agent
            response = opener.open(self.url)
            if response.getcode() == 200:
                content = response.read()
                encoding = response.info().get("Content-Encoding")
                if encoding is not None:
                    if encoding == "gzip":
                        content = zlib.decompress(content, 16+zlib.MAX_WBITS)
                    else:
                        logger.warning("Don't know encoding %s", encoding)                        
            else:
                logger.debug("Got code %d and %s for %s", response.getcode(), response.read(), self.url)
        except IncompleteRead as e: # Probably the servers fault
            content = e.partial # Let's hope it's not encoded
            logger.debug("We've got an IncompleteRead, partial content of length %d", len(content))
        except:
            # TODO: Retry in some cases..
            logger.exception("Can't retrieve request %s", self.url)
        finally:
            try:
                response.close()
            except:
                pass
            
        return content