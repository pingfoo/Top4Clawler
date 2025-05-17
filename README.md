# Top4Crawler

This repository contains utilities to download paper metadata and PDFs from the top security conferences (IEEE S\&P, ACM CCS, USENIX Security, NDSS).

## Usage

```bash
pip install -r requirements.txt
python -m top4crawler.main YEAR CONFERENCE [--output FILE]
```

`CONFERENCE` can be one of `sp`, `ccs`, `usenix`, or `ndss`. Data will be printed as JSON or written to the specified output file.
