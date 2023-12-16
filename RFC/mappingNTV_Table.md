
| type                 | format                             | NTVtype                                       |
|----------------------|------------------------------------|-----------------------------------------------|
| string               | default                            | string                                        |
| string               | email                              | email                                         |
| string               | uri                                | uri                                           |
| string               | Binary (base64 string)             | binary                                        |
| string               | uuid                               | uuid                                          |
| datetime             | default (datetime ISO8601 in UTC)  | datetime                                      |
| date, time, datetime | any (parsable ?)                   | *date, time or datetime with parsable format* |
| date, time, datetime | \<PATTERN\>                        | *date, time or datetime with custom format*   |
| date                 | default (date ISO8601)             | *date*                                        |
| time                 | default (time ISO8601)             | *time*                                        |
| year                 | default                            | *year*                                        |
| yearmonth            | default                            | *month*                                       |
| duration             | default (lexical duration ISO8601) | duration                                      |
| number               | default                            | number                                        |
| integer              | default                            | integer                                       |
| boolean              | default                            | boolean                                       |
| object               | default (json)                     | json                                          |
| array                | default (json array)               | Json                                          |
| geopoint             | default (string “lon, lat”)        | *Point (string)*                              |
| geopoint             | array (array [lon, lat])           | *Point (geojson array)*                       |
| geopoint             | object (eg {"lon": 90, "lat": 45}) | *Point (json object)*                         |
| geojson              | default (geojson spec)             | *Geometry (geojson)*                          |
| geojson              | Topojson (topojson spec)           | *Geometry (topojson)*                         |
| any (custom type)    | default                            | custom type                                   |
| <any>                | <any> (string)                     | *Everything (custom type)*                    |


