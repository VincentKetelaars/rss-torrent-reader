'''
Created on Dec 25, 2013

@author: Vincent Ketelaars
'''
import locale
import dateutil
from datetime import datetime
from threading import Lock
from sets import Set

from src.http.request import Request
from src.general.get_parse import GetParse

from src.logger import get_logger
from src.content.imdb_movie import IMDBMovie
logger = get_logger(__name__)

class IMDB(object):
    '''
    classdocs
    '''
    
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
            def to_int(arg):
                try:
                    return int(arg.strip())
                except:
                    return -1
            
            created_format = "%a %b %d %H:%M:%S %Y"
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8") # FIXME: Not windows compatible
    
            lines = content.split("\n")
            movies = []
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
                    
                    movies.append(IMDBMovie(args[1], created, modified, args[4], args[5], args[6], directors,
                                            rated, rating, runtime, year, genres, numvotes, release_date, args[15]))
                except:
                    logger.exception("Tried parsing %s", line)
            return movies
            
        def get(self, csv):
            if csv.protected():
                request = Request(csv.url, username=csv.username, password=csv.password)
            else:
                request = Request(input.url)
            return request.imdb_csv_request()

    def __init__(self, csvs, event):
        self.event = event
        self.threads = [self.MovieParser(c, self.result_callback, self.error_callback) for c in csvs]
        for t in self.threads:
            t.start()
        self.returned = 0
        self.results = []
        self.lock = Lock()
        
    def result_callback(self, result):
        with self.lock:
            if result is not None:
                self.results.append(result)
            self.returned += 1
            if self.ready():
                self.event.set()

    def error_callback(self, c):
        pass
    
    def ready(self):
        return len(self.threads) == self.returned
    
    def movies(self):
        return Set([m for s in self.results for m in s])