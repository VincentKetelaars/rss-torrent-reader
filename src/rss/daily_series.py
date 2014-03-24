'''
Created on Mar 24, 2014

@author: Vincent Ketelaars
'''
import json
from threading import Thread, Event

from src.logger import get_logger
from src.http.request import Request
from src.content.movie import Movie
from src.general.constants import DAILY_WAIT
logger = get_logger(__name__)

class DailySeries(Thread):
    '''
    Retrieve the series that aired today.
    '''

    def __init__(self):
        Thread.__init__(self, name="DailySeries")
        self.results = []
        self.event = Event()
        
    def run(self):
        content = Request("http://www.kimonolabs.com/api/5zuphis2?apikey=a9ac702e3760e13f1a580055c168d838").request()
        if content is not None:
            self.results = json.loads(content)
        self.event.set()
        
    def serie_to_content(self, serie):
        return (serie["Name"]["text"], int(serie["Season"]["text"]), int(serie["Episode"]["text"]))
        
    def series(self):
        series = self.results["results"]["Series"]
        return [Movie(*self.serie_to_content(serie)) for serie in series]
    
    def wait(self, timeout=DAILY_WAIT):
        self.event.wait(timeout)
    
    