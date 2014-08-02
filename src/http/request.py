'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''
from httplib import IncompleteRead
from urllib2 import HTTPHandler, HTTPSHandler, HTTPErrorProcessor, HTTPRedirectHandler, build_opener
import zlib

from src.logger import get_logger
logger = get_logger(__name__)

class Request(object):
    '''
    This class takes a string that represents a URL and obtains the content
    '''

    def __init__(self, url):
        self.url = url
    
    def _create_opener(self):
        opener = build_opener(HTTPHandler(), HTTPErrorProcessor(), HTTPRedirectHandler(), HTTPSHandler())
        opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Spoof User agent
        return opener
    
    def request(self):
        return self._request(self._create_opener(), self.url)
    
    def _request(self, opener, url):
        content = None
        charset = None
        try:
            response = opener.open(url)
            if response.getcode() == 200:
                content = response.read()
                try:
                    content_type = response.info().get("Content-Type")
                    if content_type.find("charset"):
                        charset = content_type.split('charset=')[-1].strip()
                except:
                    logger.exception("Can't obtain charset, resorting to default")
                encoding = response.info().get("Content-Encoding")
                if encoding is not None and content is not None and len(content) > 0:
                    if encoding == "gzip":
                        try:
                            content = zlib.decompress(content, 16+zlib.MAX_WBITS)
                        except:
                            logger.exception("Error with content: %s". content)
                    else:
                        logger.warning("Don't know encoding %s", encoding)                        
            if response.getcode() != 200 or content is None:
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
        
        if charset is not None:
            logger.debug("Content from %s has charset %s and size %d", url, charset, len(content))
        # For now we use the utf-8 encoded python strings
#         try:
#             content = content.decode(charset)
#         except:
#             logger.exception("Decoding failed")
            
        return content