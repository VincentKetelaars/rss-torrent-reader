'''
Created on Jan 11, 2014

@author: Vincent Ketelaars
'''
import locale
import dateutil
from datetime import datetime

from src.general.get_parse import GetParse
from src.content.imdb_movie import IMDBMovie
from src.http.request import Request

from src.logger import get_logger
from src.general.constants import IMDB_TIMESTAMP_FORMAT, IMDB_DEFAULT_YEAR,\
    IMDB_DEFAULT_DATE
logger = get_logger(__name__)

class MovieParser(GetParse):
    
    def parse(self, content):
        """
        Parse CSV watchlist file
        position,const,created,modified,description,Title,Title type,Directors,You rated,IMDb Rating,
        Runtime (mins),Year,Genres,Num. Votes,Release Date(month/day/year),URL
        
        created/modified: DDD MMM dd hh:mm:ss YYYY
        release date: yyyy-mm-dd
        
        Each line has komma separated values, but genres can have komma's as well.
        Each value should be encapsulated by quotes.
        """
        if content is None:
            logger.debug("Getting nothing")
            return None
        logger.info("MovieParser starts parsing content of length %d", len(content))
        
        def to_float(arg):
            try:
                return float(arg.strip())
            except ValueError:
                return -1.0
            
        def to_int(arg):
            try:
                return int(arg.strip())
            except ValueError:
                return -1
            
        def first_arg(arg):
            i = to_int(arg)
            if i == -1: # Assume denoting season-episode
                try:
                    return [to_int(a) for a in arg.split("-")]
                except TypeError:
                    logger.debug("Don't know what this is then: %s", arg)
            else:
                return i
                
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8") # FIXME: Not windows compatible

        lines = content.split("\n")
        movies = {}
        for line in lines:
            args = line.split('"')[1::2] # Get only the first of every pair
            if len(args) < 16 or args[0] == "position": # First line of watchlist
                continue
            try:
                created = datetime.strptime(args[2], IMDB_TIMESTAMP_FORMAT)
                modified = datetime.strptime(args[3], IMDB_TIMESTAMP_FORMAT)
                directors = [g.strip() for g in args[12].split(",")]            
                rated = to_float(args[8])
                rating = to_float(args[9])
                runtime = to_int(args[10])
                year = to_int(args[11])
                if year < IMDB_DEFAULT_YEAR: year = IMDB_DEFAULT_YEAR
                genres = [g.strip() for g in args[12].split(",")]
                numvotes = to_int(args[13])
                release_date = datetime(*IMDB_DEFAULT_DATE)
                try:
                    release_date = datetime.strptime(args[14], "%Y-%m-%d")
                except:
                    try:
                        release_date = dateutil.parser.parse(args[14])
                    except:
                        pass
                        
                m = IMDBMovie(line, args[1], created, modified, args[4], args[5], args[6], directors,
                              rated, rating, runtime, year, genres, numvotes, release_date, args[15])
                f = first_arg(args[0])
                try:
                    if len(f) == 2: # season - episode: Should be fased out
                        m.latest_season = f[0]
                        m.latest_episode = f[1]
                    elif len(f) == 3:
                        m.download = f
                        m.latest_season = f[1]
                        m.latest_episode = f[2]
                except TypeError:
                    # Either 0 or 1 indicating download or positive number for index (from imdb.com)
                    m.download = f # Only False when 0, which means True by default
                if len(args) == 17:
                    m.time_downloaded = datetime.strptime(args[16], IMDB_TIMESTAMP_FORMAT)
                    
                movies[args[1]] = m
            except:
                logger.exception("Tried parsing %s", line)
        logger.debug("Returning %d movies", len(movies))
        return movies
        
    def get(self, csv):
        logger.info("IMDB CSV: %s", csv.url)
        if csv.protected():
            request = Request(csv.url, username=csv.username, password=csv.password)
        else:
            request = Request(csv.url)
        return request.imdb_csv_request()