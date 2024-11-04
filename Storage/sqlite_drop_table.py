import sqlite3


conn = sqlite3.connect('movies_reviews.sqlite')
c = conn.cursor()

# Drop the movie table if it exists
c.execute('''
          DROP TABLE IF EXISTS movie
          ''')

# Drop the review table if it exists
c.execute('''
          DROP TABLE IF EXISTS review
          ''')

conn.commit()
print("Dropped movies and reviews table")
conn.close()
