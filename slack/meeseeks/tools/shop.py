import re

SITES = (
    'https://www.amazon.com/s?k=',
    'https://www.ebay.com/sch/i.html?_nkw=',
    'https://www.newegg.com/p/pl?d=',
    'https://www.bestbuy.com/site/searchpage.jsp?st=',
    'https://www.walmart.com/search?q=',
    'https://www.target.com/s?searchTerm=',
    'https://www.bhphotovideo.com/c/search?q=',
    'https://www.bing.com/shop?q=',
    'https://www.google.com/search?udm=28&q='
)

def shop(text: str) -> str:
    result = []
    query = re.sub(r"\s+", "%20", text)
    for site in SITES:
        result.append(f"{site}{query}")
    return "\n".join(result)
