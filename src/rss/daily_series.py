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
        self.results = {}
        self.event = Event()
        
    def run(self):
        content = Request("http://www.kimonolabs.com/api/5zuphis2?apikey=a9ac702e3760e13f1a580055c168d838").request()
        if content is not None:
            self.results = json.loads(content)
        self.event.set()
        
    def serie_to_content(self, serie):
        try:
            return (serie["Name"]["text"], int(serie["Season"]["text"]), int(serie["Episode"]["text"]))
        except ValueError:
            logger.exception("Couldn't parse %s and %s to ints", serie["Season"]["text"], serie["Episode"]["text"])
        return (serie["Name"]["text"], 0, 0)
        
    def series(self):
        if len(self.results.items()) == 0:
            return []
        series_info = []
        try:
            series = self.results["results"]["Series"]
            for serie in series:
                name, season, episode = self.serie_to_content(serie)
                if season > 0:
                    series_info.append(Movie(name, season, episode))
        except:
            logger.exception("Error in handling daily series")
        logger.info("Today %d series have a new episode", len(series_info))
        return series_info
    
    def wait(self, timeout=DAILY_WAIT):
        self.event.wait(timeout)
    
    