import mysql.connector
from datetime import datetime

# Connect to MySQL
db_conn = mysql.connector.connect(
    host="mysql-3855.centralus.cloudapp.azure.com", 
    user="user", 
    password="yourpassword", 
    database="movies_reviews_db"  
)
db_cursor = db_conn.cursor()

# Create table for movies
db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS movie (
           id INT NOT NULL AUTO_INCREMENT, 
           movie_id VARCHAR(250) NOT NULL,
           title VARCHAR(250) NOT NULL,
           release_date VARCHAR(100) NOT NULL,
           length INT NOT NULL,
           genre VARCHAR(100) NOT NULL,
           cast VARCHAR(500) NOT NULL,
           director VARCHAR(250) NOT NULL,
           date_created DATETIME NOT NULL,
           trace_id CHAR(40) NOT NULL,
           CONSTRAINT movie_pk PRIMARY KEY (id))
          ''')

# Create table for reviews
db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS review (
           id INT NOT NULL AUTO_INCREMENT, 
           user_id VARCHAR(250) NOT NULL,
           movie_id VARCHAR(250) NOT NULL,
           comment TEXT NOT NULL,
           rating INT NOT NULL,
           date_created DATETIME NOT NULL,
           trace_id CHAR(40) NOT NULL,
           CONSTRAINT review_pk PRIMARY KEY (id))
          ''')

db_conn.commit()  # Commit the changes
print("Created movies and reviews tables in MySQL")

db_conn.close()  # Close the connection
