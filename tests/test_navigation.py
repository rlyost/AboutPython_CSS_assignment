from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional

try:
    from bs4 import BeautifulSoup  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback when BeautifulSoup isn't installed
    BeautifulSoup = None  # type: ignore


class _NavigationHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_navigation = False
        self.current_label: Optional[str] = None
        self.labels: List[str] = []

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        attr_dict = dict(attrs)
        if tag == "div" and attr_dict.get("id") == "navigation":
            self.in_navigation = True
        elif self.in_navigation and attr_dict.get("class") == "nav_items":
            self.current_label = ""

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if self.current_label is not None and tag in {"p", "li", "span"}:
            label = self.current_label.strip()
            if label:
                self.labels.append(label)
            self.current_label = None
        elif self.in_navigation and tag == "div":
            self.in_navigation = False

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self.current_label is not None:
            self.current_label += data


def load_navigation_labels() -> List[str]:
    project_root = Path(__file__).resolve().parents[1]
    html_path = project_root / "AboutPython.html"
    html_content = html_path.read_text(encoding="utf-8")

    if BeautifulSoup is not None:
        soup = BeautifulSoup(html_content, "html.parser")
        navigation = soup.find(id="navigation")
        if navigation is None:
            raise AssertionError("Navigation element with id 'navigation' not found")
        labels = [element.get_text(strip=True) for element in navigation.find_all(class_="nav_items")]
        return labels

    parser = _NavigationHTMLParser()
    parser.feed(html_content)

    if not parser.labels:
        raise AssertionError("Navigation element with id 'navigation' not found")

    return parser.labels


def test_navigation_contains_expected_labels():
    expected_labels = [
        "About",
        "Downloads",
        "Documentation",
        "Community",
        "News",
        "Events",
    ]

    actual_labels = load_navigation_labels()

    assert actual_labels == expected_labels
