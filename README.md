# tiff-strip-map

Map classic TIFF IFD metadata and grayscale strip ownership, including aliases and out-of-file evidence.

For Image ingestion maintainers investigating a small grayscale TIFF. Offset/count arrays and inline fields can conceal metadata/strip collisions before pixel decoding.

## Quickstart

Python3.10+; zero runtime dependencies. Wheel builds require setuptools from the normal Python registry.

```sh
git clone https://github.com/nripankadas07/tiff-strip-map.git
cd tiff-strip-map
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/tiff-strip-map --make-example example.tiff
.venv/bin/tiff-strip-map example.tiff
```

Exit0: a2x2 invented image has one strip at bytes122..126 with no ownership overlaps.

Example generators create only an explicitly named new file and refuse overwrite. Reports never modify the input. Windows equivalents use `.venv\Scripts\python.exe` and the installed `.exe`; Windows/macOS have not been executed by this release's Linux CI.

## Contract

Classic TIFF II/MM version42. At most32 acyclic word-aligned IFDs,128 fields per IFD; known field types1..12 have bounded payload extents and inline values up to4 bytes. Width/height, explicit8-bit samples, compression1, grayscale photometric0/1, one sample and contiguous planar layout. Explicit rows-per-strip and exact offset/count array sizes, including final partial strip. Expected raw bytes equal width times strip rows. Strip/strip and strip/metadata overlaps are exit1 findings with no winner policy; exact aliases remain visible.

JSON reports go to stdout. Exit0 means the documented successful result, exit1 a valid finding/incomplete/rejected result, exit2 invalid/unsupported input, I/O or budget failure with stderr and no partial report. Ranges are half-open.

## Limits

8 MiB, width/height/rows1..1000000,4096 decoded values per interpreted tag,4096 strips total, first256 overlaps retained plus omitted count. No BigTIFF, compression, tiles, SubIFDs, color images, pixel decoding, orientation transforms, GeoTIFF/OME interpretation, metadata cleanup or full baseline TIFF conformance validation. Metadata/metadata aliases are not classified.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/tiff-strip-map-check
/tmp/tiff-strip-map-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/tiff-strip-map-check/bin/python
```

[Validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md), [security](SECURITY.md), [MIT license](LICENSE).

Original implementation, prose and invented fixtures developed with AI assistance. No measured performance-superiority or verified production-adoption claim.
