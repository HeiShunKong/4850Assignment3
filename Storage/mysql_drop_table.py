import mysql.connector

# Connect to MySQL
db_conn = mysql.connector.connect(
    host="mysql-3855.centralus.cloudapp.azure.com",    
    user="user",  
    password="yourpassword",
    database="movies_reviews_db"  
)
db_cursor = db_conn.cursor()

# Drop the movie table if it exists
db_cursor.execute('''
          DROP TABLE IF EXISTS movie
          ''')

# Drop the review table if it exists
db_cursor.execute('''
          DROP TABLE IF EXISTS review
          ''')

db_conn.commit()  # Commit the changes
print("Dropped movie and review tables in MySQL")

db_conn.close()  # Close the connection
