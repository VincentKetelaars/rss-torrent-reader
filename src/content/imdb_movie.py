'''
Created on Dec 31, 2013

@author: Vincent Ketelaars
'''

class IMDBMovie(object):
    '''
    IMDB Movie description
    
    const,created,modified,description,Title,Title type,Directors,You rated,IMDb Rating,
    Runtime (mins),Year,Genres,Num. Votes,Release Date(month/day/year),URL
    '''

    def __init__(self, id_, created, modified, desc, title, type_, directors, rate, 
                 rating, runtime, year, genres, votes, release, url):
        self.id = id_
        self.created = created
        self.modified = modified
        self.desc = desc
        self.title = title
        self.type = type_
        self.directors = directors
        self.rate = rate
        self.rating = rating
        self.runtime = runtime # min
        self.year = year
        self.genres = genres
        self.votes = votes
        self.release = release
        self.url = url

    def is_serie(self):
        return self.type == "TV Series"
    
    