'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

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

"""
PORTABILITY
"""
NEWLINE = "\r\n"

"""
WAIT TIMES
"""
HANDLER_WAIT = 20.0 # Seconds
FEED_WAIT = 20.0 # Seconds
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