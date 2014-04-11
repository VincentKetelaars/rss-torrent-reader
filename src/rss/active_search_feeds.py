'''
Created on Feb 9, 2014

@author: Vincent Ketelaars
'''
import sys
from random import sample
from datetime import datetime, timedelta
from urllib import quote_plus

from src.general.constants import ACTIVE_SERIES_CATEGORIES, ACTIVE_SERIES_SHARE,\
    SEARCH_REPLACE_VALUE
from src.logger import get_logger
logger = get_logger(__name__)

class ActiveSearchFeeds(object):
    '''
    This class takes in movies and series and creates new rss feeds
    For movies the focus will be on older movies, randomly chosen, because the newer ones will likely not be available
    and are very likely to be found by the passive rss feeds
    For series the focus will be on series of which the last download was between a week and a month old for 80%
    but will choose older series for 20% as well
    '''

    def __init__(self, movies, series, daily):
        self.movies = movies
        self.series = series
        self.daily = daily
        
    def _get_most_current_movie(self):
        """
        Return the current most movie that was downloaded
        """
        movies = sorted([m for m in self.movies.itervalues()], key=lambda x: x.release, reverse=True)
        for m in movies:
            if m.is_downloaded():
                return m
        return movies[0]
    
    def choose_movies(self, active_feed_params):
        chosen_movies = []
        if len(self.movies) > 0:
            most_current = self._get_most_current_movie()        
            dmovies = [m for m in self.movies.itervalues() if m.download and 
                       (m.release < most_current.release or m.release == datetime.min)]
            chosen_movies = sample(dmovies, min(active_feed_params.max_movies, len(dmovies)))
            if len(chosen_movies) < active_feed_params.max_movies: # Fill up as much as possible if needed
                dmovies = [m for m in self.movies.itervalues() if m.download and m.release > most_current.release]
                chosen_movies += sample(dmovies, min(active_feed_params.max_movies - len(chosen_movies), len(dmovies)))
        return chosen_movies
    
    def choose_series(self, active_feed_params):
        chosen_series = []
        if chosen_series is not None:
            chosen_series = self.daily_series()
        logger.debug("We have %d series today, namely %s", len(chosen_series), [str(s) for s in chosen_series])
        dseries = [s for s in self.series.itervalues() if s.download]
        if len(dseries) > 0:
            start_time = timedelta()
            for i in range(len(ACTIVE_SERIES_CATEGORIES)):
                categorie = [s for s in dseries if s.time_downloaded < datetime.utcnow() - start_time and
                             s.time_downloaded > datetime.utcnow() - ACTIVE_SERIES_CATEGORIES[i]]
                samples = sample(categorie, min(len(categorie), int(ACTIVE_SERIES_SHARE[i] * 
                                                                (active_feed_params.max_series - len(chosen_series)))))
                logger.debug("Chosen %s with %f chance of max %d feeds between %s and %s out of %d in categorie", 
                             [str(s) for s in samples], ACTIVE_SERIES_SHARE[i], active_feed_params.max_series, 
                             str(datetime.utcnow() - ACTIVE_SERIES_CATEGORIES[i]),
                             str(datetime.utcnow() - start_time), len(categorie))
                chosen_series += samples
                start_time = ACTIVE_SERIES_CATEGORIES[i]
            # In case there is room left for more
            samples = sample(set(dseries) - set(chosen_series), active_feed_params.max_series - len(chosen_series))
            logger.debug("Had to choose the remainder of series: %s", [str(s) for s in samples])
            chosen_series += samples
        return chosen_series
    
    def daily_series(self):
        self.daily.wait()
        chosen = []
        for ds in self.daily.series():
            for s in self.series.itervalues():
                if s.title == ds.title and s.is_newer(ds.season, ds.episode):
                    chosen.append(s)
                    break
        return chosen
        
    def movie_to_url(self, active_feed_params, movies):
        urls = {}
        for m in movies:
            for u in active_feed_params.urls:
                urls[u.replace(SEARCH_REPLACE_VALUE, quote_plus(m.search_string()))] = m
        return urls

    def get_feeds(self, active_feed_params):
        """
        This method creates urls that will return results for searches on specific movies and series.
        The movies are chosen such that the only older releases are searched than we have actually downloaded.
        The series are chosen according to the ACTIVE_SERIES_CATEGORIES, and the respective ACTIVE_SERIES_SHARE weights.
        @return: {url, film}
        """
        chosen_movies = self.choose_movies(active_feed_params)
        chosen_series = self.choose_series(active_feed_params)
        return self.movie_to_url(active_feed_params, chosen_movies + chosen_series)
    