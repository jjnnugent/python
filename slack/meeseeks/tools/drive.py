#travelmode = driving | bicycle | walking | transit
# https://www.google.com/maps/dir/?api=1&origin=Paris%2CFrance&destination=Cherbourg%2CFrance&travelmode=driving&waypoints=Palace+of+Versailles%7CChartres+Cathedral%7CCathedral+of+Saint+Julian+of+Le+Mans%7CCaen+Castle
# pre + origin + destination + travelmode + waypoints = x | y | z
import re
def drive(text: str) -> str:
    prefix = "https://www.google.com/maps/dir/?api=1"
    destination = "&destination="
    #!"\#\$%\&'\(\)\*\+,\-\./:;<=>\?@\[\\\]\^_`\{\|\}\~
    invalid_symbols = r"\"\$%\(\)\*\+/:<=>\?@\[\\\]\^_`\{\|\}\~"
    text = re.sub(r"[" + invalid_symbols  + r"]", "", text)
    waypoints = text.split(";")
    waypoints = [place.strip() for place in waypoints if place.strip()]
    print(waypoints)
    for i in range(len(waypoints)):
        waypoints[i] = re.sub(r"\s+", "%20", waypoints[i])
        waypoints[i] = re.sub(r"!", "%21", waypoints[i])
        waypoints[i] = re.sub(r"#+", "%23", waypoints[i])
        waypoints[i] = re.sub(r"\&+", "%26", waypoints[i])
        waypoints[i] = re.sub(r"'+", "%27", waypoints[i])
        waypoints[i] = re.sub(r",+", "%2C", waypoints[i])
        waypoints[i] = re.sub(r"\-", "%2D", waypoints[i])
        waypoints[i] = re.sub(r"\.", "%2E", waypoints[i])
    destination += waypoints.pop() if waypoints else "bumfuck+nowhere"
    waypoints = f"&waypoints={'%7C'.join(waypoints)}" if waypoints else ""
    return f"{prefix}{destination}{waypoints}"
