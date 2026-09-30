# Translate your first filter

In this tutorial, you will translate a Sentinel-2 cloud-cover filter into OData without contacting a catalogue. You need Python 3.10 or later, Git, and a terminal. Installation requires network access.

## 1. Create an environment

```console
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pygeofilter-odata-cdse
```

On Windows, activate with `.venv\Scripts\activate` instead. To work from a checkout, replace the last command with `python -m pip install -e .` from the repository root.

## 2. Translate a collection filter

Save this as `first_filter.py`:

```python
from pygeocdse.evaluator import to_cdse

collection = {
    "op": "=",
    "args": [{"property": "Collection/Name"}, "SENTINEL-2"],
}
print(to_cdse(collection))
```

Run `python first_filter.py`. You should see:

```text
Collection/Name eq 'SENTINEL-2'
```

You have generated an OData filter string. No HTTP request has been made.

## 3. Add a cloud-cover condition

Append this to the same file:

```python
cloud_cover = {"op": "<=", "args": [{"property": "cloudCover"}, 20]}
combined = {"op": "and", "args": [collection, cloud_cover]}
print(to_cdse(combined))
```

Run the file again. The second line should be:

```text
Collection/Name eq 'SENTINEL-2' and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le 20)
```

The collection condition addresses a product field directly. The cloud-cover condition searches the product's typed attribute list.

You have built and translated a compound query. Continue with [searching the catalogue](../how-to/search.md), or read [why attributes use typed expressions](../explanation/architecture.md).
