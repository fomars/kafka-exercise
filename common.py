import pickle
from collections import namedtuple

BaseData = namedtuple('Data', ['url', 'ts', 'response_time_ms', 'http_code', 'regex_matches'])


class Data(BaseData):
    def dumps(self):
        return pickle.dumps(self)

    @classmethod
    def loads(cls, string):
        return cls(*pickle.loads(string))
