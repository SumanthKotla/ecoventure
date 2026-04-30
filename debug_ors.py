import os, math, requests
from dotenv import load_dotenv

load_dotenv("/Users/sumanthvasudev/Desktop/ecoventure/.env")
key = os.getenv("ORS_API_KEY")
print(f"Key: {key[:8]}...")

def geocode(city):
    url = "https://api.heigit.org/pelias/v1/search"
    r = requests.get(url, params={"api_key": key, "text": city, "size": 1}, timeout=10)
    coords = r.json()["features"][0]["geometry"]["coordinates"]
    print(f"  {city}: {coords}")
    return coords

def haversine(a, b):
    R = 6371000
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(h))

print("\nGeocoding...")
sf = geocode("San Francisco, CA")
sj = geocode("San Jose, CA")
la = geocode("Los Angeles, CA")
locations = [sf, sj, la]
cities = ["SF", "SJ", "LA"]

print("\nCalling ORS matrix...")
url = "https://api.openrouteservice.org/v2/matrix/driving-car"
headers = {"Authorization": key, "Content-Type": "application/json"}
body = {"locations": locations, "metrics": ["distance", "duration"]}
r = requests.post(url, json=body, headers=headers, timeout=20)
print(f"Status: {r.status_code}")
dist = r.json()["distances"]

print("\nResults:")
for i in range(3):
    for j in range(3):
        if i != j:
            d = dist[i][j]
            straight = haversine(locations[i], locations[j])
            if d is None:
                print(f"  {cities[i]}->{cities[j]}: None")
            else:
                ratio = d / straight
                flag = "CAUGHT" if ratio > 4 else "ok"
                print(f"  {cities[i]}->{cities[j]}: {d/1609.34:.1f}mi ratio={ratio:.2f}x {flag}")