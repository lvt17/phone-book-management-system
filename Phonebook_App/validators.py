import re


def validate_phone(phone: str) -> bool:
    """
    Validate phone number.
    Must belong to Vietnam (+84 or 0 prefix) and have exactly 10 digits for local (e.g. 09...) or 11/12 digits for +84 (e.g. +849...).
    Allowed formats: 0[3|5|7|8|9]XXXXXXXX or +84[3|5|7|8|9]XXXXXXXX
    """
    pattern = r'^(0|\+84)(3|5|7|8|9)[0-9]{8}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return True  # Optional field
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Username must be at least 3 characters, alphanumeric and underscores only."""
    if not username or len(username) < 3:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))


def validate_password(password: str) -> bool:
    """Password must be at least 6 characters."""
    return bool(password and len(password) >= 6)
