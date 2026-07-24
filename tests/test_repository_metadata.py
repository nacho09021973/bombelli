"""Consistency checks for public citation and discovery metadata."""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION_DOI = "10.5281/zenodo.20743638"
PREVIOUS_VERSION_DOI = "10.5281/zenodo.20357739"
PROJECT_URL = "https://nacho09021973.github.io/bombelli/"
ARTICLE_URL = PROJECT_URL + "reviving-bombelli-1987-causal-set-code.html"


def test_public_metadata_uses_current_version_doi():
    current_files = [
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
    for path in current_files:
        assert CURRENT_VERSION_DOI in path.read_text(encoding="utf-8"), path

    for relative in [
        "OUTREACH.md",
        "docs/reviving-bombelli-1987-causal-set-code.html",
        "outreach/causal-sets.md",
        "outreach/reproducibility.md",
        "outreach/software-preservation.md",
    ]:
        path = ROOT / relative
        assert PREVIOUS_VERSION_DOI not in path.read_text(encoding="utf-8"), path


def test_machine_readable_metadata_is_valid():
    for relative in [".zenodo.json", "docs/ai-context.json"]:
        with (ROOT / relative).open(encoding="utf-8") as handle:
            json.load(handle)


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
