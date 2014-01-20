'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

import wx

from src.conf.configuration import Configuration

from src.constants.constants import TITLE_MAIN, CONF_FILE
from src.content.imdb import IMDB
from src.rss.feed_handler import FeedHandler
from src.content.write_imdb_to_csv import WriteIMDBToCsv
from src.content.merge_imdb_csv import MergeIMDBCsv

from src.logger import get_logger
from src.torrent.decider import Decider
from src.torrent.downloader import Downloader
logger = get_logger(__name__)

def main():
#     app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
#     frame = wx.Frame(None, wx.ID_ANY, TITLE_MAIN) # A Frame is a top-level window.
#     frame.Show(True)     # Show the frame.
#     app.MainLoop()
    conf = Configuration(CONF_FILE)
    imdb = IMDB(conf.get_imdb_csv_urls())
    merge = MergeIMDBCsv(imdb, *conf.get_imdb_paths())
    merge.start()
    feed = FeedHandler(conf.get_torrent_rss_feeds())
    decider = Decider(merge, feed, conf.get_torrent_preference())
    matches = decider.decide() # blocking
    downloader = Downloader(matches, **conf.get_handler("downloader"))
    downloader.start()
    # Write the updated values (ensure that downloaded torrents are assimilated as well)
    writer = WriteIMDBToCsv(merge.movies(), downloader, *conf.get_imdb_paths())
    writer.start()
    logger.info("We have %d IMDB movies", len(imdb.movies()))
    logger.info("We have %d torrents from %d channels", len(feed.torrents()), len(feed.channels()))
    logger.info("We have %d matches", len(matches))
    for m in matches:
        logger.info("Match %s with %s", m.movie.title, m.torrent.title)

if __name__ == '__main__':
    main()