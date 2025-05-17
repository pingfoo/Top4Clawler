import os
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional


def _safe_get(urls: List[str]) -> Optional[str]:
    """Return the body of the first successfully retrieved URL."""
    for url in urls:
        try:
            resp = requests.get(url)
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
    pub_ids = {
        2021: "9519381",
        2020: "9097518",
        2019: "8803633",
        2018: "8355477",
        2017: "7946416",
        2022: "9749231",
        2023: "10191403",
        2024: "11000000",  # placeholder
    }

    api_key = os.getenv("IEEE_API_KEY")
    if api_key and year in pub_ids:
        url = (
            f"https://ieeexploreapi.ieee.org/api/v1/search/articles?"
            f"publication_number={pub_ids[year]}&apikey={api_key}"
        )
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                papers = []
                for art in data.get("articles", []):
                    title = art.get("title", "")
                    authors = [a.get("full_name", "") for a in art.get("authors", [])]
                    pdf_url = art.get("pdf_url")
                    abstract = art.get("abstract")
                    papers.append(Paper(title, authors, pdf_url, abstract))
                if papers:
                    return papers
        except requests.RequestException:
            pass

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
    params = {
        "filter": f"member:320,from-pub-date:{year}-01-01,until-pub-date:{year}-12-31",
        "rows": 1000,
    }
    headers = {"User-Agent": "Top4Crawler/0.1"}
    try:
        resp = requests.get("https://api.crossref.org/v1/works", params=params, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("message", {}).get("items", [])
            papers = []
            for it in items:
                titles = it.get("title", [])
                if not titles:
                    continue
                container = "".join(it.get("container-title", []))
                if "Communications Security" not in container:
                    continue
                title = titles[0]
                authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in it.get("author", [])]
                pdf_url = None
                for link in it.get("link", []):
                    if link.get("content-type") == "application/pdf":
                        pdf_url = link.get("URL")
                        break
                abstract = it.get("abstract")
                papers.append(Paper(title, authors, pdf_url, abstract))
            if papers:
                return papers
    except requests.RequestException:
        pass

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
    candidates = [
        f"https://www.usenix.org/conference/usenixsecurity{year}/technical-sessions",
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
    candidates = [
        f"https://www.ndss-symposium.org/ndss{year}-program/",
        f"https://www.ndss-symposium.org/ndss{year}/program/",
        f"https://www.ndss-symposium.org/ndss{year}/accepted-papers/",
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
