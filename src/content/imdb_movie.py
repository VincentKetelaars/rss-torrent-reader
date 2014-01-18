'''
Created on Dec 31, 2013

@author: Vincent Ketelaars
'''
import re
from src.constants.constants import SERIES_TYPES, MOVIE_TYPES

from src.logger import get_logger
logger = get_logger(__name__)

class IMDBMovie(object):
    '''
    IMDB Movie description
    
    const,created,modified,description,Title,Title type,Directors,You rated,IMDb Rating,
    Runtime (mins),Year,Genres,Num. Votes,Release Date(month/day/year),URL
    '''

    def __init__(self, line, id_, created, modified, desc, title, type_, directors, rate, 
                 rating, runtime, year, genres, votes, release, url, download=True, 
                 latest_season=0, latest_episode=0):
        self.line = line.strip() # No new line characters here..
        self.id = id_
        self.created = created
        self.modified = modified
        self.desc = desc
        self.title = title
        self.type = type_
        self.directors = directors
        self.rate = rate
        self.rating = rating
        self.runtime = runtime # min
        self.year = year
        self.genres = genres
        self.votes = votes
        self.release = release
        self.url = url
        self.download = download
        self.latest_season = latest_season
        self.latest_episode = latest_episode

    def is_series(self):
        return self.type in SERIES_TYPES
    
    def is_movie(self):
        return self.type in MOVIE_TYPES
    
    def should_download(self, season=0, episode=0):
        if self.is_movie():
            return self.download
        if self.is_series():
            return season > self.latest_season or season == self.latest_season and episode > self.latest_episode
        logger.debug("Dealing with unknown film of type %s", self.type)
        return False
    
    def merge(self, movie):
        if movie is None:
            return
        self.download = movie.download
        self.latest_season = movie.latest_season
        self.latest_episode = movie.latest_episode
        # Anything else that where the old value might be useful?
        
    def to_line(self):
        # Only the part before the comma needs to be changed (every value is between quotes)
        r = ""
        if self.is_movie():
            r = "1" if self.download else "0"
        elif self.is_series():
            r = str(self.latest_season) + "-" + str(self.latest_episode)
        line = re.sub('"[\w-]*"', '"' + r + '"', self.line, count=1)
        return line
    
    def __eq__(self, other):
        if not isinstance(other, IMDBMovie):
            return False
        return self.url == other.url
    
    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return self.url.__hash__()