'''
Created on Dec 24, 2013

@author: Vincent Ketelaars
'''
import ConfigParser
import os

from src.content.imdb_csv import IMDBCsv
from src.logger import get_logger
from src.general.constants import DEFAULT_MOVIES_CSV, DEFAULT_SERIES_CSV,\
    DEFAULT_MAX_MOVIES, DEFAULT_MAX_SERIES, PREFERENCE_TITLE_NOT,\
    PREFERENCE_TITLE_ALLOWED, PREFERENCE_TITLE_PREF, PREFERENCE_MIN_WIDTH,\
    PREFERENCE_MIN_HEIGHT, PREFERENCE_MIN_MOVIE_SIZE, PREFERENCE_MAX_MOVIE_SIZE,\
    PREFERENCE_LANGUAGES, PREFERENCE_SUBTITLES, DEFAULT_MISSED_CSV,\
    CONF_DEFAULT_FILE, PREFERENCE_DESC_NOT, PREFERENCE_EXCLUDED_EXTENSIONS,\
    PREFERENCE_MIN_SERIES_SIZE, PREFERENCE_MAX_SERIES_SIZE
from src.torrent.preference import Preference
from src.rss.active_search_params import ActiveSearchParameters
from ConfigParser import NoSectionError
logger = get_logger(__name__)

class Configuration(object):
    '''
    Read and hold configuration from file
    '''

    def __init__(self, file_):
        self.config = ConfigParser.ConfigParser()
        self.config.read([file_])
        self.file = file_
        
    def get_torrent_rss_feeds(self):
        return [l[0] for l in self._get_list("torrents", ["feed"], 0)]
    
    def get_imdb_csv_urls(self):
        return [IMDBCsv(*l) for l in self._get_list("imdb", ["url", "user", "pass"], 0)]
    
    def get_webgui_params(self):
        return self._get_all_options_as_dictionary("webgui")
    
    def get_imdb_paths(self):
        m = self._get_option("storage", "movies_file", default=DEFAULT_MOVIES_CSV)
        s = self._get_option("storage", "series_file", default=DEFAULT_SERIES_CSV)
        miss = self._get_option("storage", "missed_file", default=DEFAULT_MISSED_CSV)        
        return (m, s, miss)
    
    def get_torrent_preference(self):
        not_list = self._get_option("match", "title_not", default=PREFERENCE_TITLE_NOT, is_list=True)
        allowed_list = self._get_option("match", "title_allowed", default=PREFERENCE_TITLE_ALLOWED, is_list=True)
        pref_list = self._get_option("match", "title_pref", default=PREFERENCE_TITLE_PREF, is_list=True)
        not_in_desc = self._get_option("match", "not_in_desc", default=PREFERENCE_DESC_NOT, is_list=True)
        width = self._get_option("match", "min_width", default=PREFERENCE_MIN_WIDTH)
        height = self._get_option("match", "min_height", default=PREFERENCE_MIN_HEIGHT)
        min_movie_size = self._get_option("match", "min_movie_size", default=PREFERENCE_MIN_MOVIE_SIZE)
        max_movie_size = self._get_option("match", "max_movie_size", default=PREFERENCE_MAX_MOVIE_SIZE)
        min_series_size = self._get_option("match", "min_series_size", default=PREFERENCE_MIN_SERIES_SIZE)
        max_series_size = self._get_option("match", "max_series_size", default=PREFERENCE_MAX_SERIES_SIZE)
        languages = self._get_option("match", "languages", PREFERENCE_LANGUAGES, is_list=True)
        subtitles = self._get_option("match", "subtitles", PREFERENCE_SUBTITLES, is_list=True)
        excluded_extensions = self._get_option("match", "excluded_extensions", default=PREFERENCE_EXCLUDED_EXTENSIONS, is_list=True)
        return Preference(not_list, allowed_list, pref_list, not_in_desc, width, height, min_movie_size, max_movie_size, min_series_size, max_series_size, languages, subtitles, excluded_extensions)
    
    def get_handler(self, handler):
        return self._get_all_options_as_dictionary("handler_" + handler.lower())
    
    def get_handlers(self):
        return (self._get_option("handlers", "primary", default=[], is_list=True),
                self._get_option("handlers", "secondary", default=[], is_list=True))
        
    def get_active_feeds(self):
        feeds = [l[0] for l in self._get_list("active", ["active_url"], 0)]
        max_movies = self._get_option("active", "max_movies", DEFAULT_MAX_MOVIES)
        max_series = self._get_option("active", "max_series", DEFAULT_MAX_SERIES)
        return ActiveSearchParameters(feeds, max_movies, max_series)
    
    def _get_list(self, section, options, start=0):
        l = []
        i = start
        while True:
            t = []
            for o in options:
                v = self._get_option(section, o +  str(i))
                if v is not None:
                    t.append(v)
                else:
                    break
            if not t: # t == []
                break
            l.append(t)
            i+=1
        return l
    
    def _get_all_options_as_dictionary(self, section):
        d = {}
        try:
            l = self.config.items(section)
        except NoSectionError:
            logger.debug("Can't get section %s", section)
            return d
        for i in l:
            d[i[0]] = self._parse_option(i[1])
        return d
    
    def _parse_option(self, option, is_list=False):
        if option.find(",") > -1 and not (option.startswith('"') or option.endswith('"')):
            is_list = True
        result = option.strip(' ').strip('"')
        if result.lower() == "false":
            return False
        if result.lower() == "true":
            return True
        if len(result) == 0:
            if is_list:
                return []
            return None
        if is_list:
            temp = []
            for r in result.split(","):
                x = r.strip().strip('"')
                if len(x) == 0:
                    continue
                try:
                    x = int(x)
                except ValueError:
                    pass
                temp.append(x)
            result = temp
        else:
            try:
                result = int(result)
            except ValueError:
                pass
        return result
    
    def _get_option(self, section, option, default=None, is_list=False):
        try:
            return self._parse_option(self.config.get(section, option), is_list)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            logger.debug("We do not have this option %s in section %s", option, section)
        return default
    
    def _set_option(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        
    def set_option(self, section, option, value):
        if value is not None:
            self._set_option(section, option, str(value))
            
    def add_to_list(self, section, option, value):
        options = self._get_option(section, option, default=[], is_list=True)
        if not str(value) in options:
            options.append(str(value))
        self.config.set(section, option, ",".join(options))
        
    def write(self):
        try:
            with open(self.file, "w+") as f:
                self.config.write(f)
        except IOError:
            return False
        return True
    
def get_location_from_text_file(filename):
    location = ""
    try:
        with open(filename, "r") as f:
            location = f.read().strip()
    except IOError:
        pass
    if os.path.isfile(location):
        return location
    return CONF_DEFAULT_FILE