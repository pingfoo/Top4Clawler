# Repository Guidelines

This project provides command line utilities to fetch paper metadata and PDF links from the top four security conferences (IEEE S&P, ACM CCS, USENIX Security, NDSS).

## Development
- Python 3 is used for all code in `top4crawler`.
- Each scraper must attempt multiple known program URLs using the helper `_safe_get` and return an empty list if none are reachable. Where possible, fall back to open sources such as DBLP or Crossref.
- IEEE S&P scraping may use the IEEE Xplore API when an `IEEE_API_KEY` environment variable is available.
- Update `README.md` whenever user‑visible behavior changes.

## Testing
- Run `python -m py_compile top4crawler/*.py` to verify syntax after modifying code.
- Network access may not be available during testing. Use local HTML or mocks instead of real HTTP requests.
