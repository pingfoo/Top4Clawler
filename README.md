# Top4Crawler

This repository contains utilities to download paper metadata and PDFs from the top security conferences (IEEE S\&P, ACM CCS, USENIX Security, NDSS).

## Usage

```bash
pip install -r requirements.txt
python -m top4crawler.main YEAR CONFERENCE [--output FILE]
```

`CONFERENCE` can be one of `sp`, `ccs`, `usenix`, or `ndss`. Data will be printed as JSON or written to the specified output file.

The scraper attempts several known program URLs for each conference. If none of
them are reachable (e.g. because the program page for the given year has not yet
been published), an empty list will be returned.

USENIX Security sometimes uses a two-digit year in its URL, e.g.
`https://www.usenix.org/conference/usenixsecurity23/technical-sessions` for
2023. The scraper tries this pattern in addition to the standard forms.
