from datetime import date, datetime, timedelta

import pytest

from pygeocdse.evaluator import date_format, to_cdse


@pytest.mark.parametrize(
    ("literal", "expected"),
    [
        ("O'Brien", "'O''Brien'"),
        ("'quoted'", "'''quoted'''"),
        ("x' or true or 'y", "'x'' or true or ''y'"),
        ("", "''"),
    ],
)
def test_string_literals(literal: str, expected: str) -> None:
    assert to_cdse({"op": "=", "args": [{"property": "processorName"}, literal]}) == (
        "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processorName' "
        f"and att/OData.CSC.StringAttribute/Value eq {expected})"
    )
    assert to_cdse({"op": "=", "args": [{"property": "Collection/Name"}, literal]}) == (
        f"Collection/Name eq {expected}"
    )


@pytest.mark.parametrize(("literal", "expected"), [(True, "true"), (False, "false")])
def test_boolean_literals(literal: bool, expected: str) -> None:
    assert to_cdse({"op": "=", "args": [{"property": "sliceProductFlag"}, literal]}) == (
        "Attributes/OData.CSC.BooleanAttribute/any(att:att/Name eq 'sliceProductFlag' "
        f"and att/OData.CSC.BooleanAttribute/Value eq {expected})"
    )


def test_in_escapes_string_options() -> None:
    assert to_cdse(
        {"op": "in", "args": [{"property": "processorName"}, ["O'Brien", "D'Angelo"]]}
    ) == (
        "(Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processorName' "
        "and att/OData.CSC.StringAttribute/Value eq 'O''Brien') or "
        "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'processorName' "
        "and att/OData.CSC.StringAttribute/Value eq 'D''Angelo'))"
    )


@pytest.mark.parametrize("operator", ["and", "or"])
def test_negated_compound_expression(operator: str) -> None:
    expression = {
        "op": operator,
        "args": [
            {"op": "=", "args": [{"property": "orbitNumber"}, 1]},
            {"op": "=", "args": [{"property": "relativeOrbitNumber"}, 2]},
        ],
    }
    expected = (
        "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'orbitNumber' "
        "and att/OData.CSC.IntegerAttribute/Value eq 1) "
        f"{operator} "
        "Attributes/OData.CSC.IntegerAttribute/any(att:att/Name eq 'relativeOrbitNumber' "
        "and att/OData.CSC.IntegerAttribute/Value eq 2)"
    )
    if operator == "or":
        expected = f"({expected})"
    assert to_cdse({"op": "not", "args": [expression]}) == f"not ({expected})"


def test_nested_negation_preserves_grouping() -> None:
    expression = {
        "op": "not",
        "args": [
            {
                "op": "and",
                "args": [
                    {"op": "=", "args": [{"property": "Collection/Name"}, "A"]},
                    {
                        "op": "not",
                        "args": [
                            {
                                "op": "or",
                                "args": [
                                    {"op": "=", "args": [{"property": "Collection/Name"}, "B"]},
                                    {"op": "=", "args": [{"property": "Collection/Name"}, "C"]},
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
    }
    assert to_cdse(expression) == (
        "not (Collection/Name eq 'A' and not ((Collection/Name eq 'B' or Collection/Name eq 'C')))"
    )


@pytest.mark.parametrize(
    "timestamp",
    [
        "2024-01-01T10:00:00.123456Z",
        "2024-01-01T12:00:00.123456+02:00",
        "2024-01-01T05:00:00.123456-05:00",
        "2024-01-01T15:30:00.123456+05:30",
    ],
)
@pytest.mark.parametrize(
    ("operator", "expected"),
    [("t_begins", "ge"), ("t_ends", "le"), ("t_before", "lt"), ("t_after", "gt")],
)
def test_equivalent_timestamp_offsets(timestamp: str, operator: str, expected: str) -> None:
    assert (
        to_cdse(
            {"op": operator, "args": [{"property": "ContentDate/Start"}, {"timestamp": timestamp}]}
        )
        == f"ContentDate/Start {expected} 2024-01-01T10:00:00.123456Z"
    )


@pytest.mark.parametrize("structured", [True, False])
def test_date_attribute_normalizes_timestamps(structured: bool) -> None:
    timestamp = "2024-01-01T00:30:00.000001+02:00"
    assert to_cdse(
        {
            "op": "=",
            "args": [
                {"property": "processingDate"},
                {"timestamp": timestamp} if structured else timestamp,
            ],
        }
    ) == (
        "Attributes/OData.CSC.DateTimeOffsetAttribute/any(att:att/Name eq 'processingDate' "
        "and att/OData.CSC.DateTimeOffsetAttribute/Value eq 2023-12-31T22:30:00.000001Z)"
    )


def test_interval_preserves_offsets_and_fractional_seconds() -> None:
    assert to_cdse(
        {
            "op": "t_begins",
            "args": [
                {"property": "ContentDate/Start"},
                {"interval": ["2024-01-01T12:00:00.123456+02:00", "PT0.5S"]},
            ],
        }
    ) == (
        "ContentDate/Start ge 2024-01-01T10:00:00.123456Z and "
        "ContentDate/Start le 2024-01-01T10:00:00.623456Z"
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2024, 1, 1), "2024-01-01T00:00:00Z"),
        (datetime(2024, 1, 1, 12), "2024-01-01T12:00:00Z"),
        ("2024-01-01T12:00:00+02:00", "2024-01-01T10:00:00Z"),
        ("2024-01-01T23:30:00-02:00", "2024-01-02T01:30:00Z"),
    ],
)
def test_date_format(value: str | date, expected: str) -> None:
    assert date_format(value) == expected


@pytest.mark.parametrize("value", [None, timedelta(seconds=1)])
def test_date_format_requires_concrete_date(value: timedelta | None) -> None:
    with pytest.raises(ValueError, match="A concrete date is required"):
        date_format(value)
