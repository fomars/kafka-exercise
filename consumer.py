import os

from kafka import KafkaConsumer

from common import Data
from db_adapter import insert_data

consumer = KafkaConsumer(
    "website_availability",
    auto_offset_reset="earliest",
    bootstrap_servers=os.getenv('SERVICE_URI'),
    group_id="cons1",
    security_protocol="SSL",
    ssl_cafile="ca.pem",
    ssl_certfile="service.cert",
    ssl_keyfile="service.key",
)

# Call poll twice. First call will just assign partitions for our
# consumer without actually returning anything
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
        print('.', end='')
    except KeyboardInterrupt:
        break


# Commit offsets so we won't get the same messages again


