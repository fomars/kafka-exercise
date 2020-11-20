import argparse
import json
import os
import re
import signal
import time
from queue import Queue, Empty
from threading import Thread, Event

import requests
from kafka import KafkaProducer

from common import Data


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
            data = queue.get(timeout=period)
        except Empty:
            continue
        if data is not None:  # use None to terminate thread
            print(f'Sending {data}')
            producer.send('website_availability', data.dumps())
            producer.flush()
        else:
            break


def get_scheduler(period):
    t = time.time()
    while True:
        yield t
        t += period


class Poller(Thread):
    def __init__(self, url, timeout, scheduler, stop_event, queue, regex=None):
        """
        :type queue: Queue
        :type regex: str
        :type url: str
        :type scheduler: generator
        :type stop_event: Event
        """
        super().__init__()
        self.url = url if url.startswith('http') else f'http://{url}'
        self.timeout = timeout
        self.scheduler = scheduler
        self.stop_event = stop_event
        self.results_queue = queue
        self.regex_b = regex.encode('utf-8') if regex else None

    def run(self):
        while not self.stop_event.is_set():
            start_time = next(self.scheduler)
            while time.time() < start_time:
                if not self.stop_event.is_set():
                    pass
                else:
                    return
            self.results_queue.put(self.check_website())

    def check_website(self):
        """

        :rtype: Data
        """
        ts = time.time()
        try:
            resp = requests.get(self.url, timeout=self.timeout)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return Data(self.url, ts,
                        int((time.time() - ts) * 1000),
                        0, False)  # zero http code - a convention for ConnectionError
        return Data(self.url, ts,
                    int(resp.elapsed.total_seconds() * 1000),
                    resp.status_code,
                    re.search(self.regex_b, resp.content) is not None if self.regex_b else False)


def set_interrupt_handler(stop_event, pollers, queue, results_sender):
    def interrupt_handler(signum, frame):
        print('Signal handler called with signal', signum)
        stop_event.set()
        for poller in pollers:
            poller.join()
        queue.put(None)  # use None to terminate results sender thread
        results_sender.join()

    signal.signal(signal.SIGINT, interrupt_handler),
    signal.signal(signal.SIGTERM, interrupt_handler)


def main(url, period, timeout, regex):
    results_queue = Queue()
    stop = Event()
    results_sender = Thread(target=kafka_producer, args=(results_queue, period))
    results_sender.start()
    scheduler = get_scheduler(period)

    # should have enough pollers to keep poll period constant even if target url times out
    pollers_number = timeout // period or 1
    pollers = [Poller(url, timeout, scheduler, stop, results_queue, regex) for i in
               range(pollers_number)]

    set_interrupt_handler(stop, pollers, results_queue, results_sender)

    for poller in pollers:
        poller.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-p', '--period', type=int, help='Poll period in seconds', default=2)
    parser.add_argument('-t', '--timeout', type=int, help='Timeout in seconds', default=10)
    parser.add_argument('-r', '--regex')
    args = parser.parse_args()
    main(args.url, args.period, args.timeout, args.regex)
