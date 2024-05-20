# package installation

## json_ntv package

The `json_ntv` package includes

- `ntv` module
  - `Ntv` abstract class
  - `NtvSingle` and `NtvList` child classes
- `namespace` module
  - `TypeBase`, `Datatype`, `Namespace`, `DatatypeError` classes
- `ntv_util` module
  - `NtvConnector`, `NtvUtil`, `NtvTree`, `NtvJsonEncoder`, `NtvError` classes
- `ntv_connector`module (`NtvConnector` child classes)
  - `SfieldConnec`, `SdatasetConnec`, `NfieldConnec`, `NdatasetConnec`, `MermaidConnec`, `ShapelyConnec`, `CborConnec` classes
- `ntv_patch` module
  - `NtvOp`, `NtvPatch`, `NtvPointer`, `NtvOpError` classes
- `ntv_validate`module
  - `Validator`, `ValidateError`classes

The 'Namespaces' used are defined in the [configuration files](https://github.com/loco-philippe/NTV/blob/main/json_ntv/config/README.md)

## Installation

json_ntv itself is a pure Python package. It can be installed with pip

    pip install json_ntv

dependency:

- only packages associated to used connectors (e.g. `Mermaid` if we use `MermaidConnec`)
