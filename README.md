# Comicon

Comicon is a lightweight comic converter library between CBZ, PDF, EPUB, and MOBI that preserves metadata. Once Comicon has converted a comic, it is **guaranteed** that the reverse conversion will restore the original comic with all of its original metadata.

## Usage

For a command line interface, please see [Mandown](https://github.com/potatoeggy/mandown).

```python
import comicon

comicon.convert("comic.cbz", "comic.epub")
```

## Installation

Amazon's **Kindlegen** is required if you want to convert to MOBI. See [here](https://github.com/ciromattia/kcc/issues/371) for more information.

Comicon is available from PyPI:

```
pip install comicon
```

## Supported conversions

| Format | Convert from?      | Convert to?        | Supports table of contents? |
| ------ | ------------------ | ------------------ | --------------------------- |
| CBZ    | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:          |
| EPUB   | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:          |
| PDF    | :heavy_check_mark: | :heavy_check_mark: | :x:                         |
| MOBI   | :x:                | :heavy_check_mark: | :heavy_check_mark:          |

### Format discrepancies

- Formats that do not support a table of contents will encode them so that they are restored if converted back to a format that supports them.
- PDF does not support importing genre data due to a lack of library support. This may be worked around in the future.

## Notes

Under the hood, Comicon converts each format into the **Comicon Intermediate Representation (CIR)** — more or less a strictly structured folder, which allows for many guarantees to be made for each input and output plugin. See `comicon.cirtools` for more information.

For new input and output formats to be added, they should be added in `comicon.inputs` or `comicon.outputs` respectively as a new module and in the `__init__.py` file(s).
