import re


def normalize_company_name(name: str) -> str:
    """
    Normalizes company name for consistent caching.
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
