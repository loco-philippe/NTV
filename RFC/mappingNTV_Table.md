# mapping NTVtypes

## mapping NTV-Table Schema

|----------------------|------------------------------------|-----------------------------------------------|
| type                 | format                             | NTVtype                                       |
|----------------------|------------------------------------|-----------------------------------------------|
| string               | default                            | string                                        |
| string               | email                              | email                                         |
| string               | uri                                | uri                                           |
| string               | binary (base64 string)             | base64                                        |
| string               | uuid                               | uuid                                          |
| number               | default                            | number                                        |
| integer              | default                            | int                                           |
| boolean              | default                            | boolean                                       |
| object               | default (json)                     | json                                          |
| array                | default (json array)               | array                                         |
| date                 | default (date ISO8601)             | date                                          |
| time                 | default (time ISO8601)             | time                                          |
| datetime             | default (datetime ISO8601 in UTC)  | datetime                                      |
| year                 | default                            | year                                          |
| yearmonth            | default                            | yearmonth                                     |
| duration             | default (lexical duration ISO8601) | duration                                      |
| geopoint             | default (string "lon, lat")        | pointstr                                      |
| geopoint             | array (array [lon, lat])           | point                                         |
| geopoint             | object (eg {"lon": 90, "lat": 45}) | pointobj                                      |
| geojson              | default (geojson spec)             | geojson                                       |
| -any-                | -any-                              | $xxx (custom type)                            |

parsable and pattern formats (datation) and topojson (location) are not included

## mapping NTV-JSON Schema

|----------------------|------------------------------------|-----------------------------------------------|
| type                 | format                             | NTVtype                                       |
|----------------------|------------------------------------|-----------------------------------------------|
| string               |                                    | string                                        |
| string               | date-time                          | datetime                                      |
| string               | time                               | time                                          |
| string               | date                               | date                                          |
| string               | duration                           | duration                                      |
| string               | email                              | email                                         |
| string               | idn-email                          | idnemail                                      |
| string               | hostname                           | hostname                                      |
| string               | idn-hostname                       | idnhostname                                   |
| string               | ipv4                               | ipv4                                          |
| string               | ipv6                               | ipv6                                          |
| string               | uuid                               | uuid                                          |
| string               | uri                                | uri                                           |
| string               | uri-reference                      | uriref                                        |
| string               | uri-template                       | uritem                                        |
| string               | iri                                | iri                                           |
| string               | iri-reference                      | iriref                                        |
| string               | json-pointer                       | jpointer                                      |
| string               | relative-json-pointer              | rjpointer                                     |
| string               | regex                              | regex                                         |
| number               | default                            | number                                        |
| integer              | default                            | int                                           |
| boolean              | default                            | boolean                                       |
| object               |                                    | object                                        |
| array                |                                    | array                                         |
| contentEncoding      | base64                             | base64                                        |
| contentEncoding      | base32                             | base32                                        |
| contentEncoding      | base16                             | base16                                        |
| contentEncoding      | binary                             | binary                                        |
| null                 |                                    | null                                          |

Built-in types with Keywords : $key, $ref, $anchor, $ref, $defs are not included. 

## mapping YANG

|----------------------|------------------------------------|-----------------------------------------------|
| type                 | NTVtype                            |comments                                       |
|----------------------|------------------------------------|-----------------------------------------------|
| boolean              | boolean                            |                                               |
| decimal64            | decimal64                          |                                               |
| empty                | null                               |                                               |
| int8                 | int8                               |                                               |
| int16                | int16                              |                                               |
| int32                | int32                              |                                               |
| int64                | int64                              |                                               |
| uint8                | uint8                              |                                               |
| uint16               | uint16                             |                                               |
| uint32               | uint32                             |                                               |
| uint64               | uint64                             |                                               |
| string               | string                             |                                               |
| bit                  | bit                                |                                               |
| binary               | binary                             |                                               |
| leafref              | ref                                |                                               |
| -any-                | -any-                              | $xxx (custom type)                            |

Built-in types : enumeration, bits, leafref, identityref, instance-identifier, union are not included.