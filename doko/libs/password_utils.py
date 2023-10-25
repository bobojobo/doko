import re

import bcrypt


# todo:
#   rename file into authentication utils
#   add session token generator.
#   (Add Username validator regex)


# Some pepper stored in code. Yes, I am aware that is open source and visible.
# No I don't care, 't is just for the funs and the learnings anyway.
pepper = "dfc202e7#zc*4;1b81fzabbf5J2fÖ8b7"
hashing_rounds = 11

# pepper is 32 chars long, bcrypt has maximum lenght of 72, afterwards it cuts it off anyways.
# todo: rename to password valdation regex
password_regex = r"[A-Za-z0-9@#$%^&+=]{8,39}"

password_regex_description = """
    - Minimum 8 characters
    - Maximum 39 characters
    - uppercase letters
    - lowercase letters
    - digits
    - '@', '#', '$', '%', '^', '&', '+'
"""


def is_valid_password(password: str) -> bool:
    # todo: make nicer typwise. Probably "return re.fullmatch() is None" or "is not None"
    if re.fullmatch(password_regex, password):
        return True
    return False


def pepper_password(password: str) -> bytes:
    return f"{pepper}{password}".encode("utf-8")


def hash_password(password: str) -> bytes:
    """Salted and peppered one way hash with 11 iterations"""
    return bcrypt.hashpw(
        password=pepper_password(password),
        salt=bcrypt.gensalt(rounds=hashing_rounds),
    )


def password_matches(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(
        password=pepper_password(password),
        hashed_password=hashed,
    )


# todo: unused. Is this even nicer?
class password:
    pepper: str = "dfc202e7#zc*4;1b81fzabbf5J2fÖ8b7"
    hashing_rounds: int = 11
    password_regex = r"[A-Za-z0-9@#$%^&+=]{8,39}"
    password_regex_description = """
        - Minimum 8 characters
        - Maximum 39 characters
        - uppercase letters
        - lowercase letters
        - digits
        - '@', '#', '$', '%', '^', '&', '+'
    """

    def __init__(self, password: str) -> None:
        self.password = password

    @property
    def peppered_password(self) -> bytes:
        return f"{self.pepper}{self.password}".encode("utf-8")

    def matches(self, hashed: bytes) -> bool:
        return bcrypt.checkpw(
            password=pepper_password(self.password),
            hashed_password=hashed,
        )

    @property
    def hash(self) -> bytes:
        return bcrypt.hashpw(
            password=pepper_password(self.password),
            salt=bcrypt.gensalt(rounds=self.hashing_rounds),
        )

    @property
    def is_valid(self) -> bool:
        if re.fullmatch(self.password_regex, self.password):
            return True
        return False
