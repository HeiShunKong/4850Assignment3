import sqlite3
from datetime import datetime

conn = sqlite3.connect('movies_reviews.sqlite')
c = conn.cursor() # Excute sql command

# Create table for movies 
c.execute('''
          CREATE TABLE IF NOT EXISTS movie
          (id INTEGER PRIMARY KEY ASC, 
           movie_id VARCHAR(250) NOT NULL,
           title VARCHAR(250) NOT NULL,
           release_date DATE NOT NULL,
           length INTEGER NOT NULL,
           genre VARCHAR(100) NOT NULL,
           cast VARCHAR(500) NOT NULL,
           director VARCHAR(250) NOT NULL,
           date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)
          ''')

# Create table for reviews
c.execute('''
          CREATE TABLE IF NOT EXISTS review
          (id INTEGER PRIMARY KEY ASC, 
           user_id VARCHAR(250) NOT NULL,
           movie_id VARCHAR(250) NOT NULL,
           comment TEXT NOT NULL,
           rating INTEGER NOT NULL,
           date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)
          ''')

conn.commit() # Commit the changes and close the connection
print("Created movies and reviews table")
conn.close()
