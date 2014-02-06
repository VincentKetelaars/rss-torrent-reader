'''
Created on Feb 6, 2014

@author: Vincent Ketelaars
'''
import unittest
from src.content.movie_parser import MovieParser
from src.general.constants import NEWLINE

class Test(unittest.TestCase):

    def setUp(self):
        self.text = '"0-0","tt1474684","Sun Feb  2 10:26:36 2014","Sun Feb  2 10:26:36 2014","","Luther","TV Series","","","8.7","360","2010","crime, drama, mystery","33083","2010-05-04","http://www.imdb.com/title/tt1474684/"' + NEWLINE

    def tearDown(self):
        pass

    def test_read_write_read(self):
        movies = MovieParser(self.text).parse(self.text)
        text = "".join([m.to_line() + NEWLINE for m in movies.itervalues()])
        new_movies = MovieParser(text).parse(text)
        self.assertItemsEqual(movies, new_movies)

if __name__ == "__main__":
    unittest.main()