'''
Created on Dec 31, 2013

@author: Vincent Ketelaars
'''
from datetime import datetime
from src.general.constants import SERIES_TYPES, MOVIE_TYPES, IMDB_DEFAULT_DATE

from src.logger import get_logger
from src.general.constants import IMDB_TIMESTAMP_FORMAT
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
        self.time_downloaded = datetime(*IMDB_DEFAULT_DATE)

    def is_series(self):
        return self.type in SERIES_TYPES
    
    def is_movie(self):
        return self.type in MOVIE_TYPES
    
    def set_episode(self, season, episode):
        self.latest_season = season
        self.latest_episode = episode
    
    def should_download(self, season=0, episode=0):
        if self.is_movie():
            return self.download
        if self.is_series():
            return self.download and season > self.latest_season or (season == self.latest_season and episode > self.latest_episode)
        logger.debug("Dealing with unknown film of type %s", self.type)
        return False
    
    def is_downloaded(self):
        return self.time_downloaded != IMDB_DEFAULT_DATE
    
    def handled(self, season=0, episode=0):
        if not self.download: # Already marked as downloaded
            return
            self.download = False
        if self.is_series():
            if season < self.latest_season or (season == self.latest_season and episode <= self.latest_episode):
                return
            self.set_episode(season, episode)
        self.time_downloaded = datetime.utcnow()
    
    def merge(self, movie):
        if movie is None:
            return
        self.download = movie.download
        self.latest_season = movie.latest_season
        self.latest_episode = movie.latest_episode
        # Anything else that where the old value might be useful?
        
    def to_line(self):
        """
        The original line from imdb is slightly changed:
        The line is extended by a timestamp indicating the last time it was downloaded
        The first value is changed such that for movies it is either 0 or 1 indicating whether it should be downloaded
        For series it is extended by the latest season and episode value that we're at (previously downloaded)
        Movies = 0|1
        Series = (0|1)-season-episode
        """        
        def quoted(text):
            return '"' + str(text) + '"'
        
        def commalist(l):
            return ",".join([quoted(i) for i in l])
        
        # Only the part before the comma needs to be changed (every value is between quotes)
        r = "1" if self.download else "0"
        if self.is_series():
            r += "-" + str(self.latest_season) + "-" + str(self.latest_episode)
        line = commalist([r, self.id, self.created.strftime(IMDB_TIMESTAMP_FORMAT), self.modified.strftime(IMDB_TIMESTAMP_FORMAT), 
                         self.desc, self.title, self.type, ", ".join(self.directors), self.rate, self.rating, self.runtime, 
                         self.year, ", ".join(self.genres), self.votes, self.release.strftime("%Y-%m-%d"), 
                         self.url, self.time_downloaded.strftime(IMDB_TIMESTAMP_FORMAT)])
        return line
    
    def __str__(self):
        return "%s %s %s %d %s %d %d" % (self.id, self.title, self.url, self.year, self.download,
                self.latest_season, self.latest_episode)
    
    def __eq__(self, other):
        if not isinstance(other, IMDBMovie):
            return False
        return self.id == other.id
    
    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return self.id.__hash__()