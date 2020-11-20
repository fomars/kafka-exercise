import os
import sys

from kafka import KafkaConsumer

from .common import Data, env_check
from .db_adapter import insert_data


def get_kafka_consumer():
    return KafkaConsumer(
        "website_availability",
        auto_offset_reset="earliest",
        bootstrap_servers=os.getenv('SERVICE_URI'),
        group_id="cons1",
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )


def main():
    env_check('SERVICE_URI')
    env_check('DB_URL')
    consumer = get_kafka_consumer()
    while True:
        try:
            for _ in range(2):
                raw_msgs = consumer.poll(timeout_ms=1000)
                for tp, msgs in raw_msgs.items():
                    for msg in msgs:
                        data = Data.loads(msg.value)
                        print(f"Received: {data}")
                        insert_data(data)
            consumer.commit()
            sys.stdout.write('.')
            sys.stdout.flush()
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()


