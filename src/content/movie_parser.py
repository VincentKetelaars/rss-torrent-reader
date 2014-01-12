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
        logger.info("MovieParser starts parsing")
        
        def to_int(arg):
            try:
                return int(arg.strip())
            except:
                return -1
            
        def first_arg(arg):
            i = to_int(arg)
            if i == -1: # Assume denoting season-episode
                try:
                    se = arg.split("-")
                    s = to_int(se[0])
                    e = to_int(se[1])
                    return (s, e)
                except:
                    logger.debug("Don't know what this is then: %s", arg)
            else:
                return i
                
        
        created_format = "%a %b %d %H:%M:%S %Y"
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8") # FIXME: Not windows compatible

        lines = content.split("\n")
        movies = {}
        for line in lines[1:]: # First is column names
            args = line.split('"')[1::2] # Get only the first of every pair
            if len(args) != 16:
                break
            try:
                created = datetime.strptime(args[2], created_format)
                modified = datetime.strptime(args[3], created_format)
                directors = [g.strip() for g in args[12].split(",")]            
                rated = to_int(args[8])
                rating = to_int(args[9])
                runtime = to_int(args[10])
                year = to_int(args[11])
                genres = [g.strip() for g in args[12].split(",")]
                numvotes = to_int(args[13])
                release_date = datetime.min
                try:
                    release_date = datetime.strptime(args[14], "%Y-%m-%d")
                except:
                    try:
                        release_date = dateutil.parser.parse(args[14])
                    except:
                        pass
                finally:                
                    if release_date == datetime.min and year != -1:
                        release_date = datetime(year, 1, 1)
                        
                m = IMDBMovie(line, args[1], created, modified, args[4], args[5], args[6], directors,
                              rated, rating, runtime, year, genres, numvotes, release_date, args[15])
                f = first_arg(args[0])
                try:
                    m.latest_season = f[0]
                    m.latest_episode = f[1]
                except:
                    if f == 0 or f== 1:
                        m.download = f

                movies[args[1]] = m
            except:
                logger.exception("Tried parsing %s", line)
        return movies
        
    def get(self, csv):
        logger.info("IMDB CSV: %s", csv.url)
        if csv.protected():
            request = Request(csv.url, username=csv.username, password=csv.password)
        else:
            request = Request(csv.url)
        return request.imdb_csv_request()