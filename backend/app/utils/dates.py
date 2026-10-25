import re
from datetime import datetime, date, timezone
from typing import Optional, Tuple

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def parse_date_string(raw: Optional[str]) -> Optional[date]:
    """
    Deterministically parses multi-format date strings into a Python date.
    Returns None if date cannot be resolved with high confidence.
    """
    if not raw or not isinstance(raw, str):
        return None

    cleaned = raw.strip().replace(",", " ").replace(".", "/")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Format 1: ISO YYYY-MM-DD or YYYY/MM/DD
    m1 = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", cleaned)
    if m1:
        y, m, d = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
        try:
            return date(y, m, d)
        except ValueError:
            return None

    # Format 2: DD-Mon-YYYY or DD Mon YYYY (e.g. 15 Jan 2028 or 15-JAN-2028)
    m2 = re.match(r"^(\d{1,2})[-/ ]([A-Za-z]{3,9})[-/ ](\d{4})$", cleaned)
    if m2:
        d = int(m2.group(1))
        mon_str = m2.group(2).lower()
        y = int(m2.group(3))
        if mon_str in MONTH_MAP:
            try:
                return date(y, MONTH_MAP[mon_str], d)
            except ValueError:
                return None

    # Format 3: Mon DD YYYY (e.g. Oct 25 2027)
    m3 = re.match(r"^([A-Za-z]{3,9})[-/ ](\d{1,2})[-/ ](\d{4})$", cleaned)
    if m3:
        mon_str = m3.group(1).lower()
        d = int(m3.group(2))
        y = int(m3.group(3))
        if mon_str in MONTH_MAP:
            try:
                return date(y, MONTH_MAP[mon_str], d)
            except ValueError:
                return None

    # Format 4: DD/MM/YYYY
    m4 = re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", cleaned)
    if m4:
        p1, p2, y = int(m4.group(1)), int(m4.group(2)), int(m4.group(3))
        # If first part > 12, it must be DD/MM/YYYY
        if p1 > 12 and p2 <= 12:
            try:
                return date(y, p2, p1)
            except ValueError:
                return None
        # Standard international default: DD/MM/YYYY
        try:
            return date(y, p2, p1)
        except ValueError:
            try:
                return date(y, p1, p2)
            except ValueError:
                return None

    return None

def evaluate_expiry_status(
    expiry_date: Optional[date],
    warning_days: int = 60,
    reference_date: Optional[date] = None
) -> Tuple[str, Optional[int], str]:
    """
    Evaluates expiry date against reference date (defaults to today).
    Returns (status: str, days_remaining: Optional[int], message: str).
    Status values:
      - VALID
      - EXPIRING_SOON
      - EXPIRED
      - EXPIRY_DATE_NOT_FOUND
      - MANUAL_VERIFICATION_REQUIRED
    """
    if expiry_date is None:
        return (
            "EXPIRY_DATE_NOT_FOUND",
            None,
            "No discernible expiry date detected in document"
        )

    ref = reference_date or date.today()
    delta_days = (expiry_date - ref).days

    if delta_days < 0:
        return (
            "EXPIRED",
            delta_days,
            f"Document expired {abs(delta_days)} days ago (on {expiry_date.isoformat()})"
        )
    elif delta_days <= warning_days:
        return (
            "EXPIRING_SOON",
            delta_days,
            f"Document expires soon in {delta_days} days (on {expiry_date.isoformat()})"
        )
    else:
        return (
            "VALID",
            delta_days,
            f"Document is valid for {delta_days} more days (expires {expiry_date.isoformat()})"
        )
