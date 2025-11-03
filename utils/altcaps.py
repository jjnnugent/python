from random import choice
def altcaps(text: str) -> str:
    return ''.join([choice([char.upper(), char.lower()]) for char in text]) if len(text) > 0 else "no text found"
