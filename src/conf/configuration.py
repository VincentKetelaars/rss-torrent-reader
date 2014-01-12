'''
Created on Dec 24, 2013

@author: Vincent Ketelaars
'''
import ConfigParser

from src.content.imdb_csv import IMDBCsv
from src.logger import get_logger
from src.constants.constants import DEFAULT_MOVIES_CSV, DEFAULT_SERIES_CSV
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
        l = self.config.items("webgui")
        d = {}
        for i in l:
            d[i[0]] = i[1]
        return d
    
    def get_imdb_paths(self):
        m = DEFAULT_MOVIES_CSV
        s = DEFAULT_SERIES_CSV
        try:
            m = self.config.get("imdb", "movies")
            s = self.config.get("imdb", "series")
        except:
            pass
        return (m, s)
    
    def _get_list(self, section, options, start=0):
        l = []
        i = start
        while True:
            t = []
            for o in options:
                try:
                    t.append(self.config.get(section, o +  str(i)).strip('"'))
                except: # Assume not more valid options
                    logger.debug("We do not have this option %s number %d", o, i)
                    break
            if not t: # t == []
                break
            l.append(t)
            i+=1
        return l