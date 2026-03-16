from __future__ import annotations

import re
import unicodedata

WHITESPACE_RE = re.compile(r"[ \t]+")
MULTI_BLANK_RE = re.compile(r"\n{3,}")
WORD_RE = re.compile(r"[a-z0-9\+\#\./-]+")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.strip().lower()).strip("-")
    return slug or "item"


def clean_text(value: str) -> str:
    lines = [WHITESPACE_RE.sub(" ", line).strip() for line in value.replace("\r", "").split("\n")]
    collapsed = "\n".join(line for line in lines if line or any(lines))
    return MULTI_BLANK_RE.sub("\n\n", collapsed).strip()


def split_lines(value: str) -> list[str]:
    return [line.strip() for line in clean_text(value).split("\n") if line.strip()]


def tokenize(value: str) -> list[str]:
    cleaned = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return WORD_RE.findall(cleaned)


def sentence_chunks(value: str) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [chunk.strip(" -") for chunk in chunks if chunk.strip(" -")]

