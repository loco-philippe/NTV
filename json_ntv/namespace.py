# -*- coding: utf-8 -*-
"""
Namespace and Datatype entities are used to define NTVtype.

The `namespace` module is part of the `NTV.json_ntv` package ([specification document](
https://loco-philippe.github.io/ES/JSON%20semantic%20format%20(JSON-NTV).htm)).

It contains the `Namespace`, `Datatype`, `DatatypeError` classes and
the functions `agreg_type`, `from_file`, `mapping`, `relative_type` and `str_type`.

For more information, see the
[user guide](https://loco-philippe.github.io/NTV/documentation/user_guide.html)
or the [github repository](https://github.com/loco-philippe/NTV)
"""

import configparser
from pathlib import Path
import json
import requests

import json_ntv
from json_ntv.ntv_util import NtvUtil
from json_ntv.ntv_validate import Validator

SCH_ORG = "https://schema.org/"


def agreg_type(str_typ, def_type, single):
    """
    Aggregate  str_typ and def_type.

    Parameters
    ----------
    str_typ : Datatype or String (long_name)
        Datatype to aggregate.
    def_type : Datatype or String (long_name)
        Default Datatype or Namespace.
    single : Boolean
        Ntv entity concerned (True if NtvSingle).

    Returns
    -------
    aggregation
        Datatype or Namespace if not single.
    """
    if isinstance(str_typ, Datatype):
        str_typ = str_typ.long_name
    def_type = str_type(def_type, single)
    if not str_typ and (not single or isinstance(def_type, Datatype)):
        return def_type
    if not str_typ:
        return Datatype("json")
    clas = Namespace if str_typ[-1] == "." else Datatype
    if not def_type:
        return clas.add(str_typ)
    if clas == Datatype or clas == Namespace and not single:
        try:
            return clas.add(str_typ)
        except DatatypeError:
            for typ in _join_type(def_type.long_name, str_typ):
                try:
                    return clas.add(typ)
                except DatatypeError:
                    pass
    raise DatatypeError(str_typ + " and " + def_type.long_name + " are incompatible")


def from_file(file, name, long_parent=None):
    """create a set of Datatype and Namespace associated to a custom Namespace

    *Parameters*

        - **file** : .ini file - description of the Datatype and Namespace
        - **name** : string - name of the root custom Namespace
        - **long_parent** : longname of the parent Namespace of the root Namespace
    """
    long_parent = "" if not long_parent else long_parent
    if name[0] != "$":
        raise DatatypeError(name + " is not a custom Datatype")
    if long_parent not in Namespace.namespaces():
        raise DatatypeError(long_parent + " is not a valid Datatype")
    schema_nsp = Namespace(name, long_parent)
    config = configparser.ConfigParser()
    config.read(file)
    if name not in config.sections():
        raise DatatypeError(name + " is not present in " + str(file))
    _add_namespace(config, schema_nsp)


def mapping(typ=None, func=None):
    """Affect a validate function (func) to a Datatype (typ)"""
    if typ and func:
        Datatype(typ).validate = func
    else:
        if isinstance(typ, str):
            func_lis = [typ + "_valid"]
        elif isinstance(typ, (list, tuple)):
            func_lis = [typ_str + "_valid" for typ_str in typ]
        else:
            func_lis = [typ_str + "_valid" for typ_str in Datatype._types_]
        for func_str in func_lis:
            if func_str in Validator.__dict__:
                Datatype(func_str[:-6]).validate = Validator.__dict__[func_str]


def relative_type(str_def, str_typ):
    """return relative str_typ string from Datatype or Namespace str_def

    *Parameters*

        - **str_def** : String - long_name of the Namespace or Datatype
        - **str_type** : String - long_name of Ntvtype to be relative"""
    if not str_def and not str_typ:
        return ""
    if str_def == str_typ:
        return ""
    if not str_def or str_def not in str_typ:
        return str_typ
    if not str_typ and str_def[-1] != ".":
        return str_def
    str_def_split = str_def.split(".")[:-1]
    str_typ_split = str_typ.split(".")
    ind = 0
    for ind, name in enumerate(str_typ_split):
        if name not in str_def_split:
            break
    return ".".join(str_typ_split[ind:])


def str_type(long_name, single):
    """create a Datatype or a Namespace from a string

    *Parameters*

        - **long_name** : String - name of the Namespace or Datatype
        - **single** : Boolean - If True, default type is 'json', else None"""
    if not long_name and single:
        return Datatype("json")
    if not long_name and not single:
        return None
    if long_name.__class__.__name__ in ["Datatype", "Namespace"]:
        return long_name
    if not isinstance(long_name, str):
        raise DatatypeError("the long_name is not a string")
    if long_name[-1] == ".":
        return Namespace.add(long_name)
    return Datatype(long_name)


def _add_namespace(config, namesp):
    """create the child Namespace and the child Datatype of the parent namespace"""
    if namesp.name in config.sections():
        confname = config[namesp.name]
        if "namespace" in confname:
            for nspname in json.loads(confname["namespace"]):
                nsp = Namespace(nspname, namesp, force=True)
                _add_namespace(config, nsp)
        if "type" in confname:
            for typ in json.loads(confname["type"]):
                Datatype(typ, namesp, force=True)


def _join_type(namesp, str_typ):
    """join Namespace string and Datatype or Namespace string"""
    namesp_sp = namesp.split(".")
    str_typ_sp = str_typ.split(".")
    idx = -1
    if str_typ_sp[0] in namesp_sp:
        idx = namesp_sp.index(str_typ_sp[0])
        if namesp_sp[idx:] != str_typ_sp[: len(namesp_sp[idx:])]:
            idx = -1
    if idx > -1:
        namesp_sp = namesp_sp[:idx]
    return [
        ".".join(namesp_sp[: i + 1] + str_typ_sp)
        for i in range(len(namesp_sp) - 1, -1, -1)
    ]


def _isin_schemaorg(name, prop=True, typ=None):
    """return True if a schema.org Property is present and associated to a Type
    or if a schema.org Type is present"""
    n_org = name if prop else name[:-1]
    t_org = typ[:-1] if typ else None
    req_name = requests.get(
        SCH_ORG + n_org, allow_redirects=True, timeout=10
    ).content.decode()
    if not prop:
        return "Type</ti" in req_name
    is_prop = "Property</ti" in req_name
    if not t_org:
        return is_prop
    if is_prop:
        return (
            "/" + n_org
            in requests.get(
                SCH_ORG + t_org, allow_redirects=True, timeout=10
            ).content.decode()
        )
    return False


class TypeBase(NtvUtil):
    """type of NTV entities.

    *Attributes :*

    - **name** : String - name of the type
    - **nspace** : Namespace - namespace associated
    - **custom** : boolean - True if not referenced
    - **validate** : function (default None) - validate function

    The methods defined in this class are :

    *staticmethods*
    - `types`
    - `add`

    *dynamic values (@property)*
    - `category`
    - `json_type`
    - `gen_type`
    - `long_name`

    *instance methods*
    - `isin_namespace`
    """

    @staticmethod
    def types():
        """return the list of TypeBase created"""
        return [nam.long_name for nam in NtvUtil._types_.values()]

    @classmethod
    def add(cls, long_name, module=False, force=False, validate=None):
        """activate and return a valid TypeBase defined by the long name

        *parameters :*

        - **long_name** : String - absolut name of the TypeBase
        - **module** : boolean (default False) - if True search data in the
        local .ini file, else in the distant repository
        - **validate** : function (default None) - validate function to include
        """
        if long_name == "":
            return None
        if long_name in cls.types():
            return NtvUtil._types_[long_name]
        split_name = long_name.rsplit(".", 1)
        if split_name[-1] == "":
            raise DatatypeError(long_name + " is not a valid TypeBase")
        if len(split_name) == 1:
            return cls(split_name[0], force=force, validate=validate)
        if len(split_name) == 2:
            nspace = Namespace.add(split_name[0] + ".", module=module, force=force)
            return cls(split_name[1], nspace, force=force)
        raise DatatypeError(long_name + " is not a valid TypeBase")

    def __init__(self, name, nspace=None, force=False, validate=None):
        """TypeBase constructor.

        *Parameters*

        - **name** : string - name of the Type
        - **nspace** : Namespace (default None) - namespace associated
        - **force** : boolean (default False) - if True, no Namespace control
        - **validate** : function (default None) - validate function to include"""
        if isinstance(name, TypeBase):
            self.name = name.name
            self.nspace = name.nspace
            self.custom = name.custom
            self.validate = name.validate
            # self.gen_type = name.gen_type
            # self.long_name = name.long_name
            return
        if not name or not isinstance(name, str):
            raise DatatypeError("null name is not allowed")
        if not name and not nspace:
            name = "json"
        if not nspace:
            nspace = NtvUtil._namespaces_[""]
        if nspace.file and SCH_ORG in nspace.file:
            if not _isin_schemaorg(name, typ=nspace.name):
                raise DatatypeError(
                    name
                    + " is not a schema.org Property associated to the "
                    + nspace.name
                    + "Type "
                )
        else:
            if not (name[0] == "$" or force or name in nspace.content["type"]):
                raise DatatypeError(name + " is not defined in " + nspace.long_name)
        self.name = name
        self.nspace = nspace
        self.custom = nspace.custom or name[0] == "$"
        # self.gen_type = '' if self.custom else self.nspace.content['type'][self.name]
        # self.long_name = self.nspace.long_name + self.name
        if validate:
            self.validate = validate
        NtvUtil._types_[self.long_name] = self
        return

    def __eq__(self, other):
        """equal if name and nspace are equal"""
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.name == other.name and self.nspace == other.nspace

    def __hash__(self):
        """return hash(name) + hash(nspace)"""
        return hash(self.name) + hash(self.nspace)

    def __str__(self):
        """return string format"""
        return self.long_name

    def __repr__(self):
        """return classname and long name"""
        return self.__class__.__name__ + "(" + self.long_name + ")"

    @property
    def json_type(self):
        """return the json type of the TypeBase"""
        if self.custom:
            return ""
        prop = self.nspace.content["type"][self.name]
        if isinstance(prop, list):
            return prop[1]
        return "json"

    @property
    def category(self):
        """return the category of the TypeBase"""
        if self.custom:
            return ""
        prop = self.nspace.content["type"][self.name]
        if isinstance(prop, list):
            return prop[2]
        return "local"

    @property
    def gen_type(self):
        """return the generic type of the TypeBase"""
        if self.custom:
            return ""
        prop = self.nspace.content["type"][self.name]
        if isinstance(prop, list):
            return prop[0]
        return prop

    @property
    def long_name(self):
        """return a string with the absolute name"""
        return self.nspace.long_name + self.name

    def isin_namespace(self, long_name):
        """return the number of level between self and nspace, -1 if None"""
        return self.nspace.is_child(Namespace.add(long_name))


class Datatype(TypeBase):
    """The Datatype of NTV entities is composed with a TypeBase and an optional
    extension.

    *Attributes :*

    - **name** : String - name of the Datatype
    - **base_name** : String - name of the TypeBase
    - **nspace** : Namespace - namespace associated
    - **custom** : boolean - True if not referenced
    - **validate** : function (default None) - validate function
    - **typebase** : TypeBase - TypeBase of the Datatype
    - **extension** : String (default None) - extension of the TypeBase

    The methods defined in this class are :

    *classmethod*
    - `add`

    *dynamic values (@property)*
    - `category`
    - `json_type`
    - `gen_type`
    - `long_name` (TypeBase)

    *staticmethods*
    - `types` (TypeBase)

    *instance methods*
    - `isin_namespace` (TypeBase)
    - `validate` (TypeBase)
    """

    def __init__(self, full_name, module=False, force=False, validate=None):
        """DataType constructor.

        *Parameters*

        - **full_name** : String - absolut name of the Datatype
        - **module** : boolean (default False) - if True search data in the
        local .ini file, else in the distant repository
        - **force** : boolean (default False) - if True, no Namespace control
        - **validate** : function (default None) - validate function to include"""
        if isinstance(full_name, Datatype):
            self.name = full_name.name
            self.base_name = full_name.base_name
            self.typebase = full_name.typebase
            self.extension = full_name.extension
            return
        spl_name = full_name.split("[", maxsplit=1)
        long_base = spl_name[0]
        self.extension = spl_name[1][:-1] if len(spl_name) == 2 else None
        self.typebase = TypeBase.add(long_base, module, force, validate)
        ext_str = "[" + self.extension + "]" if self.extension else ""
        self.base_name = self.typebase.name
        self.name = self.typebase.name + ext_str
        return

    @property
    def gen_type(self):
        """return the generic type of the Datatype"""
        return self.typebase.gen_type

    @property
    def json_type(self):
        """return the json type of the Datatype"""
        return self.typebase.json_type

    @property
    def category(self):
        """return the category of the Datatype"""
        return self.typebase.category

    @property
    def nspace(self):
        """return the nspace of the Datatype"""
        return self.typebase.nspace

    @property
    def custom(self):
        """return the custom of the Datatype"""
        return self.typebase.custom

    @property
    def validate(self):
        """return the validate of the Datatype"""
        return self.typebase.validate

    @classmethod
    def add(cls, long_name, module=False, force=False, validate=None):
        """method eqivalent to the constructor"""
        return cls(long_name, module, force, validate)


class Namespace(NtvUtil):
    """Namespace of NTV entities.

    *Attributes :*

    - **name** : String - name of the namespace
    - **file** : string - location of the file init
    - **content** : dict - {'type': <list of ntv_type names>,
                            'namespace': <list of namespace names>}
    - **parent** : Namespace - parent namespace
    - **custom** : boolean - True if not referenced

    The methods defined in this class are :

    *staticmethods*
    - `namespaces`

    *classmethods*
    - `add`

    *dynamic values (@property)*
    - `long_name`

    *instance methods*
    - `is_child`
    - `is_parent`
    """

    _pathconfig_ = (
        "https://raw.githubusercontent.com/loco-philippe/NTV/master/json_ntv/config/"
    )
    _global_ = "NTV_global_namespace.ini"

    @staticmethod
    def namespaces():
        """return the list of Namespace created"""
        return [nam.long_name for nam in NtvUtil._namespaces_.values()]

    @classmethod
    def add(cls, long_name, module=False, force=False):
        """activate and return a valid Namespace defined by the long_name.

        *parameters :*

        - **long_name** : String - absolut name of the Namespace
        - **module** : boolean (default False) - if True search data in the
        local .ini file, else in the distant repository
        """
        if long_name in Namespace.namespaces():
            return NtvUtil._namespaces_[long_name]
        split_name = long_name.rsplit(".", 2)
        if len(split_name) == 1 or split_name[-1] != "":
            raise DatatypeError(long_name + " is not a valid Namespace")
        if len(split_name) == 2:
            return cls(split_name[0] + ".", module=module, force=force)
        if len(split_name) == 3:
            parent = Namespace.add(split_name[0] + ".", force=force)
            return cls(split_name[1] + ".", parent, module=module, force=force)
        raise DatatypeError(long_name + " is not a valid Namespace")

    def __init__(self, name="", parent=None, module=False, force=False):
        """
        Namespace constructor.

        *Parameters*

        - **name** : String - name of the namespace
        - **parent** : Namespace - parent namespace
        - **module** : boolean (default False) - if True search data in the
                        local .ini file, else in the distant repository
        - **content** : dict : {'type': <list of ntv_type names>,
                                'namespace': <list of namespace names>}
        """
        if name and not parent:
            parent = NtvUtil._namespaces_[""]
        if parent and parent.file and SCH_ORG in parent.file:
            if not _isin_schemaorg(name, False):
                raise DatatypeError(name + " is not a schema.org Type ")
        else:
            if name and not (
                name[0] == "$" or force or name in parent.content["namespace"]
            ):
                raise DatatypeError(name + " is not defined in " + parent.long_name)
        self.name = name
        self.parent = parent
        self.custom = parent.custom or name[0] == "$" if parent else False
        self.file = Namespace._file(self.parent, self.name, self.custom, module)
        self.content = Namespace._content(self.file, self.name, self.custom, module)
        NtvUtil._namespaces_[self.long_name] = self

    def __eq__(self, other):
        """equal if name and parent are equal"""
        if self is None and other is None:
            return True
        if self is None or other is None:
            return False
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        return self.name == other.name and self.parent == other.parent

    def __hash__(self):
        """return hash(name) + hash(parent)"""
        return hash(self.name) + hash(self.parent)

    def __str__(self):
        """return string format"""
        return self.long_name

    def __repr__(self):
        """return classname and long name"""
        return self.__class__.__name__ + "(" + self.long_name + ")"

    @staticmethod
    def _file(parent, name, custom, module):
        """return the file name of the Namespace configuration

        *parameters :*

        - **parent** : Namespace - Parent of the Namespace
        - **name** : String - name of the Namespace
        - **custom** : boolean - if True, return None (custom Namespace)
        - **module** : boolean (default False) - if True search data in the
        local .ini file, else in the distant repository
        """
        if custom:
            return None
        if parent:
            if "schema.org" in parent.file or name == "org.":
                return SCH_ORG
            config = configparser.ConfigParser()
            if module:
                p_file = Path(parent.file).stem + Path(parent.file).suffix
                config.read(Path(json_ntv.__file__).parent / "config" / p_file)
            else:
                config.read_string(
                    requests.get(
                        parent.file, allow_redirects=True, timeout=10
                    ).content.decode()
                )
            return (
                Namespace._pathconfig_ + json.loads(config["data"]["namespace"])[name]
            )
        return Namespace._pathconfig_ + Namespace._global_

    @staticmethod
    def _content(file, name, custom, module):
        """return the content of the Namespace configuration

        *parameters :*

        - **file** : string - file name of the parent Namespace
        - **name** : string - name of the Namespace
        - **custom** : boolean - if True, return empty dict (custom Namespace)
        - **module** : boolean (default False) - if True search data in the
        local .ini file, else in the distant repository

        *return :*

        - dict : {'type': <list of ntv_type names>,
                  'namespace': <list of namespace names>}
        """
        if custom or "schema.org" in file:
            return {"type": {}, "namespace": {}}
        config = configparser.ConfigParser()
        if module:
            p_file = Path(file).stem + Path(file).suffix
            config.read(Path(json_ntv.__file__).parent / "config" / p_file)
        else:
            config.read_string(
                requests.get(file, allow_redirects=True, timeout=10).content.decode()
            )
        config_name = config["data"]["name"]
        if config_name != name:
            raise DatatypeError(file + " is not correct")
        return {
            "type": json.loads(config["data"]["type"]),
            "namespace": json.loads(config["data"]["namespace"]),
        }

    @property
    def long_name(self):
        """return a string with the absolute name"""
        if self.parent is None or self.parent.name == "":
            return self.name
        return self.parent.long_name + self.name

    def is_child(self, nspace):
        """return the number of level between self and nspace, -1 if None"""
        parent = self.parent
        if self == nspace:
            return 0
        if not self.name:
            return -1
        rang = 1
        while parent.name != "" and parent != nspace:
            rang += 1
            parent = parent.parent
        if parent == nspace:
            return rang
        return -1

    def is_parent(self, nspace):
        """return the number of level between self and nspace, -1 if None"""
        return nspace.is_child(self)


class DatatypeError(Exception):
    """Datatype or Namespace Exception"""


nroot = Namespace(module=True)
for root_typ in nroot.content["type"]:
    # typ = Datatype(root_typ, module=True,
    Datatype(root_typ, module=True, validate=Validator.__dict__[root_typ + "_valid"])
# mapping(Datatype.types())
typ_json = Datatype("json")
