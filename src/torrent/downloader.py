'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from os.path import join

from src.torrent.match_handler import MatchHandler
from src.http.request import Request

from src.logger import get_logger
from threading import Thread
logger = get_logger(__name__)

class Downloader(MatchHandler):
    '''
    This class will download torrents to a location
    '''

    def __init__(self, matches, directory, **kwargs):
        MatchHandler.__init__(self, matches, name="Downloader", **kwargs)
        self.directory = directory
        
    def handle_matches(self, matches):
        threads = [(m, Thread(target=self.handle, args=(m,self.successes))) for m in matches]
        for t in threads:
            t[1].start()
        for t in threads:
            t[1].join() # Wait till they are all done
        return matches
        
    def handle(self, match, successes):
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
                    successes.append(match)
                    return True
                except IOError:
                    logger.error("Could not write to %s", path)
            else:
                logger.warning("This content does not correspond to a torrent: %s", download[:100])
        return False
                
            
        