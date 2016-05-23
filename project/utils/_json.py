from json import *
import json
import datetime
import decimal

class JSONEncoderEx(json.JSONEncoder):

    def default(self, obj):
        print('Used with {}'.format(obj))
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def dumps(obj, skipkeys=False, ensure_ascii=False, check_circular=True, allow_nan=True, cls=JSONEncoderEx, indent=None, separators=None, default=None, sort_keys=False, **kw):
    return json.dumps(obj,
        skipkeys=skipkeys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        cls=cls,
        indent=indent,
        separators=separators,
        default=default,
        sort_keys=sort_keys,
        **kw)