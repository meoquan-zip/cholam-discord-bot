import re
import unicodedata


def strip_accents(text: str) -> str:
    text = unicodedata.normalize('NFD', text.strip())
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.translate(str.maketrans({'Đ': 'D', 'đ': 'd'}))


def remove_invisible(text: str) -> str:
    return re.compile(r'[\u200B-\u200D\u2060\u180E\u00A0]').sub('', text)


def normalise(text: str) -> str:
    text = strip_accents(text)
    text = remove_invisible(text)
    return re.sub(r'[^a-z0-9]', '', text.lower())
