'''
Created on Aug 2, 2014

@author: Vincent Ketelaars
'''

from src.logger import get_logger
logger = get_logger(__name__)

# Overwrite sys.excepthook to ensure that uncaught exceptions are also logged
import sys
import traceback
def uncaught_logger(etype, value, tb):
    logger.error("".join(traceback.format_exception(etype, value, tb)))
sys.excepthook = uncaught_logger

from src.conf.configuration import Configuration, get_location_from_text_file

from src.general.constants import CONF_LOCATION_FILE, MERGER_WAIT
from src.content.imdb import IMDB
from src.content.write_imdb_to_csv import WriteIMDBToCsv
from src.content.merge_imdb_csv import MergeIMDBCsv
from src.content.imdb_read_from_file import IMDBReadFromFile

def main(args):
    tries = 1
    try:
        tries = int(args[0])
    except ValueError:
        logger.warning("The first argument was not an integer, performing task %d time", tries)
    for i in range(tries):
        logger.debug("Accessing IMDB, try %d out of %d", i + 1, tries)
        if try_access_imdb():
            logger.info("Successfully updated the local file with IMDB watchlist")
            break
    else:
        logger.info("Could not access IMDB watchlist for update")

def try_access_imdb():
    conf = Configuration(get_location_from_text_file(CONF_LOCATION_FILE))
    movie_file, series_file, missed_file = conf.get_imdb_paths()
    movies_from_file = IMDBReadFromFile(movie_file).read()
    series_from_file = IMDBReadFromFile(series_file).read()
    imdb = IMDB(conf.get_imdb_csv_urls())
    merge = MergeIMDBCsv(imdb, movies_from_file, series_from_file)
    merge.start()
    merge.wait(MERGER_WAIT)
    if len(imdb.movies()) == 0:
        return False

    # Write the updated values
    writer = WriteIMDBToCsv(merge.movies(), movie_file, series_file)
    writer.start()
    logger.info("We have %d IMDB movies of which %d should be downloaded", len(imdb.movies()), len([m for m in imdb.movies().itervalues() if m.download]))
    return True

if __name__ == '__main__':
    main(sys.argv[1:])