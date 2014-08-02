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

def main():
    conf = Configuration(get_location_from_text_file(CONF_LOCATION_FILE))
    movie_file, series_file, missed_file = conf.get_imdb_paths()
    movies_from_file = IMDBReadFromFile(movie_file).read()
    series_from_file = IMDBReadFromFile(series_file).read()
    imdb = IMDB(conf.get_imdb_csv_urls())
    merge = MergeIMDBCsv(imdb, movies_from_file, series_from_file)
    merge.start()
    merge.wait(MERGER_WAIT)
    # Write the updated values (ensure that downloaded torrents are assimilated as well)
    writer = WriteIMDBToCsv(merge.movies(), movie_file, series_file)
    writer.start()
    logger.info("We have %d IMDB movies of which %d should be downloaded", len(imdb.movies()), len([m for m in imdb.movies().itervalues() if m.download]))

if __name__ == '__main__':
    main()