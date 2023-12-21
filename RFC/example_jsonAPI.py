# -*- coding: utf-8 -*-
"""
Example OpenAPI
"""

from json_ntv import Ntv

b = Ntv.obj(
{"example:$openAPI.":{
    "servers.": [
        {":url": "https://{username}.gigantic-server.com:{port}/{basePath}",
         ":description": "The production API server", 
         "variables.": {
            "username": {
              ":default": "demo",
              ":description": "this value is assigned by the service provider, in this example `gigantic-server.com`"},
            "port": {
              ":enum": ["8443", "443"],
              "default": "8443" },
            "basePath": {
              ":default": "v2"
            }}}]}})

print(b.to_tuple())
print()
