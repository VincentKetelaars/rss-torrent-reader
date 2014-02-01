'''
Created on Dec 24, 2013

@author: Vincent Ketelaars
'''
import ConfigParser

from src.content.imdb_csv import IMDBCsv
from src.logger import get_logger
from src.constants.constants import DEFAULT_MOVIES_CSV, DEFAULT_SERIES_CSV
from src.torrent.preference import Preference
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
        width = int(self._get_option("match", "min_width", default=0))
        height = int(self._get_option("match", "min_height", default=0))
        return Preference(not_list, allowed_list, pref_list, width, height)
    
    def get_handler(self, handler):
        return self._get_all_options_as_dictionary("handler_" + handler.lower())
    
    def get_handlers(self):
        return self._get_option("handlers", "handlers", default=[], is_list=True)
    
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
            d[i[0]] = i[1]
        return d
    
    def _get_option(self, section, option, default=None, is_list=False):
        try:
            result = self.config.get(section, option).strip('"')
            if is_list:
                result = [r.strip() for r in result.split(",")]
            return result
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            logger.debug("We do not have this option %s in section %s", option, section)
        return default