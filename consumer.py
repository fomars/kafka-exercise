import os

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "website_availability",
    auto_offset_reset="earliest",
    bootstrap_servers=os.getenv('SERVICE_URI'),
    # client_id="demo-client-1",
    group_id="cons1",
    security_protocol="SSL",
    ssl_cafile="ca.pem",
    ssl_certfile="service.cert",
    ssl_keyfile="service.key",
)

# Call poll twice. First call will just assign partitions for our
# consumer without actually returning anything

for _ in range(2):
    raw_msgs = consumer.poll(timeout_ms=1000)
    for tp, msgs in raw_msgs.items():
        for msg in msgs:
            print("Received: {}".format(msg.value))

# Commit offsets so we won't get the same messages again

consumer.commit()
