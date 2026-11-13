"""Fast structural checks for the static product surface.

These tests intentionally use only the standard library: they catch broken
navigation, inaccessible native controls, stale architecture copy, and a deck
that accidentally stops loading the parity-tested finance module.
"""

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
HTML_FILES = tuple(sorted(SITE.glob("*.html")))


class _DocumentContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = None
        self.ids = set()
        self.label_targets = set()
        self.range_ids = set()
        self.has_title = False
        self.has_viewport = False
        self.has_primary_nav = False
        self.step_buttons = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "title":
            self.has_title = True
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        if tag == "nav" and values.get("aria-label") == "Primary":
            self.has_primary_nav = True
        if tag == "label" and values.get("for"):
            self.label_targets.add(values["for"])
        if tag == "input" and values.get("type") == "range":
            assert values.get("id"), "Every range input must have an id"
            self.range_ids.add(values["id"])
        if tag == "button" and "step" in (values.get("class") or "").split():
            assert values.get("aria-label"), "Journey step buttons need an accessible name"
            self.step_buttons += 1


def _parse(path: Path) -> _DocumentContractParser:
    parser = _DocumentContractParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def test_static_pages_have_basic_document_and_navigation_contracts():
    assert HTML_FILES
    for path in HTML_FILES:
        parsed = _parse(path)
        assert parsed.html_lang == "en", path
        assert parsed.has_title, path
        assert parsed.has_viewport, path
        assert parsed.has_primary_nav, path


def test_native_range_controls_have_programmatic_labels():
    parsed = _parse(SITE / "card1.html")
    assert parsed.range_ids
    assert parsed.range_ids <= parsed.label_targets
    assert parsed.step_buttons == 4


def test_deck_uses_the_parity_tested_finance_module():
    source = (SITE / "companion.html").read_text(encoding="utf-8")
    assert '<script src="finance.js"></script>' in source
    expected_calls = {
        "pv", "fv", "perpetuity", "growingPerpetuity", "annuityPV",
        "growingAnnuityPV", "npv", "irr", "ear", "loanPayment",
        "bondPrice", "ytm", "capm", "ddm", "effectiveBets",
    }
    assert {name for name in expected_calls if f"Finance.{name}(" in source} == expected_calls


def test_project_map_does_not_advertise_removed_local_services():
    source = (SITE / "app.html").read_text(encoding="utf-8")
    for stale_reference in ("frontend/src", "FastAPI", "localhost:8000", "core/data/"):
        assert stale_reference not in source
