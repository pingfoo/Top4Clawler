import os
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional, Dict

# Known IEEE S&P publication numbers (used for the IEEE Xplore API)
IEEE_SP_PUB_IDS: Dict[int, str] = {
    2021: "9519381",
}


def _safe_get(urls: List[str]) -> Optional[str]:
    """Return the body of the first successfully retrieved URL."""
    headers = {"User-Agent": "top4crawler"}
    for url in urls:
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.text
        except requests.RequestException:
            continue
    print(f"Could not fetch any page from: {', '.join(urls)}")
    return None

@dataclass
class Paper:
    title: str
    authors: List[str]
    pdf_url: Optional[str]
    abstract: Optional[str]

def fetch_ieee_sp(year: int) -> List[Paper]:
    """Fetch papers from IEEE S&P for the given year."""

    # For 2021 the IEEE Xplore Metadata API can be used if an API key is
    # available.  This provides more reliable results than scraping.
    if year in IEEE_SP_PUB_IDS:
        api_key = os.environ.get("IEEE_API_KEY")
        if api_key:
            pub_id = IEEE_SP_PUB_IDS[year]
            url = (
                "https://ieeexploreapi.ieee.org/api/v1/search/articles"
                f"?publication_number={pub_id}&max_records=200&apikey={api_key}"
            )
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                data = resp.json()
            except requests.RequestException:
                data = None
            if data and data.get("articles"):
                papers = []
                for art in data["articles"]:
                    title = art.get("title", "").strip()
                    authors = [a.get("full_name", "").strip() for a in art.get("authors", [])]
                    pdf_url = art.get("pdf_url")
                    abstract = art.get("abstract")
                    papers.append(Paper(title, authors, pdf_url, abstract))
                return papers
        else:
            print("IEEE_API_KEY not set; falling back to scraping.")

    # Fallback to scraping the conference program page
    candidates = [
        f"https://www.ieee-security.org/TC/SP{year}/program.html",
        f"https://sp{year}.ieee-security.org/program.html",
    ]
    text = _safe_get(candidates)
    if text is None:
        return []

    soup = BeautifulSoup(text, "html.parser")
    papers = []
    for item in soup.select("div.paper"):
        title = item.select_one("div.title").get_text(strip=True)
        authors = [a.strip() for a in item.select_one("div.authors").get_text().split(',')]
        pdf_link_tag = item.find('a', href=lambda x: x and x.endswith('.pdf'))
        pdf_url = pdf_link_tag['href'] if pdf_link_tag else None
        abstract_tag = item.find_next('p')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
        papers.append(Paper(title, authors, pdf_url, abstract))
    return papers

def fetch_acm_ccs(year: int) -> List[Paper]:
    """Fetch papers from ACM CCS for the given year."""
    if year == 2021:
        # Use Crossref to retrieve metadata for CCS 2021 since ACM does not
        # provide a public API.  This query filters by year and conference name.
        url = (
            "https://api.crossref.org/works?"
            "query=ACM%20SIGSAC%20Conference%20on%20Computer%20and%20Communications%20Security"
            f"&filter=from-pub-date:{year}-01-01,until-pub-date:{year}-12-31&rows=1000"
        )
        try:
            resp = requests.get(url, headers={"User-Agent": "top4crawler"})
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            data = None
        if data and data.get("message", {}).get("items"):
            papers = []
            for item in data["message"]["items"]:
                title = item.get("title", [""])[0]
                authors = [
                    f"{a.get('given', '').strip()} {a.get('family', '').strip()}".strip()
                    for a in item.get("author", [])
                ]
                pdf_url = None
                for link in item.get("link", []):
                    if link.get("content-type") == "application/pdf":
                        pdf_url = link.get("URL")
                        break
                abstract = item.get("abstract")
                papers.append(Paper(title, authors, pdf_url, abstract))
            return papers

    # Fallback to scraping the conference website
    candidates = [
        f"https://www.sigsac.org/ccs/CCS{year}/program.html",
        f"https://www.sigsac.org/ccs/CCS{year}/program/",
    ]
    text = _safe_get(candidates)
    if text is None:
        return []
    soup = BeautifulSoup(text, "html.parser")
    papers = []
    for item in soup.select("div.paper"):
        title = item.select_one("h3").get_text(strip=True)
        authors = [a.strip() for a in item.select_one("p.authors").get_text().split(',')]
        pdf_tag = item.find('a', href=lambda x: x and x.endswith('.pdf'))
        pdf_url = pdf_tag['href'] if pdf_tag else None
        abstract_tag = item.find('div', class_='abstract')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
        papers.append(Paper(title, authors, pdf_url, abstract))
    return papers

def fetch_usenix_security(year: int) -> List[Paper]:
    """Fetch papers from USENIX Security for the given year."""
    if year == 2021:
        url = "https://www.usenix.org/conference/usenixsecurity21/technical-sessions"
        text = _safe_get([url])
        if text is None:
            return []
        soup = BeautifulSoup(text, "html.parser")
        papers = []
        for a in soup.find_all('a', href=lambda h: h and h.endswith('.pdf')):
            title = a.get_text(strip=True)
            pdf_url = a['href']
            # Authors are not explicitly structured on this page; omit them
            papers.append(Paper(title, [], pdf_url, None))
        return papers

    candidates = [
        f"https://www.usenix.org/conference/usenixsecurity{year}/presentation",
        f"https://www.usenix.org/conference/usenixsecurity{year}/program",
    ]
    text = _safe_get(candidates)
    if text is None:
        return []
    soup = BeautifulSoup(text, "html.parser")
    papers = []
    for item in soup.select("div.node--type-paper"):
        title = item.select_one("h3.node-title").get_text(strip=True)
        authors_tag = item.find('div', class_='field--name-field-paper-authors')
        authors = [a.strip() for a in authors_tag.get_text(separator=',').split(',')]
        pdf_tag = item.find('a', href=lambda x: x and x.endswith('.pdf'))
        pdf_url = pdf_tag['href'] if pdf_tag else None
        abstract_tag = item.find('div', class_='field--name-field-abstract')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
        papers.append(Paper(title, authors, pdf_url, abstract))
    return papers

def fetch_ndss(year: int) -> List[Paper]:
    """Fetch papers from NDSS for the given year."""
    if year == 2021:
        index_url = "https://www.ndss-symposium.org/ndss2021/accepted-papers/"
        text = _safe_get([index_url])
        if text is None:
            return []
        soup = BeautifulSoup(text, "html.parser")
        papers = []
        detail_links = [a['href'] for a in soup.find_all('a', href=lambda h: h and '/ndss-paper/' in h)]
        for link in detail_links:
            detail_text = _safe_get([link])
            if not detail_text:
                continue
            dsoup = BeautifulSoup(detail_text, 'html.parser')
            title_tag = dsoup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ''
            authors_tag = title_tag.find_next('p') if title_tag else None
            authors_text = authors_tag.get_text(strip=True) if authors_tag else ''
            authors = [a.strip() for a in authors_text.split(',')] if authors_text else []
            pdf_tag = dsoup.find('a', string="Paper")
            pdf_url = pdf_tag['href'] if pdf_tag else None
            abstract_tag = dsoup.find('p', class_='abstract')
            abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
            papers.append(Paper(title, authors, pdf_url, abstract))
        return papers

    candidates = [
        f"https://www.ndss-symposium.org/ndss{year}-program/",
        f"https://www.ndss-symposium.org/ndss{year}/program/",
    ]
    text = _safe_get(candidates)
    if text is None:
        return []
    soup = BeautifulSoup(text, "html.parser")
    papers = []
    for item in soup.select("div.paper"):
        title = item.select_one("div.title").get_text(strip=True)
        authors = [a.strip() for a in item.select_one("div.authors").get_text().split(',')]
        pdf_tag = item.find('a', href=lambda x: x and x.endswith('.pdf'))
        pdf_url = pdf_tag['href'] if pdf_tag else None
        abstract_tag = item.find_next('p')
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else None
        papers.append(Paper(title, authors, pdf_url, abstract))
    return papers
