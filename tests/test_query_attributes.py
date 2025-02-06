import unittest

from loguru import logger
from pygeofilter.parsers.cql2_json import parse as json_parse
from pygeofilter.util import IdempotentDict

from pygeocdse.evaluator import to_cdse


# see https://documentation.dataspace.copernicus.eu/APIs/OData.html#query-by-attributes
# To search for products by StringAttribute, the filter query should be built with the following structure:
# Attributes/OData.CSC.StringAttribute/any(att:att/Name eq ‘[Attribute.Name]’ and att/OData.CSC.StringAttribute/Value eq ‘[Attribute.Value]’)
class TestQueryAttributes(unittest.TestCase):

    def setUp(self):
        pass

    def test_search_string_attribute(self):
        cql2_filter = {"op": "eq", "args": [{"property": "platformShortName"}, "Sentinel-2A"]}
        expected = "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'platformShortName' and att/OData.CSC.StringAttribute/Value eq 'Sentinel-2A')"
        self.assertEqual(
            expected, to_cdse(cql2_filter)
        )

    def test_search_integer_attribute(self):
        cql2_filter = {"op": "eq", "args": [{"property": "orbitNumber"}, 20]}
        expected = "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' and att/OData.CSC.IntegerAttribute/Value eq 20)"
        self.assertEqual(
            expected, to_cdse(cql2_filter)
        )

    def test_search_double_attribute(self):
        cql2_filter = {"op": "eq", "args": [{"property": "cloudCover"}, 20]}
        expected = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value eq 20)"
        self.assertEqual(
            expected, to_cdse(cql2_filter)
        )

    def test_search_date_time_offset_attribute(self):
        cql2_filter = {
            "op": "eq",
            "args": [{"property": "processingDate"}, "2023-02-01T00:00:00Z"],
        }
        expected = "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'processingDate' and att/OData.CSC.DateTimeOffsetAttribute/Value eq 2023-02-01T00:00:00Z)"
        self.assertEqual(
            expected, to_cdse(cql2_filter)
        )
