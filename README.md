### *JSON-NTV (named and typed value) : a semantic format for interoperability*

*JSON-NTV is a universal representation format. It allows the sharing and conversion of any type of data (NTV format).*     
    
*The NTV format is part of the [Environmental Sensing Project](https://github.com/loco-philippe/Environmental-Sensing#readme)*

# NTV
    
Today, the semantic level of shared data remains low. It is very often limited to the type of data defined in the exchange formats (strings for CSV formats; 
numbers, strings, arrays and objects for JSON formats).

The proposed consists of adding a type and a name to the data exchanged (see also the [presentation document](./documentation/JSON-NTV-standard.pdf)).

With this evolution any data, whatever its semantic level, can be identified, shared and interpreted in a consistent way.
The implementation of a type with a nested structure facilitates its appropriation.
Finally, compatibility with existing JSON structures allows progressive deployment.

# NTV structure

The constructed entities (called NTV for *named typed value*) are therefore a triplet with one mandatory element (the value in JSON format) and two optional elements (name, type).
>
> *For example, the location of Paris can be represented by:*
> - *a name: "Paris",*
> - *a type: the coordinates of a point according to the GeoJSON format,*
> - *a value: [ 2.3522, 48.8566]*

The easiest way to add this information is to use a JSON-object with a single member using the syntax [JSON-ND](https://github.com/glenkleidon/JSON-ND) for the first term of the member and the JSON-value for the second term of the member.
>
> *For the example above, the JSON representation is:*    
> *```{ "paris:point" : [2.3522, 48.8566] }```*

With this approach, three NTV entities are defined:
- a primitive entity which is not composed of any other entity (NTV-single),
- two structured entities: an unordered collection of NTV entities (NTV-set) and an ordered sequence of NTV entities (NTV-list).
      
as well as two JSON formats:
- simple format when the name and the type are not present (this is the usual case of CSV data),
- named format when the name or type is present (see example above for an NTV-single entity and below for a structured entity).
>
> *Example of an entity composed of two other entities:*
> - *```{ "cities::point": [[2.3522, 48.8566], [4.8357, 45.7640]] }``` for an NTV-list entity*
> - *```{ "cities::point": { "paris":[2.3522, 48.8566], "lyon":[4.8357, 45.7640] } }``` for an NTV-set entity*
>
> *Note: This syntax can also be used for CSV file headers*

The type incorporates a notion of `namespaces` that can be nested.
> *For example, the type: "ns1.ns2.type" means that:*
> - *ns1. is a namespace defined in the global namespace,*
> - *ns2. is a namespace defined in the ns1 namespace.,*
> - *type is defined in the ns2 namespace.*    
    
This structuring of type makes it possible to reference any type of data that has a JSON representation and to consolidate all the shared data structures within the same tree of types.

# NTV and JSON

The flowchart below explain how to convert and exchange native entities through NTV and JSON format.

```mermaid
flowchart LR
    text["#10240;#10240;JSON#10240;#10240;\ntext"]
    val["#10240;JSON-NTV#10240;\nvalue"]
    ntv["#10240;#10240;#10240;NTV#10240;#10240;#10240;\nentity"]
    nat["#10240;native#10240;\nentity"]
    text--->|JSON load|val
    val--->|JSON dump|text
    val--->|NTV from obj|ntv
    ntv--->|from NTV|nat
    ntv--->|NTV to obj|val
    nat--->|to NTV|ntv

```

### ***If you are interested challenge us !*** We will be very happy to show you the relevance of our approach

# Documentation and installation

- [Specification](./documentation/README.md)
- [Example](./example/README.md)
- [Python Connectors documentation](https://loco-philippe.github.io/NTV/json_ntv.html)
- [installation and package](./json_ntv/README.md)
