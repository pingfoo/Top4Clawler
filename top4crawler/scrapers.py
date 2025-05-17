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
