# Copyright 2025 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pygeocdse.sentinel1 import SENTINEL1
from pygeocdse.sentinel1rtc import SENTINEL1RTC
from pygeocdse.sentinel2 import SENTINEL2
from pygeocdse.sentinel3 import SENTINEL3
from pygeocdse.sentinel5p import SENTINEL5P


# TODO: import all attributes from all satellites
# see https://documentation.dataspace.copernicus.eu/APIs/OData.html#list-of-odata-query-attributes-by-collection
# GLOBAL-MOSAICS
# SMOS
# ENVISAT
# LANDSAT-5
# LANDSAT-7
# LANDSAT-8
# COP-DEM
# TERRAAQUA
# S2GLC
# CCM
ADDITIONAL_ATTRIBUTES = ["Collection/Name", "PublicationDate", "ModificationDate"]

ALL_ATTRIBUTES = [ SENTINEL1, SENTINEL2, SENTINEL3, SENTINEL5P ]


def get_attribute_type(attribute_name):
    if attribute_name in ADDITIONAL_ATTRIBUTES:
        return ""

    for attribute in ALL_ATTRIBUTES:
        type = attribute.get(attribute_name)
        if type is not None:
            return type
    raise ValueError(f"Attribute {attribute_name} not found in attribute list")
