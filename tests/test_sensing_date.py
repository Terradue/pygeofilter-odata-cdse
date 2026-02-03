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


# see https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-sensing-date
class TestSensingDate(unittest.TestCase):
    def setUp(self):
        pass

    """
    timestamp
    """

    def test_content_date_start(self):
        # To search for products acquired between two dates
        cql2_filter = {
            "op": "and",
            "args": [
                {
                    "op": "t_after",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {"timestamp": "2023-02-01T00:00:00Z"},
                    ],
                },
                {
                    "op": "t_before",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {"timestamp": "2023-02-28T23:59:59Z"},
                    ],
                },
            ],
        }
        expected = "ContentDate/Start gt 2023-02-01T00:00:00Z and ContentDate/Start lt 2023-02-28T23:59:59Z"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_content_date_start_inclusive(self):
        # Usually, there are two parameters describing the ContentDate (Acquisition Dates) for a product - Start and End.
        # Depending on what the user is looking for, these parameters can be mixed
        cql2_filter = {
            "op": "and",
            "args": [
                {
                    "op": "t_begins",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {"timestamp": "2023-02-01T00:00:00Z"},
                    ],
                },
                {
                    "op": "t_ends",
                    "args": [
                        {"property": "ContentDate/End"},
                        {"timestamp": "2023-02-28T23:59:59Z"},
                    ],
                },
            ],
        }
        expected = "ContentDate/Start ge 2023-02-01T00:00:00Z and ContentDate/End le 2023-02-28T23:59:59Z"
        self.assertEqual(expected, to_cdse(cql2_filter))

    """
    interval
    """

    def test_content_date_start_inclusive_intervals(self):
        # Usually, there are two parameters describing the ContentDate (Acquisition Dates) for a product - Start and End.
        # Depending on what the user is looking for, these parameters can be mixed
        cql2_filter = {
            "op": "and",
            "args": [
                {
                    "op": "t_after",
                    "args": [
                        {"property": "ContentDate/Start"},
                        {"interval": ["2023-02-01T00:00:00Z", "2023-02-01T23:59:59Z"]},
                    ],
                },
                {
                    "op": "t_before",
                    "args": [
                        {"property": "ContentDate/End"},
                        {"interval": ["2023-02-28T00:00:00Z", "2023-02-28T23:59:59Z"]},
                    ],
                },
            ],
        }
        expected = "ContentDate/Start gt 2023-02-01T00:00:00Z and ContentDate/Start le 2023-02-01T23:59:59Z and ContentDate/End ge 2023-02-28T00:00:00Z and ContentDate/End lt 2023-02-28T23:59:59Z"
        self.assertEqual(expected, to_cdse(cql2_filter))

    """
    interval with deltas
    """

    def test_content_date_start_inclusive_invalid_delta_interval(self):
        cql2_filter = {
            "op": "t_after",
            "args": [
                {"property": "ContentDate/Start"},
                {"interval": ["PT4S", "PT4S"]},
            ],
        }
        """
        expected = "ContentDate/Start gt 2023-02-01T00:00:00Z and ContentDate/Start le 2023-02-01T23:59:59Z"
        self.assertEqual(
            expected, to_cdse(cql2_filter)
        )
        """
        with self.assertRaises(ValueError):
            to_cdse(cql2_filter)

    def test_content_date_start_inclusive_delta_interval(self):
        cql2_filter = {
            "op": "t_after",
            "args": [
                {"property": "ContentDate/Start"},
                {"interval": ["2023-02-28T00:00:00Z", "PT4S"]},
            ],
        }
        expected = "ContentDate/Start gt 2023-02-28T00:00:00Z and ContentDate/Start le 2023-02-28T00:00:04Z"
        self.assertEqual(expected, to_cdse(cql2_filter))

    def test_content_date_start_inclusive_delta2_interval(self):
        cql2_filter = {
            "op": "t_after",
            "args": [
                {"property": "ContentDate/Start"},
                {"interval": ["PT4S", "2023-02-28T00:00:00Z"]},
            ],
        }
        expected = "ContentDate/Start gt 2023-02-27T23:59:56Z and ContentDate/Start le 2023-02-28T00:00:00Z"
        self.assertEqual(expected, to_cdse(cql2_filter))
