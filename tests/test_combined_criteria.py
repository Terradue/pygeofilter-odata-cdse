import unittest
from loguru import logger
import requests
from unittest.mock import patch
from pygeocdse.evaluator import http_invoke
import json
stars = 50


class TestCombinedCql2JsonQueryUrl(unittest.TestCase):
    base_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    def test_filtered_s2_product_name_by_cloudcover(self):
        logger.info(f"\n{'*'*stars}\nTesting test_filtered_s2_product_name_by_cloudcover\n{'*'*stars}\n")
        
        cql2_filter = {
            "op": "and",
            "args": [
                {"op": "eq", "args": [{"property": "Collection/Name"}, "SENTINEL-2"]},
                {"op": "<=", "args": [
                    {"property": "cloudCover"}, 20]},
                {
                    "op": "t_after",
                    "args": [
                        {"property": "ModificationDate"},
                        {"interval": ["2020-10-19T22:50:00Z", "2022-01-01T01:38:00Z"]},
                    ],
                    "exclusive": False,
                },
            ],
        }
        ##########################################################
        ##########################################################
        ## test product name with pygeocdse
        data = http_invoke(base_url=self.base_url, cql2_filter=cql2_filter)
        logger.info(f"Found {data['value'][0]['Name'].replace('.SAFE', '')}")
        self.assertEqual(
            data['value'][0]['Name'].replace('.SAFE', ''),
            "S2B_MSIL1C_20220101T000459_N0301_R130_T52DEK_20220101T004909",
        )
        logger.success("test_filtered_s2_product_name_by_cloudcover passed successfully!")
    def test_filtered_s2_product_name_by_instrument(self):
        logger.info(f"\n{'*'*stars}\nTesting filtered_s2_product_name_by_instrument\n{'*'*stars}\n")
        
        cql2_filter = {
            "op": "and",
            "args": [
                {"op": "eq", "args": [{"property": "Collection/Name"}, "SENTINEL-2"]},
                {"op": "eq", "args": [
                    {"property": "instrumentShortName"}, "AUX"]},
                {
                    "op": "t_after",
                    "args": [
                        {"property": "ModificationDate"},
                        {"interval": ["2020-10-19T22:50:00Z", "2025-02-02T00:40:51.821330Z"]},
                    ],
                    
                }
            ],
        }
        ##########################################################
        ##########################################################
        ## test product name with pygeocdse
        data = http_invoke(base_url=self.base_url, cql2_filter=cql2_filter)
        logger.info(f"Found {data['value'][0]['Name'].replace('.SAFE', '')}")
        self.assertEqual(
            data['value'][0]['Name'].replace('.SAFE', ''),
            "S2A_OPER_AUX_GNSSRD_POD__20171211T090149_V20150703T064934_20150703T235534",
        )
        logger.success("test_filtered_s2_product_name_by_instrument passed successfully!")