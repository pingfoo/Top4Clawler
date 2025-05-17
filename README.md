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

For IEEE S&P you can optionally set the environment variable `IEEE_API_KEY` to
fetch metadata via the IEEE Xplore API (using predefined publication IDs). When
the API key is absent or the year is unknown, the scraper falls back to parsing
the conference website.

ACM CCS metadata is retrieved via Crossref when possible and falls back to
scraping the program page. USENIX Security and NDSS remain purely
scraper-based but include several candidate URLs per year.
