import argparse
import json
import os
import re
import time
from queue import Queue, Empty
from threading import Thread, Event

import requests
from kafka import KafkaProducer


def kafka_producer(queue, period):
    """
    :type period: int
    :type queue: Queue
    """
    producer = KafkaProducer(
        bootstrap_servers=os.getenv('SERVICE_URI'),
        security_protocol='SSL',
        ssl_cafile='ca.pem',
        ssl_certfile='service.cert',
        ssl_keyfile='service.key',
    )
    while True:
        try:
            message = queue.get(timeout=period)
        except Empty:
            continue
        if message is not None:
            print('Sending {}'.format(message))
            producer.send('website_availability', message.encode('utf-8'))
            producer.flush()
        else:
            break


def check_website(url, regex):
    """
    :type regex: str
    :type url: str
    """
    if not url.startswith('http'):
        url = f'http://{url}'
    resp = requests.get(url)
    return {'ts': time.time(),
            'response_time_ms': resp.elapsed.total_seconds() * 1000,
            'http_code': resp.status_code,
            'regex_matches': re.findall(regex.encode('utf-8'), resp.content)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-p', '--period', type=int, help='Poll period in seconds', default=2)
    parser.add_argument('-r', '--regex')
    args = parser.parse_args()

    results_queue = Queue()
    stop_event = Event()
    results_sender = Thread(target=kafka_producer, args=(results_queue, args.period))
    results_sender.start()

    start = time.time()
    while True:
        try:
            if time.time() >= start:
                results_queue.put(json.dumps(check_website(args.url, args.regex)))
                remainder = args.period - (time.time() - start)
                start += args.period
            else:
                continue
        except KeyboardInterrupt:
            results_queue.put(None)
            break
        except requests.exceptions.ConnectionError:
            results_queue.put(None)
            raise
