import requests
import os

# All internal coordinates are [lon, lat] (GeoJSON standard).
# geocode_city returns [lon, lat].
# get_distance_matrix expects [[lon, lat], ...].
# visualizer expects [[lon, lat], ...] and flips to [lat, lon] for Folium.

def _ors_key() -> str:
    key = os.getenv("ORS_API_KEY", "")
    if not key:
        raise ValueError("ORS_API_KEY missing from .env")
    return key


def geocode_city(city_name: str) -> list[float]:
    """Returns [lon, lat] for a city name using the HeiGIT/Pelias API."""
    url = "https://api.heigit.org/pelias/v1/search"
    params = {"api_key": _ors_key(), "text": city_name, "size": 1}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    features = data.get("features", [])
    if not features:
        raise ValueError(f"Could not geocode: {city_name}")
    # Pelias returns [lon, lat] — return as-is (GeoJSON standard)
    lon, lat = features[0]["geometry"]["coordinates"]
    return [lon, lat]


def _haversine_m(a: list[float], b: list[float]) -> float:
    """Straight-line distance in meters between two [lon, lat] points."""
    import math
    R = 6_371_000
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat = lat2 - lat1; dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(h))


def get_distance_matrix(locations: list[list[float]]) -> tuple[list, list]:
    """
    locations: [[lon, lat], ...]  (GeoJSON order)
    Returns (distances_meters, durations_seconds) as 2D matrices.
    Any None values or implausible distances (>4x straight-line) are set to None
    so the caller's fill_nulls replaces them with Haversine estimates.
    """
    url = "https://api.openrouteservice.org/v2/matrix/driving-car"
    headers = {"Authorization": _ors_key(), "Content-Type": "application/json"}
    body = {
        "locations": locations,
        "metrics": ["distance", "duration"],
    }
    r = requests.post(url, json=body, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    dist = data["distances"]
    dur  = data["durations"]

    n = len(locations)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if dist[i][j] is None:
                continue
            straight = _haversine_m(locations[i], locations[j])
            if dist[i][j] > straight * 4:
                dist[i][j] = None
                dur[i][j]  = None

    for i, row in enumerate(dist):
        for j, d in enumerate(row):
            if i != j:
                print(f"DEBUG dist[{i}][{j}] = {d}")
    return dist, dur

def get_route_geometry(
    locations: list[list[float]],
    profile: str = "driving-car",
    avoid: str | None = None,
) -> list[list[float]]:
    """
    Fetches the actual road polyline from ORS Directions API.
    locations: [[lon, lat], ...] in visit order.
    Returns list of [lat, lon] points ready for Folium.

    Strategy: try the full multi-stop route first. If ORS rejects it (e.g.
    because one pair is unroutable), fall back to fetching each leg individually
    and concatenating the geometry.
    """
    url = f"https://api.openrouteservice.org/v2/directions/{profile}/geojson"
    headers = {"Authorization": _ors_key(), "Content-Type": "application/json"}

    def _fetch(coords_subset):
        body: dict = {"coordinates": coords_subset}
        if avoid:
            body["options"] = {"avoid_features": [avoid]}
        r = requests.post(url, json=body, headers=headers, timeout=20)
        r.raise_for_status()
        raw = r.json()["features"][0]["geometry"]["coordinates"]
        return [[c[1], c[0]] for c in raw]  # flip to [lat, lon] for Folium

    # Try full route
    try:
        return _fetch(locations)
    except Exception:
        pass

    # Leg-by-leg fallback
    geometry = []
    for i in range(len(locations) - 1):
        try:
            leg_pts = _fetch([locations[i], locations[i + 1]])
            geometry.extend(leg_pts)
        except Exception:
            # If even a single leg fails, just add straight line between the two points
            a, b = locations[i], locations[i + 1]
            geometry.append([a[1], a[0]])
            geometry.append([b[1], b[0]])
    return geometry


def get_weather(lat: float, lon: float) -> dict:
    """Returns weather dict for a coordinate."""
    owm_key = os.getenv("OWM_API_KEY", "")
    if not owm_key:
        return {}
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": owm_key, "units": "imperial"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()
        return {
            "city": d["name"],
            "temp_f": d["main"]["temp"],
            "description": d["weather"][0]["description"],
            "humidity": d["main"]["humidity"],
        }
    except Exception:
        return {}


def get_gas_prices() -> float:
    """Fetch weekly US avg gas price from EIA. Falls back to static average."""
    eia_key = os.getenv("EIA_API_KEY", "")
    if not eia_key:
        return 3.85
    try:
        url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
        params = {
            "api_key": eia_key,
            "frequency": "weekly",
            "data[0]": "value",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 1,
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return float(r.json()["response"]["data"][0]["value"])
    except Exception:
        return 3.85


HOTEL_COSTS = {
    "San Francisco": 180, "Los Angeles": 140, "Las Vegas": 90,
    "Seattle": 150, "Portland": 110, "Denver": 125, "Phoenix": 100,
    "San Diego": 145, "Salt Lake City": 105, "Boise": 95,
    "Grand Canyon": 120, "Yosemite": 130, "Zion": 115,
}


def get_hotel_cost(city: str) -> float:
    for key in HOTEL_COSTS:
        if key.lower() in city.lower():
            return HOTEL_COSTS[key]
    return 115


def get_trail_data(lat: float, lon: float, radius_km: int = 30) -> list[dict]:
    """Fetch nearby parks from NPS API."""
    url = "https://developer.nps.gov/api/v1/parks"
    params = {
        "api_key": os.getenv("NPS_API_KEY", "DEMO_KEY"),
        "limit": 5,
        "q": f"{lat},{lon}",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        parks = r.json().get("data", [])
        return [{"name": p["fullName"], "description": p["description"][:100]} for p in parks]
    except Exception:
        return []