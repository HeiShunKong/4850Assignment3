from flask import Flask, jsonify, request
import json
import logging
import logging.config
from kafka import KafkaConsumer
import os
import yaml
from threading import Thread

# Determine which environment configuration to use
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# Load the app configurations
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load the logging configurations
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Configuration variables
KAFKA_TOPIC = app_config["kafka"]["topic"]
KAFKA_SERVER = f"{app_config['kafka']['hostname']}:{app_config['kafka']['port']}"
THRESHOLDS = app_config["thresholds"]
DATA_STORE = app_config["data_store"]["path"]

# Kafka consumer setup
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

# JSON data store
def load_anomalies():
    try:
        with open(DATA_STORE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Create if not exist
        with open(DATA_STORE, "w") as f:
            json.dump([], f, indent=4)
        return []

# Save in to json
def save_anomalies(anomalies):
    with open(DATA_STORE, "w") as f:
        json.dump(anomalies, f, indent=4)


# Consume Kafka events and detect anomalies
def process_events():
    for message in consumer:  # Get received message
        event = message.value
        logging.info(f"Event consumed: {event}")
        
        anomalies = load_anomalies()  # Load existing anomalies from data.json

        # Movie event's length anomaly
        if "event_type" in event and event["event_type"] == "movie" and "length" in event and event["length"] > 180:
            # Ensure the event is of type 'movie' and length is longer than 180 mins
            anomaly = {
                "event_id": event["id"],
                "trace_id": event["trace_id"],
                "event_type": "movie",  
                "anomaly_type": "Too Long", 
                "description": f"Movie length is too long ({event['length']} > 180 minutes)",
                "timestamp": event["timestamp"]
            }
            anomalies.append(anomaly)
            logging.info(f"Anomaly detected: {anomaly}")

        # Review event's comment word count anomaly
        if "event_type" in event and event["event_type"] == "review" and "comment" in event:  
            # Ensure the event is of type 'review' and contains a comment field
            word_count = len(event["comment"].split())  # Count words in the comment
            if word_count > 50:
                anomaly = {
                    "event_id": event["id"],
                    "trace_id": event["trace_id"],
                    "event_type": "review", 
                    "anomaly_type": "Too Verbose",
                    "description": f"Review/comment is too verbose ({word_count} words > 50 words)",
                    "timestamp": event["timestamp"]
                }
                anomalies.append(anomaly)
                logging.info(f"Anomaly detected: {anomaly}")

        # Save anomalies
        save_anomalies(anomalies)



# Function to filter anomaly type
def get_anomalies(anomaly_type=None):
    anomalies = load_anomalies() # Load data.json
    
    if anomaly_type: # Check if anomaly type match
        filtered_anomalies = [a for a in anomalies if a["anomaly_type"] == anomaly_type]
    else:
        filtered_anomalies = anomalies  
    
    # Log the count of anomalies returned
    logger.info(f"Returned {len(filtered_anomalies)} anomalies")
    
    # Return the list of filtered anomalies
    return filtered_anomalies

# Start Kafka consumer in a separate thread
def start_kafka_consumer():
    consumer_thread = Thread(target=process_events)
    consumer_thread.daemon = True
    consumer_thread.start()

# Main entry point
if __name__ == "__main__":
    start_kafka_consumer()
    app.run(port=8120, host="0.0.0.0")
