'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''
import tempfile
import zlib
import re
# import ImageEnhance
from urllib2 import HTTPHandler, HTTPSHandler, HTTPErrorProcessor, HTTPRedirectHandler, HTTPCookieProcessor, build_opener
from urllib import urlencode
from cookielib import CookieJar
from collections import OrderedDict
from httplib import IncompleteRead

from src.content import captcha
from src.logger import get_logger
from src.general.constants import TESSERACT_ON
logger = get_logger(__name__)

IMDBLOGIN = "https://secure.imdb.com/register/login?ref_=nv_usr_lgin_3"
PRECAPTCHA = "http://pro.imdb.com"

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
        
        
        def login(form, opener):
            content = None
            try:
                params = urlencode(form)
                response = opener.open(IMDBLOGIN, params)
                if response.getcode() != 200:
                    logger.warning("Did not receive proper response from IMDB %s, code %s", IMDBLOGIN, response.getcode())
                content = response.read()
            except:
                logger.exception("Can't retrieve %s", IMDBLOGIN)
            finally:
                try: # response, or response2 might not exist
                    response.close()
                except:
                    pass
            return content

        form = OrderedDict([("49e6c", "378"), ("login", self.username), ("password",  self.password)])
        
        cj = CookieJar()
        opener = build_opener(HTTPHandler(), HTTPSHandler(), HTTPErrorProcessor(), 
                     HTTPRedirectHandler(), HTTPCookieProcessor(cj))
        login_response = login(form, opener)
        
        if login_response is None:
            return None
        match = re.search('src="(/widget/captcha\?type=stranger&c=\w+)"', login_response)
        if match: # We have a captcha to deal with
            captcha_link = PRECAPTCHA + match.group(1)
            logger.warning("IMDB doesn't trust us, hence the %s link", captcha_link)
            if not TESSERACT_ON:
                return None
            directory = tempfile.gettempdir()
            try:                 
                pic = self._request(self._create_opener(), captcha_link)
                captcha_string = captcha.convert_captcha_to_string(pic, directory)
                logger.debug("Captcha reads %s", captcha_string)
                form["captcha_answer"] = captcha_string
                if login(form, opener).find("Enter the name of the movie or person above: ") < 0:
                    logger.info("Login with captcha worked!")
                else:
                    logger.debug("Failed to login with Captcha")
                    return None
            except:
                logger.exception("No captcha for us")
                return None
                    
        content = self._request(opener, self.url)
            
        if content is not None:
            logger.info("Request for %s returns content of length %d", self.url, len(content))
        return content
    
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