import re
regex = r"(B0[A-Z0-9]{8})"
def zon(text: str) -> str:
    re_match = re.search(regex, text)
    if re_match:
        result = f"https://www.amazon.com/dp/{re_match.group(1)}"
    else:
        result = "hyperlink not found"
    return result
