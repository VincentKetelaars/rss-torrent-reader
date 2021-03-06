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
CONF_LOCATION_FILE = "conf/conf_location.txt"
CONF_DEFAULT_FILE = "conf/configuration.cfg"

DEFAULT_MOVIES_CSV = "conf/movies.csv"
DEFAULT_SERIES_CSV = "conf/series.csv"
DEFAULT_MISSED_CSV = "conf/missed.csv"

"""
IMDB
"""
MOVIE_TYPES = ["Feature Film", "Video", "TV Movie", "Documentary"]
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
DAILY_WAIT = 30.0 # Seconds
HANDLER_WAIT = 30.0 # Seconds per match
FEED_WAIT = 30.0 # Seconds per url
IMDB_WAIT = 300.0 # Seconds
MERGER_WAIT = IMDB_WAIT

"""
GENERAL CONSTANTS
"""
RESOLUTION_ZERO = (0, 0) # default / unknown
RESOLUTION_720 = (1280, 720)
RESOLUTION_1080 = (1920, 1080)
RESOLUTION_HDTV = (720, 404) # EZTV HDTV Torrent example resolution
RESOLUTION_DVDRIP = (600, 300) # Ranges from 500-700 x 250-400 in a dozen tests
RESOLUTION_BRRIP = RESOLUTION_720 # Use this as first measure and hope for more in the description

"""
TORRENT PREFERENCES
"""
PREFERENCE_TITLE_NOT = ["R5","R6","dvdscr","cam","ts"]
PREFERENCE_TITLE_ALLOWED = ["extended","theatrical","edition","extra","complete","unrated"]
PREFERENCE_TITLE_PREF = []
PREFERENCE_DESC_NOT = ["hardcoded"]
PREFERENCE_MIN_WIDTH = 0
PREFERENCE_MIN_HEIGHT = 0
PREFERENCE_MIN_MOVIE_SIZE = "0MB"
PREFERENCE_MAX_MOVIE_SIZE = "20GB"
PREFERENCE_LANGUAGES=["eng"]
PREFERENCE_SUBTITLES=["eng"]
PREFERENCE_EXCLUDED_EXTENSIONS=["m4v"]

"""
ACTIVE SEARCH
"""
SEARCH_REPLACE_VALUE = "SEARCH_PARAMETERS"
DEFAULT_MAX_MOVIES = 5
DEFAULT_MAX_SERIES = 5
# The following values are used to determine which series should be searched for
# The SHARE values indicate the share of the maximum number of series that may be searched for 
# that will be used for the corresponding category. First category is from now till CATEGORIES[0] etc.
ACTIVE_SERIES_CATEGORIES = [timedelta(days=6), timedelta(days=8), timedelta(days=30), timedelta(days=365), timedelta(days=73000)]
ACTIVE_SERIES_SHARE = [0, 0.2, 0.4, 0.2, 0.2]

"""
DOWNLOAD CHOICES
"""
DOWNLOAD_SEASON_TORRENTS = True # Note that you risk downloading torrents that do not have all episode of the season

"""
TESSERACT
"""
TESSERACT_ON = True # Only set to true if you want to use it (Make sure it is installed)
TESSERACT_FULL_PATH = "/usr/local/bin/tesseract" # Full path to tesseract
TESSERACT_CONFIG_FILE = "letters" # Config file setup as mentioned here: http://stackoverflow.com/a/2983295/1444854