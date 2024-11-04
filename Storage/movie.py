import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base

class Movie(Base): # Create a movie class
    """ Movie """

    __tablename__ = "movie"

    id = Column(Integer, primary_key=True)
    movie_id = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    release_date = Column(String(100), nullable=False)
    length = Column(Integer, nullable=False)
    genre = Column(String(100), nullable=False)
    cast = Column(String(500), nullable=False)
    director = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(40), nullable=False)

    def __init__(self, movie_id, title, release_date, length, genre, cast, director, trace_id): # Initialize a new movie object
        """ Initializes a movie entry """
        self.movie_id = movie_id
        self.title = title
        self.release_date = release_date
        self.length = length
        self.genre = genre
        self.cast = cast
        self.director = director
        self.date_created = datetime.datetime.now()  # Timestamp created
        self.trace_id = trace_id

    def to_dict(self):  # To dictionary
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'title': self.title,
            'release_date': self.release_date,
            'length': self.length,
            'genre': self.genre,
            'cast': self.cast,
            'director': self.director,
            'date_created': self.date_created,
            'trace_id': self.trace_id
        }
