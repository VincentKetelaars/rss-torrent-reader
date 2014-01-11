'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

import wx
from threading import Event

from src.logger import get_logger
from src.conf.configuration import Configuration

from src.constants.constants import TITLE_MAIN, CONF_FILE
from src.content.imdb import IMDB
from src.rss.feed_handler import FeedHandler

logger = get_logger(__name__)

def main():
#     app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
#     frame = wx.Frame(None, wx.ID_ANY, TITLE_MAIN) # A Frame is a top-level window.
#     frame.Show(True)     # Show the frame.
#     app.MainLoop()
    conf = Configuration(CONF_FILE)
    event = Event()
    imdb = IMDB(conf.get_imdb_csv_urls(), event)
    feed = FeedHandler(conf.get_torrent_rss_feeds(), event)
    event.wait(10.0)
    event.clear()
    event.wait(30.0)
    logger.info("We have %d IMDB movies", len(imdb.movies()))
    logger.info("We have %d torrents from %d channels", len(feed.torrents()), len(feed.channels()))

if __name__ == '__main__':
    main()