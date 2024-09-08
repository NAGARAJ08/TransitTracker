import time
import json
import uuid
import logging
from datetime import datetime
from kafka import KafkaProducer


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

# this is predefined route - basically lat long

# each cordintaes define the starting  point , stops and endpoint
BUS_ROUTE = [
    (40.7128, -74.0060),
    (40.7150, -74.0080),
    (40.7170, -74.0100),
    (40.7190, -74.0120),
    (40.7210, -74.0140),
]


def give_position(start, end, progress):

    return (
        start[0] + (end[0]-start[0]) * progress,
        start[1] + (end[1]-start[1]) * progress,
    )


def simulate_bus_movement():

    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # just defining only one bus with an id

    bus_id = "111"
    route_progress = 0
    current_position = 0

    while True:

        start = BUS_ROUTE[current_position]
        end = BUS_ROUTE[current_position+1]
        position = give_position(start, end, route_progress)

        message = {

            'busId': bus_id,
            'latitude': position[0],
            'longitude': position[1],
            'timestamp': datetime.now().isoformat()
        }
        try:
            producer.send('busLocations', message)
            logger.info(f"sent : {message}")
        except Exception as e:
            logger.error("exception occured in kafka producer")

        # we will update the progress

        route_progress += 0.1

        if route_progress > 1:
            current_position += 1
            route_progress = 0

        if current_position >= len(BUS_ROUTE) - 1:
            current_position = 0

        time.sleep(5)


if __name__ == '__main__':
    simulate_bus_movement()
