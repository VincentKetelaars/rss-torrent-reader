'''
Created on May 4, 2014

@author: Vincent Ketelaars
'''
import tempfile
import os
import subprocess

from threading import Thread, Event

from src.torrent.downloader import Downloader
from src.torrent.match_handler import MatchHandler
from src.logger import get_logger
logger = get_logger(__name__)

class ExecutionHandler(MatchHandler):
    '''
    This handler will download the file to some location and subsequently execute the command on it
    '''
    
    NAME="ExecutionHandler"
    PARAMETERS=["directory", "command"]
    PLACE_HOLDER = "TORRENT"

    MAX_TIME_WAIT_FOR_REMOVE = 100 # Seconds
    STEP_TIME_WAIT_FOR_REMOVE = 1 # Seconds

    def __init__(self, matches, directory, command, delete_when_done=True, **kwargs):
        MatchHandler.__init__(self, matches, name=ExecutionHandler.NAME, **kwargs)
        self.directory = directory
        self.command = command
        self.delete_when_done = False if delete_when_done == False else True # Only use false if user stated that explicitly
        
    def handle_matches(self, matches):
        if self.directory is None:
            self.directory = tempfile.gettempdir()
        if self.command is None or self.command.find(self.PLACE_HOLDER) == -1:
            return []
        # Intermediate successes are stored in self.successes
        threads = [(m, Thread(target=self.handle, name="Executioner" + m.movie.title, 
                              args=(self.directory, self.command, self.delete_when_done, m, self.successes))) for m in matches]
        for t in threads:
            t[1].start()
        for t in threads:
            t[1].join() # Wait till they are all done
        return self.successes # Not pretty, but easy solution
    
    def handle(self, directory, command, delete_when_done, match, successes):
        path = Downloader([], None).handle(directory, match, [])
        if path is not None and os.path.isfile(path):
            command = command.replace(self.PLACE_HOLDER, path)
            last_access_time = os.path.getatime(path)
            logger.debug("Executing %s, last accessed %d", command, last_access_time)
            return_code = subprocess.call(command, shell=True)
            logger.debug("Executed %s with return code %d", command, return_code)
            if return_code == 0:
                successes.append(match)
            else:
                logger.warning("Executing %s failed with return code %d", command, return_code)
            event = Event()
            while os.path.getatime(path) <= last_access_time and self.MAX_TIME_WAIT_FOR_REMOVE > 0:
                event.wait(self.STEP_TIME_WAIT_FOR_REMOVE)
                self.MAX_TIME_WAIT_FOR_REMOVE -= self.STEP_TIME_WAIT_FOR_REMOVE
            if delete_when_done:
                logger.debug("Removing %s", path)
                os.remove(path)
        else:
            logger.warning("Failed to get %s", match.torrent.url())
        
    @staticmethod
    def create_html(directory="", command="", delete_when_done=True, **kwargs):
        div = MatchHandler.create_html(name=ExecutionHandler.NAME, class_name="download_handler", **kwargs)
        MatchHandler.add_label_input_br(div, "Directory", 50, "directory", directory, explanation="Defaults to temporary folder")
        MatchHandler.add_label_input_br(div, "Command", 50, "command", command, 
                                        explanation="Command to be executed with " + ExecutionHandler.PLACE_HOLDER + " as placeholder")
        MatchHandler.add_label_input_br(div, "Delete", 50, "delete_when_done", delete_when_done, explanation="Delete file when done (True / False), default True")
        return div
        