def help(slash: str) -> str:
    tip = str()
    match slash:
        case "/altcaps":
            tip = "To alternate capital letters: `/altcaps hello world`\n```output:\nhELlo WORld```"
        case "/drive":
            tip = "To create multi-destination nav link: `/drive carl's jr on red cliffs dr; walmart supercenter; home`\n```output:\nhttps://www.google.com/maps/dir/?api=1&destination=home&travelmode=driving&waypoints=carl%27s+jr+on+red+cliffs+dr%7Cwalmart+supercenter```"
        case "/gld":
            tip = "To display current deals (price and regex pattern optional): `/gld 420.69 13900$|4080 laptop`\n```output:\n   cost         brand    screen      ram   ssd     cpu  gpu  multi  score   cpps   gpps   tpps  \n 849.99 Lenovo LOQ 15  1080 144       16   1TB  8845HS 4060  28708  17609 0.0296 0.0483 0.0184  ```"
        case "/pm":
            tip = "To load CPU/GPU benchmark scores: `/pm 13900hx`\n```output:\n                 name  multi single    socket\nIntel Core i9-13900HX  43940   4122 FCBGA1964```"
        case "/shop":
            tip = "To preload ecommerce links with search query: `/shop hello world`\n```output:\namazon.com/s?k=hello%20world```"
        case "/zon":
            tip = "To remove tracking: `/zon this is optional text [product page URL]`\n```output:\nhttps://www.amazon.com/This-Is-Optional-Text/dp/B0XXXXXXXX```"

    return tip
