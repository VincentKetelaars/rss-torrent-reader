'''
Created on Feb 9, 2014

@author: Vincent Ketelaars
'''
import sys
from random import sample
from datetime import datetime, timedelta
from src.general.constants import ACTIVE_SERIES_CATEGORIES, ACTIVE_SERIES_SHARE,\
    SEARCH_REPLACE_VALUE
from urllib import quote_plus

class ActiveSearchFeeds(object):
    '''
    This class takes in movies and series and creates new rss feeds
    For movies the focus will be on older movies, randomly chosen, because the newer ones will likely not be available
    and are very likely to be found by the passive rss feeds
    For series the focus will be on series of which the last download was between a week and a month old for 80%
    but will choose older series for 20% as well
    '''

    def __init__(self, movies, series):
        self.movies = movies
        self.series = series
        
    def _get_most_current_movie(self):
        """
        Return the current most movie that was downloaded
        """
        movies = sorted([m for m in self.movies.itervalues()], key=lambda x: x.release, reverse=True)
        for m in movies:
            if m.is_downloaded():
                return m
        return movies[0]
        
    def get_feeds(self, active_feed_params):
        """
        This method creates urls that will return results for searches on specific movies and series.
        The movies are chosen such that the only older releases are searched than we have actually downloaded.
        The series are chosen according to the ACTIVE_SERIES_CATEGORIES, and the respective ACTIVE_SERIES_SHARE weights.
        @return: {url, film}
        """
        chosen_movies = []
        if len(self.movies) > 0:
            most_current = self._get_most_current_movie()        
            dmovies = [m for m in self.movies.itervalues() if m.should_download() and 
                       (m.release < most_current.release or m.release == datetime.min)]
            chosen_movies = sample(dmovies, min(active_feed_params.max_movies, len(dmovies)))
            if len(chosen_movies) < active_feed_params.max_movies: # Fill up as much as possible if needed
                dmovies = [m for m in self.movies.itervalues() if m.should_download() and m.release > most_current.release]
                chosen_movies += sample(dmovies, min(active_feed_params.max_movies - len(chosen_movies), len(dmovies)))
        dseries = [s for s in self.series.itervalues() if s.should_download(sys.maxint, sys.maxint)]
        chosen_series = []
        if len(dseries) > 0:
            start_time = timedelta()
            for i in range(len(ACTIVE_SERIES_CATEGORIES)):
                categorie = [s for s in dseries if s.time_downloaded < datetime.utcnow() - start_time and
                             s.time_downloaded > datetime.utcnow() - ACTIVE_SERIES_CATEGORIES[i]]
                chosen_series += sample(categorie,
                                        min(len(categorie), int(ACTIVE_SERIES_SHARE[i] * active_feed_params.max_series)))
                start_time = ACTIVE_SERIES_CATEGORIES[i]
            # In case there is room left for more
            chosen_series += sample(set(dseries) - set(chosen_series), active_feed_params.max_series - len(chosen_series))
        urls = {}
        for m in chosen_movies + chosen_series:
            for u in active_feed_params.urls:
                urls[u.replace(SEARCH_REPLACE_VALUE, quote_plus(m.search_string()))] = m
        return urls