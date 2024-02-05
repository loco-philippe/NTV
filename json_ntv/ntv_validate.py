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

_dur_s = "([0-9]+S)"
_dur_n = '(' + '([0-9]+M)' + _dur_s + '?)'
_dur_h = '(' + '([0-9]+H)' + _dur_n + '?)'
_dur_time = '(T(' + _dur_h + '|' + _dur_n + '|' + _dur_s + '))'
_dur_d = "([0-9]+D)"
_dur_m = '(' + '([0-9]+M)' + _dur_d + '?)'
_dur_y = '(' + '([0-9]+Y)' + _dur_m + '?)'
_dur_date = '(('+ _dur_d + '|'+_dur_m + '|'+ _dur_y + ')('+ _dur_time + ')?)'
_dur_week = '([0-9]+W)'
DURATION = re.compile('P('+_dur_date+'|'+_dur_time+'|'+_dur_week+')')
GEOJSON = {'Point': 'coordinates', 'LineString': 'coordinates', 
           'Polygon': 'coordinates', 'MultiPoint': 'coordinates', 
           'MultiLineString': 'coordinates', 'MultiPolygon': 'coordinates', 
           'GeometryCollection': 'geometries', 'Feature': 'geometry', 
           'FeatureCollection': 'features'}
OLC = re.compile('([2-90CFGHJMPQRVWX]{2}){4}\+([2-9CFGHJMPQRVWX]{2}[2-9CFGHJMPQRVWX]*)?')
URI = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
UUID = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                  flags=re.IGNORECASE)
_dot_atom = r'(\s*[a-zA-Z0-9!#\$%&\*\+-/=\^_`{}\|~.]+)'
_quoted_string = r'(\s*"[\s*[!#-~]*]*\s*"\s*)'
_domain_literal = r'(\s*\[(\s*[!-Z^-~]+)*\s*\]\s*)'
_addr_spec = '((' + _dot_atom + '|' + _quoted_string + ')@(' + _dot_atom + '|' + _domain_literal + '))'
_mailbox = r'((.*\s*\<' + _addr_spec + r'\>\s*)|' + _addr_spec + ')'
ADDRESS = re.compile(_mailbox + '|(.*:(' + _mailbox + '(,' + _mailbox + r')*)?;\s*)') # without CFWS
HOSTNAME = re.compile(r'[-a-zA-Z_]{1,63}(\.[-a-zA-Z_]{1,63})*')
IPV4 = re.compile('(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])')
_path_absolute = r'(([a-zA-Z]:)?((/([-a-z0-9_~!&,;=:@\.\$\'\(\)\*\+]|(%[a-f0-9]{2}))*)*))'

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
        if not isinstance(val, str):
            return False
        return val in ['0', '1']

    def binary_valid(val):
        if not isinstance(val, str):
            return False
        for char in val: 
            if not char in ['0', '1']:
                return False
        return True
    
    def base64_valid(val):
        if not isinstance(val, str):
            return False
        for car in val: 
            if (not 'a' <= car <= 'z' and not 'A' <= car <= 'Z' and 
                not '0' <= car <= '9' and not car in ['-', '_', '=']):
                return False
        return True

    def base32_valid(val):
        if not isinstance(val, str):
            return False
        for car in val: 
            if not 'A' <= car <= 'Z' and not '1' < car < '8' and not car == '=':
                return False
        return True

    def base16_valid(val):
        if not isinstance(val, str):
            return False
        for car in val: 
            if not '0' <= car <= '9' and not 'A' <= car <= 'F':
                return False
        return True
     
    def year_valid(val):
        return isinstance(val, int) and 0 <= val    

    def month_valid(val):
        return isinstance(val, int) and 0 < val < 13

    def yearmonth_valid(val):
        if not isinstance(val, str):
            return False
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
    
    def dat_valid(val):
        return (Validator.date_valid(val) or Validator.time_valid(val) or 
                Validator.datetime_valid(val) or Validator.timetz_valid(val) or
                Validator.datetimetz_valid(val))
    
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
        if not isinstance(val, str):
            return False
        return DURATION.fullmatch(val) is not None

    def period_valid(val):
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

    def timearray_valid(val):
        return (isinstance(val, list) and len(val) == 2 and 
                Validator.dat_valid(val[0]) and Validator.dat_valid(val[1]))
    
    def point_valid(val):
        return (isinstance(val, list) and len(val) == 2 and 
                isinstance(val[0], (int,float)) and -180 <= val[0] <= 180 and
                isinstance(val[1], (int,float)) and -180 <= val[1] <= 180)

    def pointstr_valid(val):
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

    def pointobj_valid(val):
        if not (isinstance(val, dict) and 'lon' in val and 'lat' in val):
            return False
        return Validator.point_valid([val['lon'], val['lat']])        

    def multipoint_valid(val):
        if not isinstance(val, list):
            return False
        for point in val:
            if not Validator.point_valid(point):
                return False
        return True

    def line_valid(val):
        return Validator.multipoint_valid(val)

    def multiline_valid(val):
        if not isinstance(val, list):
            return False
        for line in val:
            if not Validator.multipoint_valid(line):
                return False
        return True
 
    def polygon_valid(val):
        return Validator.multiline_valid(val)    
    
    def multipolygon_valid(val):
        if not isinstance(val, list):
            return False
        for poly in val:
            if not Validator.multiline_valid(poly):
                return False
        return True    

    def geometry_valid(val):
        return (Validator.point_valid(val) or Validator.line_valid(val) or 
                Validator.polygon_valid(val))    

    def multigeometry_valid(val):
        if not isinstance(val, list):
            return False
        for geo in val:
            if not Validator.geometry_valid(geo):
                return False
        return True

    def box_valid(val):
        if not (isinstance(val, list) and len(val) == 4):
            return False
        for coor in val:
            if not (isinstance(coor, (int,float)) and -90 <= coor <= 90):
                return False 
        return True        
    
    def geojson_valid(val):
        if not (isinstance(val, dict) and 'type' in val):
            return False
        return val['type'] in GEOJSON and GEOJSON[val['type']] in val

    def codeolc_valid(val):
        if not isinstance(val, str):
            return False
        return OLC.fullmatch(val) is not None

    def uri_valid(val):
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    def uriref_valid(val):
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None
    
    def iri_valid(val):
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None

    def iriref_valid(val):
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None
    
    def uritem_valid(val):
        if not isinstance(val, str):
            return False
        return URI.fullmatch(val) is not None
    
    def uuid_valid(val):
        if not isinstance(val, str):
            return False
        return UUID.fullmatch(val) is not None

    def email_valid(val):
        if not isinstance(val, str):
            return False
        return ADDRESS.fullmatch(val) is not None    
    
    def hostname_valid(val):
        if not isinstance(val, str) or len(val) > 253:
            return False
        return HOSTNAME.fullmatch(val) is not None    
    
    def jpointer_valid(val):
        if not isinstance(val, str) or (len(val) > 0 and val[0] != '/'):
            return False
        return True  

    def ipv4_valid(val):
        if not isinstance(val, str):
            return False
        return IPV4.fullmatch(val) is not None        
    
class ValidateError(Exception):
    '''Validator exception'''    
    
    
    
"""
_IPv6_1_R_H16 = '(([0-9a-f]{1,4})\:){6,6}((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_2_R_H16 = '\:\:(([0-9a-f]{1,4})\:){5,5}((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_3_L_H16 = '([0-9a-f]{1,4})?\:\:(([0-9a-f]{1,4})\:){4,4}((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_4_L_H16_REPEAT = '((([0-9a-f]{1,4})\:)?([0-9a-f]{1,4}))?\:\:(([0-9a-f]{1,4})\:){3,3}((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_5_L_H16_REPEAT = '((([0-9a-f]{1,4})\:){0,2}([0-9a-f]{1,4}))?\:\:(([0-9a-f]{1,4})\:){2,2}((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_6_L_H16_REPEAT = '((([0-9a-f]{1,4})\:){0,3}([0-9a-f]{1,4}))?\:\:([0-9a-f]{1,4})\:((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_7_L_H16_REPEAT = '((([0-9a-f]{1,4})\:){0,4}([0-9a-f]{1,4}))?\:\:((([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])|([0-9a-f]{1,4})\:([0-9a-f]{1,4}))'
_IPV6_8_L_H16_REPEAT = '((([0-9a-f]{1,4})\:){0,5}([0-9a-f]{1,4}))?\:\:([0-9a-f]{1,4})'
_IPV6_9_L_H16_REPEAT = '((([0-9a-f]{1,4})\:){0,6}([0-9a-f]{1,4}))?\:\:'
_ipv6 = '(' + _IPv6_1_R_H16 + '|' + _IPV6_2_R_H16 + '|' + _IPV6_3_L_H16 + '|' + \
        _IPV6_4_L_H16_REPEAT + '|' + _IPV6_5_L_H16_REPEAT + '|' + _IPV6_6_L_H16_REPEAT + \
        '|' + _IPV6_7_L_H16_REPEAT + '|' + _IPV6_8_L_H16_REPEAT + '|' + _IPV6_9_L_H16_REPEAT + ')'
_scheme = '([a-z][a-z0-9\+\-\.]*)'
_userinfo = '(((\%[0-9a-f][0-9a-f]|[a-z0-9\-\.\_\~]|[\!\$\&\'\(\)\*\+\,\;\=]|\:)*)\@)'
_fragment = '(#([a-z0-9\-\.\_\~\!\$\&\'\(\)\*\+\,\;\=\:\@\/\?]|(%[a-f0-9]{2,2}))*)'
_query = '(\?([a-z0-9\-\.\_\~\!\$\&\'\(\)\*\+\,\;\=\:\@\/\?]|(%[a-f0-9]{2,2}))*)'
_path = '((\/([a-z0-9\-\.\_\~\!\$\&\'\(\)\*\+\,\;\=\:\@]|(%[a-f0-9]{2,2}))*)*)'
_port = '(:([0-9]+))'
_regname = '([a-z0-9\-\.\_\~]|\%[0-9a-f][0-9a-f]|[\!\$\&\'\(\)\*\+\,\;\=])'
_ipv4 = '(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3,3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])'
_ipvfuture = 'v[a-f0-9]+\.([a-z0-9\-\.\_\~]|[\!\$\&\'\(\)\*\+\,\;\=]|\:)+'
_uri = '^' + _scheme +':(\/\/(' + _userinfo + '?(\[(' + _ipv6 + '|' + _ipvfuture + ')\]|' \
       + _ipv4 + '|' + _regname + '*)' + _port + '?)' + _path + ')' + _query + '?' + _fragment + '?$'
"""