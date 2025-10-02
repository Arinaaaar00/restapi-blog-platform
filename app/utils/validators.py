def validate_email(email: str) -> bool:
    """Validate email format"""
    return '@' in email and '.' in email.split('@')[-1]

def validate_password_strength(password: str) -> bool:
    """Validate password strength"""
    return len(password) >= 6

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    return text.strip()