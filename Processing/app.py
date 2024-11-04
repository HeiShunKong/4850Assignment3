import connexion
from connexion import NoContent
from datetime import datetime
import json
import logging
import logging.config
import requests
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler

# Load the app configurations
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load the logging configurations
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def populate_stats():
    logger.info("Start Periodic Processing")

    try: # Load it app_conf.yml data.json to read
        with open(app_config['datastore']['filename'], 'r') as f:
            current_stats = json.load(f)
    except FileNotFoundError: # If not found make a new dicitonary
        current_stats = {
            "num_movies": 0,
            "avg_movie_length": 0,
            "num_reviews": 0,
            "max_review_rating": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    # Timestamp
    end_timestamp = datetime.now().isoformat(timespec='milliseconds') + 'Z'
    start_timestamp = current_stats.get("last_updated", datetime.now().isoformat(timespec='milliseconds') + 'Z')

    # Starts variable
    new_max_review_rating = 0
    total_movie_length = 0
    movie_count = 0
    total_review_count = 0

    try:
        # Fetch data Making HTTP GET requests # No hardcode URL
        movies_response = requests.get(f"{app_config['eventstore']['url']}/movie?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}")
        reviews_response = requests.get(f"{app_config['eventstore']['url']}/review?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}")

        # Handle movies response
        if movies_response.status_code == 200:
            movies_data = movies_response.json()
            logger.info(f"Received {len(movies_data)} movies.")
            current_stats["num_movies"] += len(movies_data)
            # Caculate all movies average length
            for movie in movies_data:
                movie_length = movie.get("length", 0)
                total_movie_length += movie_length
                movie_count += 1

            if movie_count > 0:
                current_stats["avg_movie_length"] = total_movie_length / movie_count

        else:
            logger.error(f"Failed to get movies: {movies_response.status_code}")

        # Handle reviews response
        if reviews_response.status_code == 200:
            reviews_data = reviews_response.json()
            logger.info(f"Received {len(reviews_data)} reviews.")
            current_stats["num_reviews"] += len(reviews_data)
            # Caculate max review rating
            for review in reviews_data:
                review_rating = review.get("rating", 0)
                if review_rating > new_max_review_rating:
                    new_max_review_rating = review_rating

            current_stats["max_review_rating"] = max(current_stats["max_review_rating"], new_max_review_rating)

        else:
            logger.error(f"Failed to get reviews: {reviews_response.status_code}")

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")

    # update to current timestamp
    current_stats["last_updated"] = end_timestamp
    
    # Writing to data.json
    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(current_stats, f)

    logger.debug(f"Updated statistics: {current_stats}")
    logger.info("Periodic Processing has ended.")


def init_scheduler(): # Manage periodic tasks Run tasks in background
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats(): # Fetch and return data from JSON file
    logger.info("Get stats request has started")

    try: # Read data.json
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        logger.error("Statistics do not exist")
        return {"message": "Statistics do not exist"}, 404

    response_data = { # Make a dictionary
        "num_movies": stats.get("num_movies", 0),
        "avg_movie_length": stats.get("avg_movie_length", 0),
        "num_reviews": stats.get("num_reviews", 0),
        "max_review_rating": stats.get("max_review_rating", 0),
        "last_updated": stats.get("last_updated", "")
    }

    logger.debug(f"Stats response data: {response_data}")
    logger.info("Get stats request has completed")
    
    return response_data, 200

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
#use_reloader=False