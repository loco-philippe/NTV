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

_DUR_S = "([0-9]+S)"
_DUR_N = '(' + '([0-9]+M)' + _DUR_S + '?)'
_DUR_H = '(' + '([0-9]+H)' + _DUR_N + '?)'
_DUR_TIME = '(T(' + _DUR_H + '|' + _DUR_N + '|' + _DUR_S + '))'
_DUR_D = "([0-9]+D)"
_DUR_M = '(' + '([0-9]+M)' + _DUR_D + '?)'
_DUR_Y = '(' + '([0-9]+Y)' + _DUR_M + '?)'
_DUR_DATE = '((' + _DUR_D + '|'+_DUR_M + '|' + \
    _DUR_Y + ')(' + _DUR_TIME + ')?)'
_DUR_WEEK = '([0-9]+W)'
DURATION = re.compile('P('+_DUR_DATE+'|'+_DUR_TIME+'|'+_DUR_WEEK+')')
GEOJSON = {'Point': 'coordinates', 'LineString': 'coordinates',
           'Polygon': 'coordinates', 'MultiPoint': 'coordinates',
           'MultiLineString': 'coordinates', 'MultiPolygon': 'coordinates',
           'GeometryCollection': 'geometries', 'Feature': 'geometry',
           'FeatureCollection': 'features'}
OLC = re.compile(
    r'([2-90CFGHJMPQRVWX]{2}){4}\+([2-9CFGHJMPQRVWX]{2}[2-9CFGHJMPQRVWX]*)?')
URI = re.compile(r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
UUID = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                  flags=re.IGNORECASE)
_DOC_ATOM = r'(\s*[a-zA-Z0-9!#\$%&\*\+-/=\^_`{}\|~.]+)'
_QUOTED_STRING = r'(\s*"[\s*[!#-~]*]*\s*"\s*)'
_DOMAIN_LITERAL = r'(\s*\[(\s*[!-Z^-~]+)*\s*\]\s*)'
_ADDR_SPEC = '((' + _DOC_ATOM + '|' + _QUOTED_STRING + \
    ')@(' + _DOC_ATOM + '|' + _DOMAIN_LITERAL + '))'
_MAILBOX = r'((.*\s*\<' + _ADDR_SPEC + r'\>\s*)|' + _ADDR_SPEC + ')'
ADDRESS = re.compile(
    _MAILBOX + '|(.*:(' + _MAILBOX + '(,' + _MAILBOX + r')*)?;\s*)')  # without CFWS
HOSTNAME = re.compile(r'[-a-zA-Z_]{1,63}(\.[-a-zA-Z_]{1,63})*')
IPV4 = re.compile(
    r'(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])')
_PATH_ABSOLUTE = r'(([a-zA-Z]:)?((/([-a-z0-9_~!&,;=:@\.\$\'\(\)\*\+]|(%[a-f0-9]{2}))*)*))'
FILE = re.compile(r'/*[-a-z0-9_~!&,;=:@\.\$\'\(\)\*\+]*' + _PATH_ABSOLUTE)


class Validator:
    '''Validator class contains static methods.
    Each method is associated to a global Datatype (name before the _) and
    return a boolean (type conformity).'''

    @staticmethod
    def json_valid(val):
        '''validate method'''
        return isinstance(val, (float, int, str, dict, list, bool)) or val is None

    @staticmethod
    def number_valid(val):
        '''validate method'''
        return isinstance(val, (float, int))

    @staticmethod
    def boolean_valid(val):
        '''validate method'''
        return isinstance(val, bool)

    @staticmethod
    def null_valid(val):
        '''validate method'''
        return val is None

    @staticmethod
    def string_valid(val):
        '''validate method'''
        return isinstance(val, str)

    @staticmethod
    def array_valid(val):
        '''validate method'''
        return isinstance(val, list)

    @staticmethod
    def object_valid(val):
        '''validate method'''
        return isinstance(val, dict)

    @staticmethod
    def int_valid(val):
        '''validate method'''
        return isinstance(val, int)

    @staticmethod
    def int8_valid(val):
        '''validate method'''
        return isinstance(val, int) and -128 <= val <= 127

    @staticmethod
    def int16_valid(val):
        '''validate method'''
        return isinstance(val, int) and -32768 <= val <= 32767

    @staticmethod
    def int32_valid(val):
        '''validate method'''
        return isinstance(val, int) and -2147483648 <= val <= 2147483647

    @staticmethod
    def int64_valid(val):
        '''validate method'''
        return isinstance(val, int) and -2 ^ 63 <= val <= 2 ^ 63

    @staticmethod
    def uint8_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val <= 255

    @staticmethod
    def uint16_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val <= 65535

    @staticmethod
    def uint32_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val <= 4294967295

    @staticmethod
    def uint64_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val <= 2 ^ 64 - 1

    @staticmethod
    def float_valid(val):
        '''validate method'''
        return isinstance(val, float)

    @staticmethod
    def float16_valid(val):
        '''validate method'''
        return isinstance(val, float) and abs(val) <= 65500

    @staticmethod
    def float32_valid(val):
        '''validate method'''
        return isinstance(val, float) and abs(val) <= 3.4028237E38

    @staticmethod
    def float64_valid(val):
        '''validate method'''
        return isinstance(val, float)

    @staticmethod
    def decimal64_valid(val):
        '''validate method'''
        return isinstance(val, float)

    @staticmethod
    def bit_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return val in ['0', '1']

    @staticmethod
    def binary_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        for char in val:
            if not char in ['0', '1']:
                return False
        return True

    @staticmethod
    def base64_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        for car in val:
            if (not 'a' <= car <= 'z' and not 'A' <= car <= 'Z' and
                    not '0' <= car <= '9' and not car in ['-', '_', '=']):
                return False
        return True

    @staticmethod
    def base32_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        for car in val:
            if not 'A' <= car <= 'Z' and not '1' < car < '8' and not car == '=':
                return False
        return True

    @staticmethod
    def base16_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        for car in val:
            if not '0' <= car <= '9' and not 'A' <= car <= 'F':
                return False
        return True

    @staticmethod
    def year_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val

    @staticmethod
    def month_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 < val < 13

    @staticmethod
    def yearmonth_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        y_m = val.split('-', maxsplit=1)
        return Validator.year_valid(int(y_m[0])) and Validator.month_valid(int(y_m[1]))

    @staticmethod
    def week_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 < val < 54

    @staticmethod
    def day_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 < val < 32

    @staticmethod
    def wday_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 < val < 8

    @staticmethod
    def yday_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 < val < 367

    @staticmethod
    def hour_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val < 13

    @staticmethod
    def minute_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val < 60

    @staticmethod
    def second_valid(val):
        '''validate method'''
        return isinstance(val, int) and 0 <= val < 60

    @staticmethod
    def dat_valid(val):
        '''validate method'''
        return (Validator.date_valid(val) or Validator.time_valid(val) or
                Validator.datetime_valid(val) or Validator.timetz_valid(val) or
                Validator.datetimetz_valid(val))

    @staticmethod
    def date_valid(val):
        '''validate method'''
        try:
            datetime.date.fromisoformat(val)
        except ValueError:
            return False
        return True

    @staticmethod
    def time_valid(val):
        '''validate method'''
        try:
            tim = datetime.time.fromisoformat(val)
        except ValueError:
            return False
        # return True if not tim.tzinfo else False
        return bool(not tim.tzinfo)

    @staticmethod
    def timetz_valid(val):
        '''validate method'''
        try:
            tim = datetime.time.fromisoformat(val)
        except ValueError:
            return False
        # return True if tim.tzinfo else False
        return bool(tim.tzinfo)

    @staticmethod
    def datetime_valid(val):
        '''validate method'''
        try:
            tim = datetime.datetime.fromisoformat(val)
        except ValueError:
            return False
        # return True if not tim.tzinfo else False
        return bool(not tim.tzinfo)

    @staticmethod
    def datetimetz_valid(val):
        '''validate method'''
        try:
            tim = datetime.datetime.fromisoformat(val)
        except ValueError:
            return False
        # return True if tim.tzinfo else False
        return bool(tim.tzinfo)

    @staticmethod
    def duration_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return DURATION.fullmatch(val) is not None

    @staticmethod
    def period_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        period = val.split('/', maxsplit=1)
        for per in period:
            if not (Validator.datetime_valid(per) or
                    Validator.datetimetz_valid(per) or
                    Validator.duration_valid(per)):
                return False
        if period[0][0] == 'P' and period[1][0] == 'P':
            return False
        return True

    @staticmethod
    def timearray_valid(val):
        '''validate method'''
        return (isinstance(val, list) and len(val) == 2 and
                Validator.dat_valid(val[0]) and Validator.dat_valid(val[1]))

    @staticmethod
    def point_valid(val):
        '''validate method'''
        return (isinstance(val, list) and len(val) == 2 and
                isinstance(val[0], (int, float)) and -180 <= val[0] <= 180 and
                isinstance(val[1], (int, float)) and -180 <= val[1] <= 180)

    @staticmethod
    def pointstr_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        coord = val.split(',', maxsplit=1)
        if len(coord) != 2:
            return False
        try:
            point = [float(coord[0]), float(coord[1])]
        except ValueError:
            return False
        return Validator.point_valid(point)

    @staticmethod
    def pointobj_valid(val):
        '''validate method'''
        if not (isinstance(val, dict) and 'lon' in val and 'lat' in val):
            return False
        return Validator.point_valid([val['lon'], val['lat']])

    @staticmethod
    def multipoint_valid(val):
        '''validate method'''
        if not isinstance(val, list):
            return False
        for point in val:
            if not Validator.point_valid(point):
                return False
        return True

    @staticmethod
    def line_valid(val):
        '''validate method'''
        return Validator.multipoint_valid(val)

    @staticmethod
    def multiline_valid(val):
        '''validate method'''
        if not isinstance(val, list):
            return False
        for line in val:
            if not Validator.multipoint_valid(line):
                return False
        return True

    @staticmethod
    def polygon_valid(val):
        '''validate method'''
        return Validator.multiline_valid(val)

    @staticmethod
    def multipolygon_valid(val):
        '''validate method'''
        if not isinstance(val, list):
            return False
        for poly in val:
            if not Validator.multiline_valid(poly):
                return False
        return True

    @staticmethod
    def geometry_valid(val):
        '''validate method'''
        return (Validator.point_valid(val) or Validator.line_valid(val) or
                Validator.polygon_valid(val))

    @staticmethod
    def multigeometry_valid(val):
        '''validate method'''
        if not isinstance(val, list):
            return False
        for geo in val:
            if not Validator.geometry_valid(geo):
                return False
        return True

    @staticmethod
    def box_valid(val):
        '''validate method'''
        if not (isinstance(val, list) and len(val) == 4):
            return False
        for coor in val:
            if not (isinstance(coor, (int, float)) and -90 <= coor <= 90):
                return False
        return True

    @staticmethod
    def geojson_valid(val):
        '''validate method'''
        if not (isinstance(val, dict) and 'type' in val):
            return False
        return val['type'] in GEOJSON and GEOJSON[val['type']] in val

    @staticmethod
    def codeolc_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return OLC.fullmatch(val) is not None

    @staticmethod
    def loc_valid(val):
        '''validate method'''
        return (Validator.point_valid(val) or Validator.pointstr_valid(val) or
                Validator.pointobj_valid(val) or Validator.line_valid(val) or
                Validator.polygon_valid(val) or Validator.multipolygon_valid(val) or
                Validator.box_valid(val) or Validator.geojson_valid(val) or
                Validator.codeolc_valid(val))

    @staticmethod
    def unit_valid(val):
        '''validate method'''
        return isinstance(val, str)

    @staticmethod
    def uri_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    @staticmethod
    def uriref_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    @staticmethod
    def iri_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    @staticmethod
    def iriref_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    @staticmethod
    def uritem_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    @staticmethod
    def uuid_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return UUID.fullmatch(val) is not None

    @staticmethod
    def email_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return ADDRESS.fullmatch(val) is not None

    @staticmethod
    def hostname_valid(val):
        '''validate method'''
        if not isinstance(val, str) or len(val) > 253:
            return False
        return HOSTNAME.fullmatch(val) is not None

    @staticmethod
    def jpointer_valid(val):
        '''validate method'''
        if not isinstance(val, str) or (len(val) > 0 and val[0] != '/'):
            return False
        return True

    @staticmethod
    def ipv4_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return IPV4.fullmatch(val) is not None

    @staticmethod
    def file_valid(val):
        '''validate method'''
        if not isinstance(val, str):
            return False
        return FILE.fullmatch(val) is not None

    @staticmethod
    def ipv6_valid(val):
        '''validate method'''

    @staticmethod
    def idnemail_valid(val):
        '''validate method'''

    @staticmethod
    def idnhostname_valid(val):
        '''validate method'''

    @staticmethod
    def rjpointer_valid(val):
        '''validate method'''

    @staticmethod
    def regex_valid(val):
        '''validate method'''

    @staticmethod
    def row_valid(val):
        '''validate method'''

    @staticmethod
    def tab_valid(val):
        '''validate method'''

    @staticmethod
    def field_valid(val):
        '''validate method'''

    @staticmethod
    def ntv_valid(val):
        '''validate method'''

    @staticmethod
    def sch_valid(val):
        '''validate method'''

    @staticmethod
    def narray_valid(val):
        '''validate method'''

    @staticmethod
    def ndarray_valid(val):
        '''validate method'''

    @staticmethod
    def xndarray_valid(val):
        '''validate method'''

    @staticmethod
    def xdataset_valid(val):
        '''validate method'''


class ValidateError(Exception):
    '''Validator exception'''
