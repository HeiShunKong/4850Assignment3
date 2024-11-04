import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base

class Review(Base): # Create a review class
    """ Review """

    __tablename__ = "review"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    movie_id = Column(String(250), nullable=False)
    comment = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(40), nullable=False)

    def __init__(self, user_id, movie_id, comment, rating, trace_id): # New review object
        """ Initializes a review entry """
        self.user_id = user_id
        self.movie_id = movie_id
        self.comment = comment
        self.rating = rating
        self.date_created = datetime.datetime.now() # Timestamp created
        self.trace_id = trace_id

    def to_dict(self): # To dictionary
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'comment': self.comment,
            'rating': self.rating,
            'date_created': self.date_created,
            'trace_id': self.trace_id
        }
