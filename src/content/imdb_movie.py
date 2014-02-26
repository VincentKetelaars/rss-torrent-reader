'''
Created on Dec 31, 2013

@author: Vincent Ketelaars
'''
from datetime import datetime, timedelta
from src.general.constants import SERIES_TYPES, MOVIE_TYPES, IMDB_DEFAULT_DATE

from src.logger import get_logger
from src.general.constants import IMDB_TIMESTAMP_FORMAT
import random
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
        
    def inclusive_title(self):
        """
        Return title + episode (if series)
        """
        return self.title + (" %s" % (self.episode_to_string(self.latest_season, self.latest_episode),) if self.is_series() else "")

    def episode_to_string(self, season, episode):
        """
        @param season: integer of at least 1
        @param episode: integer of at least 0
        @return: S{season}E{episode}, unless episode is 0. Then S{season}
        """
        return "S%02dE%02d" % (season, episode) if episode > 0 else "S%02d" % (season,)

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
            return self.download and (season > self.latest_season or (season == self.latest_season and episode > self.latest_episode))
        logger.debug("Dealing with unknown film of type %s", self.type)
        return False
    
    def is_downloaded(self):
        return self.time_downloaded != datetime(*IMDB_DEFAULT_DATE)
    
    def handled(self, season=0, episode=0):
        if not self.download: # Already marked as downloaded
            return False
        if self.is_movie():
            self.download = False
        if self.is_series():
            if season < self.latest_season or (season == self.latest_season and episode <= self.latest_episode):
                return False
            self.set_episode(season, episode)
        self.time_downloaded = datetime.utcnow()
        return True
    
    def merge(self, movie):
        if movie is None:
            return
        self.download = movie.download
        self.latest_season = movie.latest_season
        self.latest_episode = movie.latest_episode
        self.time_downloaded = movie.time_downloaded
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
    
    def predict_next(self):
        """
        Predict next episode
        @return: tuple of season and episode, episode of zero means entire season
        """
        if not self.is_series():
            return
        if self.latest_season == 0: # Initial value
            return (1, 0)
        if self.latest_episode == 0: # First episode of the season
            return (self.latest_season, 1)
        if self.time_downloaded != datetime(*IMDB_DEFAULT_DATE) and self.time_downloaded + timedelta(days=175) < datetime.utcnow(): # Season should be over after half a year
            return (self.latest_season + 1, 1)
        # Within two weeks odds are very high that we're in the same season still
        if self.time_downloaded + timedelta(days=15) > datetime.utcnow(): 
            return (self.latest_season, self.latest_episode + 1)
        if random.random() < 0.25: # Allow chance that we're in the next season
            return (self.latest_season + 1, 0)
        # else
        return (self.latest_season, self.latest_episode + 1) # Default
        
    def search_string(self):
        if self.is_movie():
            return self.title
        elif self.is_series():
            return self.title + " " + self.episode_to_string(*self.predict_next())
        else:
            return self.title
    
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