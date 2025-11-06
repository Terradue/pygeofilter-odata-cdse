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

import unittest

from pygeocdse.evaluator import http_invoke


class TestCDSEIntegration(unittest.TestCase):

    def setUp(self):
        pass

    def test_cdse_invokation(self):
        cql2_filter = {
            "op": "and",
            "args": [
                {
                    "op": "eq",
                    "args": [
                        {"property": "Collection/Name"},
                        "SENTINEL-2"
                    ]
                },
                {
                    "op": "eq",
                    "args": [
                        {"property": "productType"},
                        "S2MSI1C"
                    ]
                },
                {
                    "op": "s_intersects",
                    "args": [
                        {"property": "geometry"},
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-11, 35],
                                    [27.5, 35],
                                    [27.5, 60],
                                    [-11, 60],
                                    [-11, 35],
                                ]
                            ],
                        },
                    ],
                }
            ],
        }

        data = http_invoke("https://catalogue.dataspace.copernicus.eu/odata/v1/Products", cql2_filter)

        self.assertIsNotNone(data, f"Expected JSON data")

    def test_cdse_invokation_2(self):
        '''
        Collection/Name eq 'SENTINEL-1'
        and (Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'IW_GRHD_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'IW_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'EW_GRDM_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'EW_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S1_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S3_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S4_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S5_GRDH_1S')
        or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S6_GRDH_1S'))
        and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON((-117.861 33.138,-102.217 32.027,-98.965 29.306,-96.592 27.216,-88.945 26.667,-85.078 26.274,-81.123 26.589,-72.51 26.746,-69.961 25.006,-66.973 23.161,-61.787 19.311,-56.953 14.52,-51.152 9.882,-41.748 2.636,-30.586 -3.864,-29.18 -17.644,-47.988 -35.317,-54.844 -54.877,-74.004 -57.421,-86.484 -40.581,-86.484 -19.643,-98.262 -1.23,-114.258 20.797,-119.004 29.382,-117.861 33.138))')
        '''

        cql2_filter = {
            "op": "and",
            "args": [
                {
                    "op": "eq",
                    "args": [
                        {"property": "Collection/Name"},
                        "SENTINEL-1"
                    ]
                },
                {
                    "op": "in",
                    "args": [
                        {"property": "productType"},
                        [
                            "IW_GRHD_1S",
                            "IW_GRDH_1S",
                            "EW_GRDM_1S",
                            "EW_GRDH_1S",
                            "S1_GRDH_1S",
                            "S2_GRDH_1S",
                            "S3_GRDH_1S",
                            "S4_GRDH_1S",
                            "S5_GRDH_1S",
                            "S6_GRDH_1S"
                        ]
                    ]
                },
                {
                    "op": "s_intersects",
                    "args": [
                        {"property": "geometry"},
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-117.861, 33.138],
                                    [-102.217, 32.027],
                                    [-98.965, 29.306],
                                    [-96.592, 27.216],
                                    [-88.945, 26.667],
                                    [-85.078, 26.274],
                                    [-81.123, 26.589],
                                    [-72.51, 26.746],
                                    [-69.961, 25.006],
                                    [-66.973, 23.161],
                                    [-61.787, 19.311],
                                    [-56.953, 14.52],
                                    [-51.152, 9.882],
                                    [-41.748, 2.636],
                                    [-30.586, -3.864],
                                    [-29.18, -17.644],
                                    [-47.988, -35.317],
                                    [-54.844, -54.877],
                                    [-74.004, -57.421],
                                    [-86.484, -40.581],
                                    [-86.484, -19.643],
                                    [-98.262, -1.23],
                                    [-114.258, 20.797],
                                    [-119.004, 29.382],
                                    [-117.861, 33.138]
                                ]
                            ],
                        },
                    ],
                }
            ],
        }

        data = http_invoke("https://catalogue.dataspace.copernicus.eu/odata/v1/Products", cql2_filter)

        self.assertIsNotNone(data, f"Expected JSON data")
