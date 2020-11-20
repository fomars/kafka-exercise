import os
import pickle
from collections import namedtuple

BaseData = namedtuple('Data', ['url', 'ts', 'response_time_ms', 'http_code', 'regex_matches'])


def env_check(var_name='SERVICE_URI'):
    assert os.getenv(var_name) is not None, 'You must set SERVICE_URI environment variable'

class Data(BaseData):
    def dumps(self):
        return pickle.dumps(self)

    @classmethod
    def loads(cls, string):
        return cls(*pickle.loads(string))
