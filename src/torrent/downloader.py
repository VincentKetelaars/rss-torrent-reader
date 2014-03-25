'''
Created on Jan 19, 2014

@author: Vincent Ketelaars
'''
from os.path import join
import xml.etree.ElementTree as ET

from src.torrent.match_handler import MatchHandler
from src.http.request import Request

from src.logger import get_logger
from threading import Thread
logger = get_logger(__name__)

class Downloader(MatchHandler):
    '''
    This class will download torrents to a location
    '''
    
    NAME = "Downloader"
    PARAMETERS = ["directory"]

    def __init__(self, matches, directory, **kwargs):
        MatchHandler.__init__(self, matches, name=Downloader.NAME, **kwargs)
        self.directory = directory
        
    def handle_matches(self, matches):
        # Intermediate successes are stored in self.successes
        threads = [(m, Thread(target=self.handle, name="Downloader_" + m.movie.title, args=(m, self.successes))) for m in matches]
        successes = [] # This is returned to self.successes
        for t in threads:
            t[1].start()
        for t in threads:
            t[1].join() # Wait till they are all done
            successes.append(t[0])
        return successes
        
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
                    logger.info("Successfully downloaded %s to %s", url, path)
                    return True
                except IOError:
                    logger.error("Could not write to %s", path)
            else:
                logger.warning("This content does not correspond to a torrent: %s", download[:100])
        return False
    
    @staticmethod
    def create_html(directory="", **kwargs):
        div = MatchHandler.create_html(name="Downloader", class_name="download_handler", **kwargs)
        MatchHandler.add_label_input_br(div, "Directory", 50, "directory", directory)
        return div
        