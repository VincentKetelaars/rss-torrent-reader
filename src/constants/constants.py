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