# -*- coding: utf-8 -*-
"""
The `ntv_schema` module is a demonstrator of the application of JSON Schema to
NTV data. It relies on the `jsonschema` module.

The main function `ntv_validate` validate a NTVdata against a schema (json data).
The main function `ntv_validate_opt2` validate a NTVdata against a schema (NTV data).

For examples, see the Jupyter Notebook in the same directory : `./example_schema.ipynb`
"""


from json_ntv.ntv import Ntv, NtvList, NtvSingle
from jsonschema import validate, SchemaError

# %% interface json schema


def validat(json_data, json_sch, part, ptr, mode):
    '''return the validation (True/False) of a json data conformity 
    to a 'json_sch' JSONschema.

    *Parameters*

        - **json_data**: json_data to validate
        - **json_sch**: json-value - JSONschema
        - **mode**: integer (default 0) - level of information
            - 0: no information
            - 1: list of controls and errors
            - 2: details of errors (traceback)
    '''
    if mode > 1 and json_sch:
        print('    ', ptr, '-', part, ' : ', json_data, json_sch)
    valid = False
    if mode < 3:
        try:
            valid = validate(json_data, json_sch) is None
        except SchemaError:
            if mode > 0:
                print('  error ', ptr, '-', part, ' : ', json_data,
                      'is not valid with schema : ', json_sch)
    else:
        valid = validate(json_data, json_sch) is None
    return valid


def _ntv_to_json(ntv_data):
    '''transform a Ntv entity into a json representation'''
    return {'valueNtv': ntv_data.ntv_value,
            'nameNtv': ntv_data.ntv_name,
            'typeNtv': ntv_data.type_str}

# %% validate schema json


def ntv_validate(ntv_data, schema, mode=0):
    '''return the validation (True/False) of a NTV entity conformity to a 'sch' schema.

    *Parameters*

    - **ntv_data**: Ntv entity (json_ntv or NTV)
    - **schema**: json-value - NTVschema (JsonSchema keywords)
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''
    ntv_data = Ntv.obj(ntv_data)
    valid = True
    if mode == 1:
        print('  validate : ', ntv_data.pointer())  # , sch)
    simp_sch = {}
    for sch in schema:
        if sch == 'required' and schema[sch][0][0] == '/':
            valid &= _val_required(ntv_data, schema[sch], mode)
        elif sch == 'properties':
            valid &= _val_prop(ntv_data, schema[sch], mode)
        elif sch == 'prefixItems':
            valid &= _val_prefix(ntv_data, schema[sch], mode)
        elif sch == 'items':
            valid &= _val_items(ntv_data, schema[sch], mode)
        elif sch[0] == '/':
            valid &= _val_pointer(ntv_data, {sch: schema[sch]}, mode)
        else:
            simp_sch[sch] = schema[sch]
    if simp_sch:
        valid &= _val_simple(ntv_data, simp_sch, mode)
    return valid


def _val_pointer(ntv_data, sch, mode):
    '''return the pointer validation (True/False) of a NTV entity conformity 
    to a 'sch' schema'''
    valid = True
    sch_ptr = list(sch.keys())[0][1:]
    sch = sch['/' + sch_ptr]
    if sch_ptr.isdecimal():
        idx = int(sch_ptr)
        if len(ntv_data) > idx:
            valid &= ntv_validate(ntv_data.ntv_value[idx], sch, mode)
            return valid
    for ntv in ntv_data:
        if ntv.ntv_name and ntv.ntv_name == sch_ptr:
            valid &= ntv_validate(ntv, sch, mode)
            break
        if ntv.json_name_str and ntv.json_name_str == sch_ptr:
            valid &= ntv_validate(ntv, sch, mode)
            break
    return valid


def _val_prop(ntv_data, sch, mode):
    '''return the properties validation (True/False) of a NTV entity conformity
    to a 'sch' schema.'''
    valid = True
    for idx, ntv in enumerate(ntv_data):
        p_name = ntv.ntv_name if ntv.ntv_name in sch else (
            ntv.json_name_str if ntv.json_name_str in sch else None)
        p_name = p_name if p_name else (str(idx) if str(idx) in sch else None)
        if not p_name is None:
            valid &= ntv_validate(ntv, sch[p_name], mode)
    return valid


def _val_prefix(ntv_data, sch, mode):
    '''return the prefixItems validation (True/False) of a NTV entity conformity
    to a 'sch' schema.'''
    valid = True
    for ntv, sch_pref in zip(ntv_data, sch):
        valid &= ntv_validate(ntv, sch_pref, mode)
    return valid


def _val_required(ntv_data, sch, mode):
    '''return the required validation (True/False) of a NTV entity conformity
    to a 'sch' schema.'''
    valid = True
    ntv_names = [ntv.name for ntv in ntv_data]
    json_ntv_names = [ntv.json_name_str for ntv in ntv_data]
    for ptr in sch:
        valid &= (ptr[1:] in ntv_names) or (ptr[1:] in json_ntv_names)
    return validat([ptr[1:] for ptr in sch], valid, 'required', ntv_data.pointer(), mode)


def _val_items(ntv_data, sch, mode):
    '''return the items validation (True/False) of a NTV entity conformity
    to a 'sch' schema.'''
    valid = True
    for ntv in ntv_data:
        valid &= ntv_validate(ntv, sch, mode)
    return valid


def _val_simple(ntv_data, sch, mode):
    '''return the validation (True/False) of a NTV entity conformity
    to a 'sch' schema.'''
    if not sch:
        return True
    json_data = _ntv_to_json(ntv_data)
    json_sch = _simple_to_jsch(sch)
    valid = True
    for part in ['valueNtv', 'typeNtv', 'nameNtv']:
        valid &= validat(json_data[part], json_sch[part],
                         part, ntv_data.pointer(), mode)
    return valid


def _simple_to_jsch(ntvsch):
    '''transform a simple NTVschema into a JSONschema'''
    jsonsch = {}
    jsonsch['typeNtv'] = ntvsch.setdefault('typeNtv', {})
    jsonsch['nameNtv'] = ntvsch.setdefault('nameNtv', {})
    jsonsch['valueNtv'] = ntvsch.setdefault('valueNtv', {})
    jsonsch['valueNtv'] |= {key: val for key, val in ntvsch.items() if not key in
                            ['typeNtv', 'nameNtv', 'valueNtv', 'propertyNames']}
    jsonsch['nameNtv'] |= ntvsch.setdefault('propertyNames', {})
    return _json(jsonsch)


def _json(dic):
    '''in a schema leaf, transform NTVkeywords into JSONkeywords'''
    return {key[1:] if key[0] == ':' else key: _json(value)
            for key, value in dic.items()} if isinstance(dic, dict) else dic


def _simp(dic, keywords=None):
    '''return a dict schema without keywords members'''
    keyw = list(keywords) if keywords else []
    keyw += ['properties', 'prefixItems', 'items']
    return {key: val for key, val in dic.items()
            if not key in keyw} if isinstance(dic, dict) else dic

# %% validate schema ntv


def ntv_validate_opt2(ntv_data, ntv_sch, mode=0):
    '''return the validation (True/False) of a NTV entity conformity
    to a 'sch' NTVschema.

    *Parameters*

    - **ntv_data**: Ntv entity (json_ntv or NTV)
    - **sch**: NTV_schema (json_ntv or NTV)
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''
    ntv_sch = ntv_sch if 'sch.' in list(
        ntv_sch.keys())[0] else {'sch.': ntv_sch}
    return ntv_validate2(ntv_data, ntv_sch, mode)


def ntv_validate2(ntv_data, ntv_sch, mode=0):
    '''return the validation (True/False) of a NTV entity conformity
    to a 'sch' NTVschema.

    *Parameters*

    - **ntv_data**: Ntv entity (json_ntv or NTV)
    - **sch**: NTV_schema (json_ntv or NTV)
    - **mode**: integer (default 0) - level of information
        - 0: no information
        - 1: list of controls and errors
        - 2: details of errors (traceback)
    '''
    ntv_data = Ntv.obj(ntv_data)
    ntv_sch = Ntv.obj(ntv_sch)
    valid = True
    if mode == 1:
        print('  validate : ', ntv_data.pointer())  # , sch)
    if isinstance(ntv_sch, NtvSingle):
        ntv_sch = NtvList([ntv_sch])
    for sch in ntv_sch:
        if sch.name.isdecimal():
            idx = int(sch.name)
            if len(ntv_data) > idx:
                valid &= ntv_validate2(
                    ntv_data.ntv_value[idx], sch.ntv_value, mode)
        elif sch.type_str == "sch.items" or sch.name == "items":
            valid &= _val_item2(ntv_data, sch, mode)
        elif sch.type_str[:4] == 'sch.' and sch.type_str[-1] == '.':
            valid &= _val_pointer2(ntv_data, sch, mode)
        elif sch.type_str[:4] != 'sch.':
            valid &= _val_pointer2(ntv_data, sch, mode)
        else:
            valid &= _val_simple2(ntv_data, sch, mode)
    return valid


def _val_pointer2(ntv_data, sch, mode):
    '''return the pointer validation (True/False) of a NTV entity conformity
    to a 'sch' NTVschema.'''
    valid = True
    for ntv in ntv_data:
        if ntv.ntv_name and ntv.ntv_name == sch.name:
            valid &= ntv_validate2(ntv, sch, mode)
            break
        if ntv.json_name_str and ntv.json_name_str == sch.json_name_str:
            valid &= ntv_validate2(ntv, Ntv.obj({'sch.': sch.val}), mode)
            break
    return valid


def _val_simple2(ntv_data, sch, mode):
    '''return the validation (True/False) of a NTV entity conformity
    to a 'sch' NTVschema.'''
    if not sch:
        return True
    json_data = _ntv_to_json(ntv_data)
    json_sch = _simple_to_jsch2(sch)
    valid = True
    for part in ['valueNtv', 'typeNtv', 'nameNtv']:
        valid &= validat(json_data[part], json_sch[part],
                         part, ntv_data.pointer(), mode)
    return valid


def _val_item2(ntv_data, sch, mode):
    '''return the items validation (True/False) of a NTV entity conformity
    to a 'sch' NTVschema.'''
    valid = True
    sch_item = Ntv.obj({'sch.': sch.val})
    if isinstance(ntv_data, NtvSingle):
        ntv_data = NtvList([ntv_data])
    for ntv in ntv_data:
        valid &= ntv_validate2(ntv, sch_item, mode)
    return valid


def _replace(keyword):
    keyw = keyword[1:] if keyword[0] == ':' else keyword
    keyw = keyw[4:] if keyw[0:4] == 'sch.' else keyw
    return keyw


def _json2(dic):
    '''in a schema leaf, transform NTVkeywords into JSONkeywords'''
    return {_replace(key): _json2(value)
            for key, value in dic.items()} if isinstance(dic, dict) else dic


def _simple_to_jsch2(ntvsch):
    '''transform a simple NTVschema into a JSONschema'''
    jssch = _json2(Ntv.to_obj(ntvsch))

    jsonsch = {}
    jsonsch['typeNtv'] = jssch.setdefault('typeNtv', {})
    jsonsch['nameNtv'] = jssch.setdefault('nameNtv', {})
    jsonsch['valueNtv'] = jssch.setdefault('valueNtv', {})
    jsonsch['valueNtv'] |= {key: val for key, val in jssch.items()
                            if not key in ['typeNtv', 'nameNtv', 'valueNtv']}
    return jsonsch


class NtvSchemaError(Exception):
    ''' NtvSchema Exception'''
    # pass
