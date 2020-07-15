# _*_ coding: UTF-8 _*_

class Entity(object):
    def __init__(self, params):
        self.name = params['name']
        self.type = params['type']
        self.start = params['start']
        self.end = params['end']

    @property
    def length(self):
        return self.end - self.start + 1

    def as_ner_dict(self):
        return {
            "start": self.start,
            "end": self.end,
            "value": self.name,
            "entity": self.type,
        }
