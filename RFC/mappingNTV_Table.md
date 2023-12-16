# mapping NTVtypes

## mapping NTV-Table Schema

|----------------------|------------------------------------|-----------------------------------------------|
| type                 | format                             | NTVtype                                       |
|----------------------|------------------------------------|-----------------------------------------------|
| string               | default                            | string                                        |
| string               | email                              | email                                         |
| string               | uri                                | uri                                           |
| string               | binary (base64 string)             | binary                                        |
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
| string               | default                            | string                                        |
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
| string               | uri-template                       | uritem                                        | xxx
| string               | iri                                | iri                                           | xxx
| string               | iri-reference                      | iriref                                        | xxx
| string               | json-pointer                       | jpointer                                      | xxx
| string               | relative-json-pointer              | rjpointer                                     | xxx
| string               | regex                              | regex                                         | xxx
| number               | default                            | number                                        |
| integer              | default                            | int                                           |
| boolean              | default                            | boolean                                       |
| object               | default (json)                     | json                                          |
| array                | default (json array)               | array                                         |
| null                 | default (date ISO8601)             | date                                          |
| -any-                | -any-                              | $xxx (custom type)                            |

