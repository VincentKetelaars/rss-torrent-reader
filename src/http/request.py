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
            content = self._request(opener, self.url)
        except:
            logger.exception("Can't retrieve %s", IMDBLOGIN)
        finally:
            try: # response, or response2 might not exist
                response.close()
            except:
                pass
            
        if content is not None:
            logger.info("Request for %s returns content of length %d", self.url, len(content))
        return content
    
    def request(self):
        opener = build_opener(HTTPHandler(), HTTPErrorProcessor(), HTTPRedirectHandler(), HTTPSHandler())
        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Spoof User agent
        return self._request(opener, self.url)
    
    def _request(self, opener, url):
        content = None
        content_type = None
        try:
            response = opener.open(url)
            if response.getcode() == 200:
                content = response.read()
                try:
                    content_type = response.info().get("Content-Type").split('charset=')[-1]
                except:
                    logger.exception("Can't obtain charset, resorting to default")
                    content_type = "utf-8"
                encoding = response.info().get("Content-Encoding")
                if encoding is not None and content is not None and len(content) > 0:
                    if encoding == "gzip":
                        try:
                            content = zlib.decompress(content, 16+zlib.MAX_WBITS)
                        except:
                            logger.exception("Error with content: %s". content)
                    else:
                        logger.warning("Don't know encoding %s", encoding)                        
            else:
                logger.debug("Got code %d and %s for %s", response.getcode(), response.read(), url)
        except IncompleteRead as e: # Probably the servers fault
            content = e.partial # Let's hope it's not encoded
            logger.debug("We've got an IncompleteRead, partial content of length %d", len(content))
        except:
            # TODO: Retry in some cases..
            logger.exception("Can't retrieve request %s", url)
        finally:
            try:
                response.close()
            except:
                pass
        
        logger.debug("Content from %s has charset %s", url, content_type)
        # For now we use the utf-8 encoded python strings
#         try:
#             content = content.decode(content_type)
#         except:
#             logger.exception("Decoding failed")
            
        return content