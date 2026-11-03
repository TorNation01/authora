"""One password policy, applied everywhere a password is set.

Length alone is not enough (``passwordpassword`` is 16 characters and worthless),
and complexity rules alone are not enough (``P@ss1`` passes most checkers). The
policy here is deliberately boring and predictable for the user:

  * at least 12 characters
  * not one of the passwords that shows up in every credential dump
  * not built out of the account's own email address
  * not a single character repeated

It is used by registration, password change and password reset through the same
function, so the three can never drift apart.
"""

from __future__ import annotations

MIN_LENGTH = 12
MAX_LENGTH = 128

# A short, high-signal list: the passwords that account for a large share of
# credential-stuffing wins. Kept small on purpose — a long list belongs in a
# breach-corpus check, not in a source file.
COMMON_PASSWORDS = {
    "123456789012",
    "1234567890123",
    "12345678901234",
    "password1234",
    "password12345",
    "passwordpassword",
    "qwertyuiop123",
    "qwertyuiopasd",
    "iloveyou1234",
    "welcome12345",
    "administrator",
    "letmein12345",
    "abc123456789",
    "monkey123456",
    "dragon123456",
    "football1234",
    "baseball1234",
    "sunshine1234",
    "princess1234",
    "superman1234",
    "trustno1trustno1",
    "changeme1234",
    "authora12345",
    "authora123456",
    "correcthorsebatterystaple",
}


def password_problem(password: str, email: str | None = None) -> str | None:
    """Return a human-readable reason the password is unacceptable, or None."""
    pw = password or ""

    if len(pw) < MIN_LENGTH:
        return f"Choose a password of at least {MIN_LENGTH} characters."
    if len(pw) > MAX_LENGTH:
        return f"Passwords cannot be longer than {MAX_LENGTH} characters."

    lowered = pw.lower()
    if lowered in COMMON_PASSWORDS:
        return "That password appears in public breach lists. Choose something else."
    if len(set(pw)) == 1:
        return "That password is a single repeated character. Choose something else."

    if email:
        local = email.split("@", 1)[0].strip().lower()
        # Only a meaningful local part can make a password guessable from the
        # address; "a@b.com" would match almost anything.
        if len(local) >= 3 and local in lowered:
            return "Your password cannot contain your email address."

    return None


def validate_password(password: str, email: str | None = None) -> None:
    """Raise ValueError with the user-facing reason when the password is weak."""
    problem = password_problem(password, email)
    if problem:
        raise ValueError(problem)
