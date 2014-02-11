'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

from datetime import timedelta

"""
GUI
"""
TITLE_MAIN = "Torrent RSS Reader"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080

"""
CONFIGURATION
"""
CONF_FILE = "/home/vincent/Downloads/conf.cfg"

DEFAULT_MOVIES_CSV = "conf/movies.csv"
DEFAULT_SERIES_CSV = "conf/series.csv"

"""
IMDB
"""
MOVIE_TYPES = ["Feature Film", "Video", "TV Movie"]
SERIES_TYPES = ["TV Series", "Mini-Series"]
IMDB_TIMESTAMP_FORMAT = "%a %b %d %H:%M:%S %Y"
IMDB_DEFAULT_YEAR = 1901
IMDB_DEFAULT_DATE = (IMDB_DEFAULT_YEAR, 1, 1)

"""
PORTABILITY
"""
NEWLINE = "\r\n"

"""
WAIT TIMES
"""
HANDLER_WAIT = 60.0 # Seconds
FEED_WAIT = 60.0 # Seconds
MERGER_WAIT = 60.0 # Seconds
IMDB_WAIT = 60.0 # Seconds

"""
GENERAL CONSTANTS
"""
RESOLUTION_ZERO = (0, 0) # default / unknown
RESOLUTION_720 = (1280, 720)
RESOLUTION_1080 = (1920, 1080)
RESOLUTION_HDTV = (720, 404) # EZTV HDTV Torrent example resolution
RESOLUTION_BRRIP = RESOLUTION_720 # Use this as first measure and hope for more in the description

"""
ACTIVE SEARCH
"""
SEARCH_REPLACE_VALUE = "SEARCH_PARAMETERS"
DEFAULT_MAX_MOVIES = 5
DEFAULT_MAX_SERIES = 5
# The following values are used to determine which series should be searched for
# The SHARE values indicate the share of the maximum number of series that may be searched for 
# that will be used for the corresponding category. First category is from now till CATEGORIES[0] etc.
ACTIVE_SERIES_CATEGORIES = [timedelta(days=7), timedelta(days=30), timedelta(days=365), timedelta(days=36500)]
ACTIVE_SERIES_SHARE = [0, 0.6, 0.2, 0.2]