from pymongo import MongoClient
from kafka import KafkaConsumer
import json
import logging
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)


client = MongoClient('localhost', 27017)
db = client['TT']
location_collection = db['bus_locations']
eta_collection = db['eta_pred']

consumer = KafkaConsumer(
    'busLocations',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('ascii'))
)

BUS_STOPS = [
    {"id": 1, "name": "Stop 1", "location": (40.7150, -74.0080)},
    {"id": 2, "name": "Stop 2", "location": (40.7170, -74.0100)},
    {"id": 3, "name": "Stop 3", "location": (40.7190, -74.0120)},
]


def calculate_distance(p1, p2):

    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


def estimate_arrival_time(bus_pos, stop_pos, avg_Speed=0.0001):
    distance = calculate_distance(bus_pos, stop_pos)
    time_arrival = distance/avg_Speed
    return datetime.now()+timedelta(seconds=time_arrival)


def process_bus_location():

    for message in consumer:
        bus_data = message.value

        location_collection.insert_one(bus_data)

        bus_pos = (bus_data['latitude'], bus_data['longitude'])

        for stop in BUS_STOPS:
            eta = estimate_arrival_time(bus_pos, stop['location'])

            eta_pred = {
                'busId': bus_data['busId'],
                'stopId': stop['id'],
                'eta': eta.isoformat(),
                'calculatedAt': datetime.now().isoformat()
            }

            eta_collection.insert_one(eta_pred)

        logger.info(f'Processed location for Bus {bus_data["busId"]}')


if __name__ == "__main__":
    process_bus_location()
