import unicodedata


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.translate(str.maketrans({'Đ': 'D', 'đ': 'd'}))


def strip_accents_lower(text: str) -> str:
    return strip_accents(text).lower()
