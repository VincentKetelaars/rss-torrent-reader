'''
Created on Oct 20, 2013

@author: Vincent Ketelaars
'''

from src.logger import get_logger
from src.rss.daily_series import DailySeries
logger = get_logger(__name__)

# Overwrite sys.excepthook to ensure that uncaught exceptions are also logged
import sys
import traceback
def uncaught_logger(etype, value, tb):
    logger.error("".join(traceback.format_exception(etype, value, tb)))
sys.excepthook = uncaught_logger

from src.conf.configuration import Configuration

from src.general.constants import CONF_FILE
from src.content.imdb import IMDB
from src.rss.feed_handler import FeedHandler
from src.content.write_imdb_to_csv import WriteIMDBToCsv
from src.content.merge_imdb_csv import MergeIMDBCsv
from src.torrent.decider import Decider
from src.torrent.handler_factory import HandlerFactory
from src.content.imdb_read_from_file import IMDBReadFromFile
from src.rss.active_search_feeds import ActiveSearchFeeds

def main():
    conf = Configuration(CONF_FILE)
    movie_file, series_file = conf.get_imdb_paths()
    movies_from_file = IMDBReadFromFile(movie_file).read()
    series_from_file = IMDBReadFromFile(series_file).read()
    imdb = IMDB(conf.get_imdb_csv_urls())
    daily = DailySeries()
    daily.start()
    active_feeds = ActiveSearchFeeds(movies_from_file, series_from_file, daily).get_feeds(conf.get_active_feeds())
    merge = MergeIMDBCsv(imdb, movies_from_file, series_from_file)
    merge.start()
    feed = FeedHandler(conf.get_torrent_rss_feeds(), active_feeds)
    decider = Decider(merge, feed, conf.get_torrent_preference())
    matches = decider.decide() # blocking
    factory = HandlerFactory(matches, conf)
    factory.start()
    # Write the updated values (ensure that downloaded torrents are assimilated as well)
    writer = WriteIMDBToCsv(merge.movies(), factory, *conf.get_imdb_paths())
    writer.start()
    logger.info("We have %d IMDB movies", len(imdb.movies()))
    logger.info("We have %d torrents from %d channels", len(feed.torrents()), len(feed.channels()))
    logger.info("We have %d matches", len(matches))
    for m in matches:
        logger.info("Match %s with %s", m.movie.title, m.torrent.title)

if __name__ == '__main__':
    main()