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


from pygeocdse.evaluator import to_cdse


class TestCDSEEvaluator(unittest.TestCase):
    def setUp(self):
        pass

    def test_comparison_le(self):
        cql2_filter = {"op": "<=", "args": [{"property": "cloudCover"}, 20]}
        expected = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 20)"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_comparison_ge(self):
        cql2_filter = {"op": ">=", "args": [{"property": "cloudCover"}, 20]}
        expected = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value ge 20)"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_comparison_string(self):
        cql2_filter = {
            "op": "=",
            "args": [{"property": "platformShortName"}, "Sentinel-2A"],
        }
        expected = "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'platformShortName' and att/OData.CSC.StringAttribute/Value eq 'Sentinel-2A')"  # this should be all single quotes??
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_comparison_double(self):
        cql2_filter = {"op": "=", "args": [{"property": "cloudCover"}, 20]}
        expected = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value eq 20)"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_comparison_integer(self):
        cql2_filter = {"op": "=", "args": [{"property": "orbitNumber"}, 20]}
        expected = "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value eq 20)"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_collection_name(self):
        cql2_filter = {
            "op": "=",
            "args": [{"property": "Collection/Name"}, "SENTINEL-2"],
        }
        expected = "Collection/Name eq 'SENTINEL-2'"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_in(self):
        cql2_filter = {
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
                    "S6_GRDH_1S",
                ],
            ],
        }

        expected = "(Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'IW_GRHD_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'IW_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'EW_GRDM_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'EW_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S1_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S3_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S4_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S5_GRDH_1S') or Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S6_GRDH_1S'))"

        self.assertEqual(expected, to_cdse(cql2_filter))

    # write test for
    # Collection/Name eq 'SENTINEL-2'
    # and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover'
    # and att/OData.CSC.DoubleAttribute/Value lt 10.00)
    # and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType'
    # and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A')
    # and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection'
    # and att/OData.CSC.StringAttribute/Value eq 'ASCENDING')
    # and ContentDate/Start gt 2022-05-03T00:00:00.000Z
    # and ContentDate/Start lt 2022-05-03T04:00:00.000Z
    def test_several_attributes(self):
        cql2_filter = {
            "op": "and",
            "args": [
                {"op": "<=", "args": [{"property": "cloudCover"}, 10]},
                {"op": "=", "args": [{"property": "productType"}, "S2MSI2A"]},
                {"op": "=", "args": [{"property": "orbitDirection"}, "ASCENDING"]},
                {
                    "op": "t_begins",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {
                            "interval": [
                                "2022-05-03T00:00:00.00Z",
                                "2022-05-03T04:00:00.00Z",
                            ]
                        },
                    ],
                },
            ],
        }

        expected = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 10) and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'ASCENDING') and ContentDate/Start ge 2022-05-03T00:00:00Z and ContentDate/Start le 2022-05-03T04:00:00Z"
        current = to_cdse(cql2_filter)

        self.assertEqual(expected, current)
