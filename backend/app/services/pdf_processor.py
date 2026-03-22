import logging
import re
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class PageContent:
    def __init__(self, text: str, page_number: int):
        self.text = text
        self.page_number = page_number


def _collapse_spaced(match: re.Match) -> str:
    return match.group(0).replace(" ", "")


def clean_extracted_text(text: str) -> str:
    """Fix common PDF extraction artifacts like spaced-out characters."""
    text = re.sub(r"(?<!\S)[\w\-](?: [\w\-]){2,}(?!\S)", _collapse_spaced, text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    lines = []
    for line in text.splitlines():
        lines.append(line.strip())
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(file_path: Path) -> list[PageContent]:
    """Extract text from a PDF file, returning content per page."""
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}")

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("PDF is encrypted and could not be decrypted.")

    pages: list[PageContent] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = clean_extracted_text(text)
        if text:
            pages.append(PageContent(text=text, page_number=i + 1))

    if not pages:
        raise ValueError(
            "No text content found in PDF. The file may contain only images or scanned pages."
        )

    return pages
