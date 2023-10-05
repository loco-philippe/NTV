### ***JSON-NTV (named and typed value)  <img src="https://loco-philippe.github.io/ES/json-ntv.PNG" alt="json-NTV" style="float:right;width:233px;height:64px;"> : a semantic format for interoperability***
*JSON-NTV is a universal representation format. It allows the sharing and conversion of any type of data.*     
    
*The NTV format is part of the [Environmental Sensing Project](https://github.com/loco-philippe/Environmental-Sensing#readme)*

For more information, see the [user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html) or the [github repository](https://github.com/loco-philippe/NTV).

# What is NTV
    
The semantic level of shared JSON (or CSV) data (e.g. Open Data) remains low, which makes automated reuse difficult.

JSON-NTV proposes to enrich it to obtain a real interoperable exchange format.    
  
## NTV format

The NTV format consists of representing data by three attributes: a name, a type and a value. This representation is common in programming languages (for example a variable with Python typing is defined by `age: int = 25`), however the JSON format represents data with only a value or a key:value pair.
    
The JSON-NTV extension consists of including the type in the name to associate it with a value (for example `{'age:int': 25}` is the JSON representation of the NTV triplet ('age', 'int' , 25 ) ).
   
This approach makes it possible to reversibly represent any simple or complex data by a JSON structure (high interoperability).

## Examples
```python
In [1]: from shapely.geometry import Point
        from datetime import date
        from pprint import pprint

In [2]: pprint(Ntv.obj(21).expand())
Out[2]: {'name': '', 'type': 'json', 'value': 21}

In [3]: pprint(Ntv.obj({"paris:point": [2.3, 48.9] }).expand())
Out[3]: {'name': 'paris', 'type': 'point', 'value': [2.3, 48.9]}

In [4]: pprint(Ntv.obj({"cities::point": [[2.3, 48.9], [4.8, 45.8] }).expand())
Out[4]: {'name': 'cities',
         'type': 'point',
         'value': [{'name': '', 'type': 'point', 'value': [2.3, 48.9]},
                   {'name': '', 'type': 'point', 'value': [4.8, 45.8]}]}

In [5]: pprint(Ntv.obj({"paris:point": [2.3, 48.9], "start:date": "2023-08-03", "measurement": 45.8}).expand())
Out[5]: {'name': '',
         'type': '',
         'value': [{'name': 'paris', 'type': 'point', 'value': [2.3, 48.9]},
                   {'name': 'start', 'type': 'date', 'value': '2023-08-03'},
                   {'name': 'measurement', 'type': 'json', 'value': 45.8}]}
```

> *Note: This typing syntax can also be used for CSV file headers*

## NTV structure

With this approach, two NTV entities are defined:
- a primitive entity which is not composed of any other entity (NTV-single),
- a structured entity which is an ordered sequence of NTV entities (NTV-list).
      
as well as two JSON formats:
- simple format when the name and the type are not present (e.g. `25`),
- named format when the name or type is present ((e.g. `{'age': 25}` or `{':int': 25}`)).

The type incorporates a notion of `namespace` that can be nested.
> *For example, the type: `ns1.ns2.type_a` means that:*
> - *`ns1.` is a namespace defined in the global namespace,*
> - *`ns2.` is a namespace defined in the `ns1.` namespace.,*
> - *`type_a` is defined in the `ns2.` namespace.*    
    
This structuring of type makes it possible to reference any type of data that has a JSON representation and to consolidate all the shared data structures within the same tree of types.

## NTV uses

Several variations and use cases of the NTV format are defined:
- Tabular data exchange format (e.g. open-data)
- Compact, reversible and semantic pandas-JSON interface
- Comment and change management of JSON data
- visualization of JSON or NTV tree
- JSON data editor

## NTV and JSON

The flowchart below explain how to convert and exchange native entities through NTV and JSON format.

```mermaid
flowchart LR
    text["#10240;#10240;JSON#10240;#10240;\ntext"]
    val["#10240;JSON-NTV#10240;\nvalue"]
    ntv["#10240;#10240;#10240;NTV#10240;#10240;#10240;\nentity"]
    nat["#10240;native#10240;\nentity"]
    text--->|JSON load|val
    val--->|JSON dump|text
    val--->|NTV from JSON|ntv
    ntv--->|from NTV|nat
    ntv--->|NTV to JSON|val
    nat--->|to NTV|ntv
```
The conversion between native entity and JSON-text is reversible (round trip).
```python
In [6]: loc_and_date = {'newyear': date(2023, 1, 2), 'Paris': Point(2.3, 48.9)}
        json_loc_date = Ntv.obj(loc_and_date).to_obj(encoded=True)
        print(json_loc_date, type(json_loc_date))
Out[6]: {"newyear:date": "2023-01-02", "Paris:point": [2.3, 48.9]} <class 'str'>

In [7]: Ntv.obj(json_loc_date).to_obj(format='obj') == loc_and_date
Out[7]: True
```
*Properties :*
- each NTV object has a unique JSON representation
- each JSON data corresponds to a unique NTV entity
- an NTV entity is a tree where each node is an NTV entity and each leaf an NTV-Single entity
- an NTV entity is a neutral representation (independent of a software or hardware platform)
