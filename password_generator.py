<<<<<<< HEAD
"""
password_generator.py
─────────────────────
Core engine for the Password Generator project.

Responsibilities
────────────────
• Generate cryptographically-secure passwords via Python's `secrets` module.
• Guarantee at least one character from every selected character-set category.
• Calculate Shannon password entropy (bits).
• Classify password strength: Weak / Medium / Strong / Very Strong.

Why `secrets` and not `random`?
────────────────────────────────
`random` uses a Mersenne-Twister PRNG whose state can be predicted if enough
output is obtained.  `secrets` wraps the OS CSPRNG (e.g., /dev/urandom on Linux,
BCryptGenRandom on Windows), making it suitable for security-sensitive work.

Entropy formula
───────────────
H = L × log₂(N)
  L = password length
  N = size of the alphabet used
A 128-bit entropy threshold is considered computationally infeasible to brute-force.
"""

import math
import secrets
import string
from dataclasses import dataclass, field
from typing import Optional


# ─── Character pools ────────────────────────────────────────────────────────

UPPERCASE: str = string.ascii_uppercase          # A-Z
LOWERCASE: str = string.ascii_lowercase          # a-z
DIGITS:    str = string.digits                   # 0-9
SYMBOLS:   str = string.punctuation              # !"#$%&' …


# ─── Data containers ────────────────────────────────────────────────────────

@dataclass
class PasswordOptions:
    """
    Encapsulates the user-chosen generation parameters.

    Attributes
    ----------
    length      : Desired password length (minimum 4 when multiple categories chosen).
    use_upper   : Include A-Z.
    use_lower   : Include a-z.
    use_digits  : Include 0-9.
    use_symbols : Include punctuation symbols.
    """
    length:      int  = 16
    use_upper:   bool = True
    use_lower:   bool = True
    use_digits:  bool = True
    use_symbols: bool = True


@dataclass
class PasswordResult:
    """
    Bundles everything the caller needs after generation.

    Attributes
    ----------
    password : The generated password string.
    entropy  : Shannon entropy in bits.
    strength : Human-readable strength label.
    score    : Numeric score 0-4 (used to drive the progress bar).
    """
    password: str
    entropy:  float
    strength: str
    score:    int


# ─── Strength constants ──────────────────────────────────────────────────────

# Thresholds in bits – industry standard guidance.
_ENTROPY_THRESHOLDS = [
    (28,  "Weak",        0),
    (60,  "Fair",        1),
    (80,  "Medium",      2),
    (100, "Strong",      3),
    (999, "Very Strong", 4),
]

# Additional heuristic penalties / bonuses
_MIN_STRONG_LENGTH = 12


# ─── Public API ─────────────────────────────────────────────────────────────

def generate_password(opts: PasswordOptions) -> PasswordResult:
    """
    Generate a cryptographically secure password according to *opts*.

    Algorithm
    ---------
    1. Build alphabet from all enabled categories.
    2. Draw one character from each enabled category to satisfy the
       "at-least-one" requirement.
    3. Fill the remainder of the length with random choices from the full alphabet.
    4. Shuffle the combined list with `secrets.SystemRandom` to avoid
       predictable prefix patterns.
    5. Compute entropy and classify strength.

    Parameters
    ----------
    opts : PasswordOptions
        The generation configuration chosen by the user.

    Returns
    -------
    PasswordResult
        The password, its entropy in bits, its strength label, and numeric score.

    Raises
    ------
    ValueError
        If no character category is enabled, or length is below 4 when
        multiple categories are selected.
    """
    alphabet, guaranteed = _build_alphabet_and_guarantee(opts)

    if not alphabet:
        raise ValueError("At least one character category must be selected.")

    required_min = max(len(guaranteed), 4 if len(guaranteed) > 1 else 1)
    if opts.length < required_min:
        raise ValueError(
            f"Password length must be at least {required_min} "
            f"when {len(guaranteed)} categories are selected."
        )

    # Fill the remaining slots from the full alphabet
    filler_count = opts.length - len(guaranteed)
    filler = [secrets.choice(alphabet) for _ in range(filler_count)]

    # Combine and shuffle securely
    combined = guaranteed + filler
    sysrand = secrets.SystemRandom()
    sysrand.shuffle(combined)

    password = "".join(combined)
    entropy  = _calculate_entropy(opts.length, len(alphabet))
    strength, score = _classify_strength(entropy, opts.length)

    return PasswordResult(
        password=password,
        entropy=round(entropy, 2),
        strength=strength,
        score=score,
    )


def check_strength(password: str) -> tuple[str, int, float]:
    """
    Evaluate a *pre-existing* password string (e.g., entered manually).

    Returns
    -------
    tuple[str, int, float]
        (strength_label, score_0_to_4, entropy_bits)
    """
    alphabet_size = _infer_alphabet_size(password)
    entropy = _calculate_entropy(len(password), alphabet_size) if alphabet_size else 0.0
    strength, score = _classify_strength(entropy, len(password))
    return strength, score, round(entropy, 2)


# ─── Internal helpers ────────────────────────────────────────────────────────

def _build_alphabet_and_guarantee(opts: PasswordOptions) -> tuple[str, list[str]]:
    """Construct the combined alphabet and the guaranteed-one list."""
    alphabet   = ""
    guaranteed = []

    if opts.use_upper:
        alphabet += UPPERCASE
        guaranteed.append(secrets.choice(UPPERCASE))

    if opts.use_lower:
        alphabet += LOWERCASE
        guaranteed.append(secrets.choice(LOWERCASE))

    if opts.use_digits:
        alphabet += DIGITS
        guaranteed.append(secrets.choice(DIGITS))

    if opts.use_symbols:
        alphabet += SYMBOLS
        guaranteed.append(secrets.choice(SYMBOLS))

    return alphabet, guaranteed


def _calculate_entropy(length: int, alphabet_size: int) -> float:
    """
    Shannon entropy: H = L × log₂(N).

    Parameters
    ----------
    length        : Number of characters.
    alphabet_size : Unique characters in the pool.

    Returns
    -------
    float : Entropy in bits.
    """
    if alphabet_size <= 1 or length == 0:
        return 0.0
    return length * math.log2(alphabet_size)


def _classify_strength(entropy: float, length: int) -> tuple[str, int]:
    """
    Map entropy bits (+ length heuristic) to a strength label and score.

    Parameters
    ----------
    entropy : Calculated entropy in bits.
    length  : Password length (used as a secondary heuristic).

    Returns
    -------
    tuple[str, int] : (label, score_0_to_4)
    """
    label, score = "Weak", 0
    for threshold, lbl, scr in _ENTROPY_THRESHOLDS:
        if entropy < threshold:
            label, score = lbl, scr
            break

    # Penalise very short passwords even if the alphabet is rich
    if length < _MIN_STRONG_LENGTH and score > 2:
        score  = 2
        label  = "Medium"

    return label, score


def _infer_alphabet_size(password: str) -> int:
    """Heuristically infer the alphabet pool used in *password*."""
    size = 0
    if any(c in UPPERCASE for c in password):
        size += len(UPPERCASE)
    if any(c in LOWERCASE for c in password):
        size += len(LOWERCASE)
    if any(c in DIGITS for c in password):
        size += len(DIGITS)
    if any(c in SYMBOLS for c in password):
        size += len(SYMBOLS)
    return size


# ─── Convenience demo ────────────────────────────────────────────────────────

if __name__ == "__main__":
    opts = PasswordOptions(length=20, use_upper=True, use_lower=True,
                           use_digits=True, use_symbols=True)
    result = generate_password(opts)
    print(f"Password : {result.password}")
    print(f"Entropy  : {result.entropy} bits")
    print(f"Strength : {result.strength} (score {result.score}/4)")
=======
"""
password_generator.py
─────────────────────
Core engine for the Password Generator project.

Responsibilities
────────────────
• Generate cryptographically-secure passwords via Python's `secrets` module.
• Guarantee at least one character from every selected character-set category.
• Calculate Shannon password entropy (bits).
• Classify password strength: Weak / Medium / Strong / Very Strong.

Why `secrets` and not `random`?
────────────────────────────────
`random` uses a Mersenne-Twister PRNG whose state can be predicted if enough
output is obtained.  `secrets` wraps the OS CSPRNG (e.g., /dev/urandom on Linux,
BCryptGenRandom on Windows), making it suitable for security-sensitive work.

Entropy formula
───────────────
H = L × log₂(N)
  L = password length
  N = size of the alphabet used
A 128-bit entropy threshold is considered computationally infeasible to brute-force.
"""

import math
import secrets
import string
from dataclasses import dataclass, field
from typing import Optional


# ─── Character pools ────────────────────────────────────────────────────────

UPPERCASE: str = string.ascii_uppercase          # A-Z
LOWERCASE: str = string.ascii_lowercase          # a-z
DIGITS:    str = string.digits                   # 0-9
SYMBOLS:   str = string.punctuation              # !"#$%&' …


# ─── Data containers ────────────────────────────────────────────────────────

@dataclass
class PasswordOptions:
    """
    Encapsulates the user-chosen generation parameters.

    Attributes
    ----------
    length      : Desired password length (minimum 4 when multiple categories chosen).
    use_upper   : Include A-Z.
    use_lower   : Include a-z.
    use_digits  : Include 0-9.
    use_symbols : Include punctuation symbols.
    """
    length:      int  = 16
    use_upper:   bool = True
    use_lower:   bool = True
    use_digits:  bool = True
    use_symbols: bool = True


@dataclass
class PasswordResult:
    """
    Bundles everything the caller needs after generation.

    Attributes
    ----------
    password : The generated password string.
    entropy  : Shannon entropy in bits.
    strength : Human-readable strength label.
    score    : Numeric score 0-4 (used to drive the progress bar).
    """
    password: str
    entropy:  float
    strength: str
    score:    int


# ─── Strength constants ──────────────────────────────────────────────────────

# Thresholds in bits – industry standard guidance.
_ENTROPY_THRESHOLDS = [
    (28,  "Weak",        0),
    (60,  "Fair",        1),
    (80,  "Medium",      2),
    (100, "Strong",      3),
    (999, "Very Strong", 4),
]

# Additional heuristic penalties / bonuses
_MIN_STRONG_LENGTH = 12


# ─── Public API ─────────────────────────────────────────────────────────────

def generate_password(opts: PasswordOptions) -> PasswordResult:
    """
    Generate a cryptographically secure password according to *opts*.

    Algorithm
    ---------
    1. Build alphabet from all enabled categories.
    2. Draw one character from each enabled category to satisfy the
       "at-least-one" requirement.
    3. Fill the remainder of the length with random choices from the full alphabet.
    4. Shuffle the combined list with `secrets.SystemRandom` to avoid
       predictable prefix patterns.
    5. Compute entropy and classify strength.

    Parameters
    ----------
    opts : PasswordOptions
        The generation configuration chosen by the user.

    Returns
    -------
    PasswordResult
        The password, its entropy in bits, its strength label, and numeric score.

    Raises
    ------
    ValueError
        If no character category is enabled, or length is below 4 when
        multiple categories are selected.
    """
    alphabet, guaranteed = _build_alphabet_and_guarantee(opts)

    if not alphabet:
        raise ValueError("At least one character category must be selected.")

    required_min = max(len(guaranteed), 4 if len(guaranteed) > 1 else 1)
    if opts.length < required_min:
        raise ValueError(
            f"Password length must be at least {required_min} "
            f"when {len(guaranteed)} categories are selected."
        )

    # Fill the remaining slots from the full alphabet
    filler_count = opts.length - len(guaranteed)
    filler = [secrets.choice(alphabet) for _ in range(filler_count)]

    # Combine and shuffle securely
    combined = guaranteed + filler
    sysrand = secrets.SystemRandom()
    sysrand.shuffle(combined)

    password = "".join(combined)
    entropy  = _calculate_entropy(opts.length, len(alphabet))
    strength, score = _classify_strength(entropy, opts.length)

    return PasswordResult(
        password=password,
        entropy=round(entropy, 2),
        strength=strength,
        score=score,
    )


def check_strength(password: str) -> tuple[str, int, float]:
    """
    Evaluate a *pre-existing* password string (e.g., entered manually).

    Returns
    -------
    tuple[str, int, float]
        (strength_label, score_0_to_4, entropy_bits)
    """
    alphabet_size = _infer_alphabet_size(password)
    entropy = _calculate_entropy(len(password), alphabet_size) if alphabet_size else 0.0
    strength, score = _classify_strength(entropy, len(password))
    return strength, score, round(entropy, 2)


# ─── Internal helpers ────────────────────────────────────────────────────────

def _build_alphabet_and_guarantee(opts: PasswordOptions) -> tuple[str, list[str]]:
    """Construct the combined alphabet and the guaranteed-one list."""
    alphabet   = ""
    guaranteed = []

    if opts.use_upper:
        alphabet += UPPERCASE
        guaranteed.append(secrets.choice(UPPERCASE))

    if opts.use_lower:
        alphabet += LOWERCASE
        guaranteed.append(secrets.choice(LOWERCASE))

    if opts.use_digits:
        alphabet += DIGITS
        guaranteed.append(secrets.choice(DIGITS))

    if opts.use_symbols:
        alphabet += SYMBOLS
        guaranteed.append(secrets.choice(SYMBOLS))

    return alphabet, guaranteed


def _calculate_entropy(length: int, alphabet_size: int) -> float:
    """
    Shannon entropy: H = L × log₂(N).

    Parameters
    ----------
    length        : Number of characters.
    alphabet_size : Unique characters in the pool.

    Returns
    -------
    float : Entropy in bits.
    """
    if alphabet_size <= 1 or length == 0:
        return 0.0
    return length * math.log2(alphabet_size)


def _classify_strength(entropy: float, length: int) -> tuple[str, int]:
    """
    Map entropy bits (+ length heuristic) to a strength label and score.

    Parameters
    ----------
    entropy : Calculated entropy in bits.
    length  : Password length (used as a secondary heuristic).

    Returns
    -------
    tuple[str, int] : (label, score_0_to_4)
    """
    label, score = "Weak", 0
    for threshold, lbl, scr in _ENTROPY_THRESHOLDS:
        if entropy < threshold:
            label, score = lbl, scr
            break

    # Penalise very short passwords even if the alphabet is rich
    if length < _MIN_STRONG_LENGTH and score > 2:
        score  = 2
        label  = "Medium"

    return label, score


def _infer_alphabet_size(password: str) -> int:
    """Heuristically infer the alphabet pool used in *password*."""
    size = 0
    if any(c in UPPERCASE for c in password):
        size += len(UPPERCASE)
    if any(c in LOWERCASE for c in password):
        size += len(LOWERCASE)
    if any(c in DIGITS for c in password):
        size += len(DIGITS)
    if any(c in SYMBOLS for c in password):
        size += len(SYMBOLS)
    return size


# ─── Convenience demo ────────────────────────────────────────────────────────

if __name__ == "__main__":
    opts = PasswordOptions(length=20, use_upper=True, use_lower=True,
                           use_digits=True, use_symbols=True)
    result = generate_password(opts)
    print(f"Password : {result.password}")
    print(f"Entropy  : {result.entropy} bits")
    print(f"Strength : {result.strength} (score {result.score}/4)")
>>>>>>> c83d8f2cbbc873c011c33a36c4fa1118bed09959
