from json import JSONEncoder


class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set): 
            return list(obj) 
        return obj.__dict__