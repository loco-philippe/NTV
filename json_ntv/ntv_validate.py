# -*- coding: utf-8 -*-
"""
@author: Philippe@loco-labs.io

The `ntv_validate` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the `Validator` class.

Function in Validator class are Datatype.validate overloading for each subclass.

For more information, see the 
[user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html) 
or the [github repository](https://github.com/loco-philippe/NTV).
"""
import datetime
import re

def duration(): 
    dur_s = "([0-9]+S)"
    dur_n = '(' + '([0-9]+M)' + dur_s + '?)'
    dur_h = '(' + '([0-9]+H)' + dur_n + '?)'
    dur_time = '(T(' + dur_h + '|' + dur_n + '|' + dur_s + '))'
    dur_d = "([0-9]+D)"
    dur_m = '(' + '([0-9]+M)' + dur_d + '?)'
    dur_y = '(' + '([0-9]+Y)' + dur_m + '?)'
    dur_date = '((' + dur_d + '|' + dur_m + '|' + dur_y + ')(' + dur_time + ')?)'
    dur_week = '([0-9]+W)'
    duration = 'P(' + dur_date + '|' + dur_time + '|' + dur_week + ')$'
    return re.compile(duration)

DURATION = duration()


class Validator:
    
    def json_valid(val):
        return isinstance(val, (float, int, str, dict, list, bool)) or val is None

    def number_valid(val):
        return isinstance(val, (float, int))

    def boolean_valid(val):
        return isinstance(val, bool)

    def null_valid(val):
        return val is None
    
    def string_valid(val):
        return isinstance(val, str)

    def array_valid(val):
        return isinstance(val, list)

    def object_valid(val):
        return isinstance(val, dict)

    def int_valid(val):
        return isinstance(val, int)

    def int8_valid(val):
        return isinstance(val, int) and -128 <= val <= 127
 
    def int16_valid(val):
        return isinstance(val, int) and -32768 <= val <= 32767
 
    def int32_valid(val):
        return isinstance(val, int) and -2147483648 <= val <= 2147483647
 
    def int64_valid(val):
        return isinstance(val, int) and -2^63 <= val <= 2^63
 
    def uint8_valid(val):
        return isinstance(val, int) and 0 <= val <= 255
 
    def uint16_valid(val):
        return isinstance(val, int) and 0 <= val <= 65535
 
    def uint32_valid(val):
        return isinstance(val, int) and 0 <= val <= 4294967295
 
    def uint64_valid(val):
        return isinstance(val, int) and 0 <= val <= 2^64 - 1

    def float_valid(val):
        return isinstance(val, float)

    def float16_valid(val):
        return isinstance(val, float) and abs(val) <= 65500

    def float32_valid(val):
        return isinstance(val, float) and abs(val) <= 3.4028237E38

    def float64_valid(val):
        return isinstance(val, float)

    def decimal64_valid(val):
        return isinstance(val, float)    

    def bit_valid(val):
        return val in ['0', '1']

    def binary_valid(val):
        for char in val: 
            if not char in ['0', '1']:
                return False
        return True
    
    def base64_valid(val):
        for car in val: 
            if (not 'a' <= car <= 'z' and not 'A' <= car <= 'Z' and 
                not '0' <= car <= '9' and not car in ['-', '_', '=']):
                return False
        return True

    def base32_valid(val):
        for car in val: 
            if not 'A' <= car <= 'Z' and not '1' < car < '8' and not car == '=':
                return False
        return True

    def base16_valid(val):
        for car in val: 
            if not '0' <= car <= '9' and not 'A' <= car <= 'F':
                return False
        return True
     
    def year_valid(val):
        return isinstance(val, int) and 0 <= val    

    def month_valid(val):
        return isinstance(val, int) and 0 < val < 13

    def yearmonth_valid(val):
        y_m = val.split('-', maxsplit=1)
        return Validator.year_valid(int(y_m[0])) and Validator.month_valid(int(y_m[1]))
    
    def week_valid(val):
        return isinstance(val, int) and 0 < val < 54
    
    def day_valid(val):
        return isinstance(val, int) and 0 < val < 32
    
    def wday_valid(val):
        return isinstance(val, int) and 0 < val < 8
        
    def yday_valid(val):
        return isinstance(val, int) and 0 < val < 367
    
    def hour_valid(val):
        return isinstance(val, int) and 0 <= val < 13
    
    def minute_valid(val):
        return isinstance(val, int) and 0 <= val < 60

    def second_valid(val):
        return isinstance(val, int) and 0 <= val < 60
    
    def date_valid(val):
        try:
            datetime.date.fromisoformat(val)
        except ValueError:
            return False
        return True

    def time_valid(val):
        try:
            tim = datetime.time.fromisoformat(val)
        except ValueError:
            return False
        return True if not tim.tzinfo else False

    def timetz_valid(val):
        try:
            tim = datetime.time.fromisoformat(val)
        except ValueError:
            return False
        return True if tim.tzinfo else False

    def datetime_valid(val):
        try:
            tim = datetime.datetime.fromisoformat(val)
        except ValueError:
            return False
        return True if not tim.tzinfo else False

    def datetimetz_valid(val):
        try:
            tim = datetime.datetime.fromisoformat(val)
        except ValueError:
            return False
        return True if tim.tzinfo else False

    def duration_valid(val):
        return DURATION.match(val) is not None

    def period_valid(val):
        period = val.split('/', maxsplit=1)
        for per in period:
            if (not Validator.datetime_valid(per) and 
                not Validator.datetimetz_valid(per) and
                not Validator.duration_valid(per)):
                return False
        return True

class ValidateError(Exception):
    '''Validator exception'''    
    