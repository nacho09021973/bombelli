"""Consistency checks for public citation and discovery metadata."""

from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PROJECT_VERSION = "2.1.1"
CONCEPT_DOI = "10.5281/zenodo.20307735"
STALE_VERSION_DOIS = {
    "10.5281/zenodo.20357739",
    "10.5281/zenodo.20743638",
}
PROJECT_URL = "https://nacho09021973.github.io/bombelli/"
ARTICLE_URL = PROJECT_URL + "reviving-bombelli-1987-causal-set-code.html"


def test_public_metadata_uses_stable_concept_doi():
    public_files = [
        ROOT / "README.md",
        ROOT / "OUTREACH.md",
        ROOT / "docs" / "index.html",
        ROOT / "docs" / "reviving-bombelli-1987-causal-set-code.html",
        ROOT / "docs" / "llms.txt",
        ROOT / "docs" / "ai-context.json",
        ROOT / "outreach" / "causal-sets.md",
        ROOT / "outreach" / "reproducibility.md",
        ROOT / "outreach" / "software-preservation.md",
    ]
    for path in public_files:
        contents = path.read_text(encoding="utf-8")
        assert CONCEPT_DOI in contents, path
        for stale_doi in STALE_VERSION_DOIS:
            assert stale_doi not in contents, path


def test_machine_readable_metadata_is_valid():
    for relative in [".zenodo.json", "docs/ai-context.json"]:
        with (ROOT / relative).open(encoding="utf-8") as handle:
            json.load(handle)


def test_release_version_is_synchronized():
    with (ROOT / ".zenodo.json").open(encoding="utf-8") as handle:
        zenodo = json.load(handle)
    with (ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

    assert zenodo["version"] == PROJECT_VERSION
    assert pyproject["project"]["version"] == PROJECT_VERSION
    assert re.search(
        rf'^version: "{re.escape(PROJECT_VERSION)}"$',
        citation,
        flags=re.MULTILINE,
    )
    assert f'doi: "{CONCEPT_DOI}"' in citation


def test_sitemap_lists_the_canonical_pages():
    tree = ET.parse(ROOT / "docs" / "sitemap.xml")
    namespace = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = {
        element.text
        for element in tree.findall("sitemap:url/sitemap:loc", namespace)
    }
    assert PROJECT_URL in urls
    assert ARTICLE_URL in urls
    assert PROJECT_URL + "llms.txt" in urls
    assert PROJECT_URL + "ai-context.json" in urls
