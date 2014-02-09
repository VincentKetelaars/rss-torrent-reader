'''
Created on Dec 24, 2013

@author: Vincent Ketelaars
'''
import ConfigParser

from src.content.imdb_csv import IMDBCsv
from src.logger import get_logger
from src.general.constants import DEFAULT_MOVIES_CSV, DEFAULT_SERIES_CSV,\
    DEFAULT_MAX_MOVIES, DEFAULT_MAX_SERIES
from src.torrent.preference import Preference
from src.rss.active_search_params import ActiveSearchParameters
logger = get_logger(__name__)

class Configuration(object):
    '''
    Read and hold configuration from file
    '''

    def __init__(self, file_):
        self.config = ConfigParser.ConfigParser()
        self.config.read([file_])
        
    def get_torrent_rss_feeds(self):
        return [l[0] for l in self._get_list("torrents", ["feed"], 0)]
    
    def get_imdb_csv_urls(self):
        return [IMDBCsv(*l) for l in self._get_list("imdb", ["url", "user", "pass"], 0)]
    
    def get_webgui_params(self):
        return self._get_all_options_as_dictionary("webgui")
    
    def get_imdb_paths(self):
        m = self._get_option("storage", "movies_file", default=DEFAULT_MOVIES_CSV)
        s = self._get_option("storage", "series_file", default=DEFAULT_SERIES_CSV)        
        return (m, s)
    
    def get_torrent_preference(self):
        not_list = self._get_option("match", "title_not", default=[], is_list=True)
        allowed_list = self._get_option("match", "title_allowed", default=[], is_list=True)
        pref_list = self._get_option("match", "title_pref", default=[], is_list=True)
        width = self._get_option("match", "min_width", default=0)
        height = self._get_option("match", "min_height", default=0)
        return Preference(not_list, allowed_list, pref_list, width, height)
    
    def get_handler(self, handler):
        return self._get_all_options_as_dictionary("handler_" + handler.lower())
    
    def get_handlers(self):
        return (self._get_option("handlers", "primary", default=[], is_list=True),
                self._get_option("handlers", "secondary", default=[], is_list=True))
        
    def get_active_feeds(self):
        feeds = [l[0] for l in self._get_list("active", ["url"], 0)]
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
        l = self.config.items(section)
        d = {}
        for i in l:
            d[i[0]] = self._parse_option(i[1])
        return d
    
    def _parse_option(self, option, is_list=False):
        if option.find(",") > -1 and not (option.startswith('"') or option.endswith('"')):
            is_list = True
        result = option.strip(' ').strip('"')
        if len(result) == 0:
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