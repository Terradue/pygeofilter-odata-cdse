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

from pygeocdse.odata_attributes import get_attribute_type


class TestOdataAttributes(unittest.TestCase):
    def test_get_attribute_type_string(self):
        attribute_name = "platformShortName"
        expected = "String"
        self.assertEqual(expected, get_attribute_type(attribute_name))

    def test_get_attribute_type_integer(self):
        attribute_name = "relativeOrbitNumber"
        expected = "Integer"
        self.assertEqual(expected, get_attribute_type(attribute_name))

    def test_get_attribute_type_double(self):
        attribute_name = "illuminationZenithAngle"
        expected = "Double"
        self.assertEqual(expected, get_attribute_type(attribute_name))

    def test_get_attribute_type_dateoffset(self):
        attribute_name = "processingDate"
        expected = "DateTimeOffset"
        self.assertEqual(expected, get_attribute_type(attribute_name))

    def test_get_attribute_type_not_found(self):
        attribute_name = "not_found"
        with self.assertRaises(ValueError):
            get_attribute_type(attribute_name)
