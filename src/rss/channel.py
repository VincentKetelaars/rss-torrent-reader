'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''
import re

from src.logger import get_logger
from src.general.constants import RESOLUTION_720, RESOLUTION_1080,\
    RESOLUTION_HDTV, RESOLUTION_BRRIP, RESOLUTION_ZERO, RESOLUTION_DVDRIP
from src.general.functions import string_to_size
logger = get_logger(__name__)

class Channel(object):
    
    def __init__(self, title, description, link):
        self.title = title
        self.description = description
        self.link = link
        self.items = []
        
    def add_item(self, item):
        self.items.append(item)
        
    def __repr__(self):
        return "<Channel[%s]>" % (self.title,)
        
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
        self._resolution = RESOLUTION_ZERO
        self._episode = (0, 0)
        self._size = self.get_size()
        self._film_title = None
        self._film_year = 0
        self._parse_title() # Determines resolution by claim
        self._parse_description() # Determines resolution by actual numbers
        logger.debug("%s %s %d %s %s", self.title, self.inclusive_title(), self._film_year, self._resolution, self._size)        
    
    def url(self):
        return self.enclosure.get("url", None)
    
    def filename(self):
        f = self.torrent.get("fileName") if self.torrent is not None else None
        if f is None or f.find("%") > 0: # Percentage signs indicate malformed titles
            f = self.title 
            try:
                u = f.decode("utf-8")
                f = u.encode("ascii", "ignore")
            except:
                logger.exception("Could not convert %s from utf8 to ascii", self.title)
            f += ".torrent"
        return f
    
    def get_size(self):
        s = self.torrent.get("contentLength") if self.torrent is not None else None
        if s is None:
            s = self.enclosure.get("length")
        return int(s) if s is not None else 0
    
    def size(self):
        return self._size
    
    def film_title(self):
        return self._film_title if self._film_title is not None else self.title.replace(".", " ")
    
    def inclusive_title(self):
        """
        Return title + episode (if series)
        """
        return self.film_title() + (" S%02dE%02d" % self.episode() if self.is_series() else "")
    
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
        series = re.search("\s((S(\d{2})\-?)+(E(\d{2}\-?)+)*|(\d{1,2})x(\d{2})|season\s(\d+\-)?((\d{1,2}),?)+)(\s|$)", ndtitle, re.IGNORECASE)
        movies = re.search("\s?(\*?{?\[?\(?(\d{4})\)?\]?}?|720p|1080p|HDTV|dvd(rip)?|brrip)\s?", ndtitle[3:], re.IGNORECASE)
        if series:
            self._series = True
            index = ndtitle.find(series.group(1).strip())
            self._film_title = ndtitle[0:index].strip()
            season = 0
            if series.group(3) is not None:
                season = int(series.group(3))
            elif series.group(6) is not None:
                season = int(series.group(6))
            elif series.group(10) is not None:
                season = int(series.group(10))
            episode = 0
            if series.group(5) is not None: 
                episode = int(series.group(5))
            elif series.group(7) is not None:
                episode = int(series.group(7))
            # If episode is still 0, and the season is larger than 0, we are dealing with an entire season
            # We increment the season to show that we download the entire season
            if episode == 0 and season > 0:
                season += 1
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
        description = self.description.replace(self.title, "") # Any repeats of the torrent shouldn't cloud the parsing
        self._update_resolution(description)
        self._update_size(description)
                    
    def _update_resolution(self, text):
        resolutions = re.findall("(\d{3,4})[x*](\d{3,4})", text, re.IGNORECASE)
        resolution = RESOLUTION_ZERO
        for r in resolutions:
            width = int(r[0])
            height = int(r[1])
            # Some descriptions might have values that look like actual resolutions but aren't. So compare them to 16:9 screen
            if resolution == RESOLUTION_ZERO or abs(16 / 9 - width / height) < abs(16 / 9 - resolution[0] / resolution[1]):
                resolution = (width, height)
        if resolution != RESOLUTION_ZERO:
            self._resolution = resolution
        if self._resolution == RESOLUTION_ZERO:
            resolution = re.findall("(720p|1080p|HDTV|B[RD]RIP|BLURAY|dvd(rip)?)", text, re.IGNORECASE)        
            for r in resolution: # Could be multiple indicators in the string
                v = self._get_resolution_from_string(r[0])
                # Let's trust the torrent with the highest indicator winning
                if v != RESOLUTION_ZERO and (v > self._resolution or self._resolution == RESOLUTION_ZERO):
                    self._resolution = v
            
    def _get_resolution_from_string(self, s):
        if s.lower() == "720p":
            return RESOLUTION_720
        elif s.lower() == "1080p":
            return RESOLUTION_1080
        elif s.upper() =="HDTV":
            return RESOLUTION_HDTV
        elif s.upper() == "BRRIP" or s.upper() == "BDRIP" or s.upper() == "BLURAY":
            return RESOLUTION_BRRIP
        elif s.upper() == "DVDRIP" or s.upper() == "DVD":
            return RESOLUTION_DVDRIP
        else:
            return RESOLUTION_ZERO
        
    def _update_size(self, s):
        size_parse = "\d+\.?\d*\s*[KMGT]B"
        match = re.search(size_parse, s, re.IGNORECASE)
        if match:
            if self._size <= 50000: # Movies / Series are bigger than this, so any value below this is either in KB or bullshit
                self._size = string_to_size(match.group(0))
            
    def __str__(self):
        return self.title