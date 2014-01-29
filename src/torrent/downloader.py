'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from os.path import join

from src.torrent.match_handler import MatchHandler
from src.http.request import Request

from src.logger import get_logger
logger = get_logger(__name__)

class Downloader(MatchHandler):
    '''
    This class will download torrents to a location
    '''

    def __init__(self, matches, directory):
        MatchHandler.__init__(self, matches, name="Downloader")
        self.directory = directory
        
    def handle(self, match):
        url = match.torrent.url()
        if url is not None:
            filename = match.torrent.filename()
            path = join(self.directory, filename)
            logger.debug("Downloading %s to %s", url, path)
            download = Request(url).request()
            
            if download is None:
                return False
            
            if download.startswith("d8:announce"):
                try:
                    with open(path, "wb") as f:
                        f.write(download)
                    return True
                except IOError:
                    logger.error("Could not write to %s", path)
            else:
                logger.warning("This content does not correspond to a torrent: %s", download[:100])
        return False
                
            
        