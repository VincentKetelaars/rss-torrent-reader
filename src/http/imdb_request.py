'''
Created on Aug 2, 2014

@author: Vincent Ketelaars
'''
import tempfile
import re
from urllib2 import HTTPHandler, HTTPSHandler, HTTPErrorProcessor, HTTPRedirectHandler, HTTPCookieProcessor, build_opener
from urllib import urlencode
from cookielib import CookieJar
from collections import OrderedDict

from src.content import captcha
from src.logger import get_logger
from src.general.constants import TESSERACT_ON
logger = get_logger(__name__)
from src.http.request import Request

IMDBLOGIN = "https://secure.imdb.com/register/login?ref_=nv_usr_lgin_3"
PRECAPTCHA = "http://pro.imdb.com"

class IMDBRequest(Request):
    '''
    classdocs
    '''

    def __init__(self, url, username=None, password=None):
        Request.__init__(self, url)
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
        