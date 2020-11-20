# from psycopg2.extras import RealDictCursor
import os

import psycopg2
from contextlib import closing

uri = os.getenv('DB_URL')


def insert_data(data):
    """
    :type data: Data
    """
    with closing(psycopg2.connect(uri, sslrootcert='ca_pg.pem')) as conn:
        with conn.cursor() as cursor:
            # create website record
            cursor.execute(f"insert into website(url) values ('{data.url}') on conflict do nothing;")
            # create availability_data record
            cursor.execute(f"insert into availability_data(ts, website_id, response_time, http_code, regex_matches) values \
            (to_timestamp({data.ts}), \
            (select id from website where url='{data.url}'), \
            {data.response_time_ms}, \
            {data.http_code}, \
            {str(data.regex_matches).lower()});")
        conn.commit()
