import argparse
import json
from .scrapers import fetch_ieee_sp, fetch_acm_ccs, fetch_usenix_security, fetch_ndss

SCRAPERS = {
    'sp': fetch_ieee_sp,
    'ccs': fetch_acm_ccs,
    'usenix': fetch_usenix_security,
    'ndss': fetch_ndss,
}

def main():
    parser = argparse.ArgumentParser(description='Fetch Top4 Security conference papers.')
    parser.add_argument('year', type=int, help='Year of the conference')
    parser.add_argument('conference', choices=SCRAPERS.keys(), help='Conference name')
    parser.add_argument('--output', help='Output JSON file')
    args = parser.parse_args()

    papers = SCRAPERS[args.conference](args.year)
    data = [paper.__dict__ for paper in papers]
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
