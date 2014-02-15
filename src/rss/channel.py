'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''
import re

from src.logger import get_logger
from src.general.constants import RESOLUTION_720, RESOLUTION_1080,\
    RESOLUTION_HDTV, RESOLUTION_BRRIP, RESOLUTION_ZERO
logger = get_logger(__name__)

class Channel(object):
    
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
class Item(object):

    def __init__(self, item, title, description, category, author, link, guid, pubdate, enclosure, torrent):
        self.item = item
        self.title = title
        self.description = description
        self.category = category
        self.author = author
        self.link = link
        self.guid = guid
        self.pubdate = pubdate
        self.enclosure = enclosure # dictionary 
        self.torrent = torrent # Torrent
        
        self._series = False
        self._resolution = (0, 0)
        self._episode = (0, 0)
        self._film_title = None
        self._film_year = 0
        self._parse_title() # Determines resolution by claim
        self._parse_description() # Determines resolution by actual numbers
        logger.debug("%s %s %d %s %s %s", self.title, self._film_title, self._film_year, self._series, self._episode, self._resolution)        
    
    def url(self):
        return self.enclosure.get("url", None)
    
    def filename(self):
        f = self.torrent.get("fileName")
        if f is None:
            f = self.title + ".torrent"
        return f
    
    def film_title(self):
        return self._film_title if self._film_title is not None else self.title.replace(".", " ")
    
    def is_series(self):
        return self._series
    
    def is_movie(self):
        return not self._series
    
    @property
    def film_year(self):
        return self._film_year
        
    def episode(self):
        """
        @return: (season, episode) or (0, 0)
        """
        return self._episode
        
    def resolution(self):
        """
        Parse description for resolution and return (width, height)
        """                    
        return self._resolution
    
    def _parse_title(self):
        """
        Common title structures:
        MOVIES:
        Title Year Resolution ...
        SERIES:
        Title Episode Episode_title Resolution ....
        """
        ndtitle = self.title.replace(".", " ")
        series = re.search("\s(S(\d{2})(E\d{2})*|(\d{1,2})(x\d{2})|season\s(\d+\-)?(\d{1,2}))(\s|$)", ndtitle, re.IGNORECASE)
        movies = re.search("\s(\[?\(?(\d{4})\)?\]?|720p|1080p|HDTV)\s?", ndtitle)
        if series:
            self._series = True
            index = ndtitle.find(series.group(1).strip())
            self._film_title = ndtitle[0:index].strip()
            # If it is only season, we set the episode to 0, because you can't know how much of the season is in there
            season = 0
            if series.group(2) is not None:
                season = int(series.group(2))
            elif series.group(4) is not None:
                season = int(series.group(4))
            elif series.group(7) is not None:
                season = int(series.group(7))
            episode = 0
            if series.group(3) is not None: 
                episode = int(series.group(3)[1:])
            elif series.group(5) is not None:
                episode = int(series.group(5)[1:])
            self._episode = (season, episode)
        elif movies:
            self._series = False
            self._film_title = ndtitle[0:ndtitle.find(movies.group(1).strip())].strip()
            if len(self._film_title) < 3:
                pass # TODO: Try again?            
            if movies.group(2):
                self._film_year = int(movies.group(2))
        else:
            logger.warning("Can't parse this title: %s", self.title)
        if self._film_title is not None:
            torrent = re.search("\[?torrent\]?", self._film_title, re.IGNORECASE)
            if torrent:
                self._film_title = self._film_title.replace(torrent.group(0), "").strip()
        self._update_resolution(self.title)
        
    def _parse_description(self):
        self._update_resolution(self.description)
                    
    def _update_resolution(self, text):
        resolution = re.search("(\d{3,4})[x*](\d{3,4})", text, re.IGNORECASE)
        if resolution:
            self._resolution = (int(resolution.group(1)), int(resolution.group(2)))
        else:
            resolution = re.findall("(720p|1080p|HDTV|BRRIP)", text, re.IGNORECASE)        
            for r in resolution: # Could be multiple indicators in the string
                v = self._get_resolution_from_string(r)
                # Lower value is probably a better inidicator of actual value
                if v != RESOLUTION_ZERO and (v < self._resolution or self._resolution == RESOLUTION_ZERO):
                    self._resolution = v
            
    def _get_resolution_from_string(self, s):
        if s.lower() == "720p":
            return RESOLUTION_720
        elif s.lower() == "1080p":
            return RESOLUTION_1080
        elif s.upper() =="HDTV":
            return RESOLUTION_HDTV
        elif s.upper() == "BRRIP":
            return RESOLUTION_BRRIP
        else:
            return RESOLUTION_ZERO
            
    def __str__(self):
        return self.title