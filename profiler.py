import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
 
PROFILES = {
    0: {
        "name": "Peak Chaser",
        "emoji": "🏔️",
        "description": "You live for elevation. Mountains, ridgelines, and summit views are your fuel.",
        "stop_tags": ["mountain", "hiking", "summit", "alpine", "glacier"],
        "avoid_tags": ["beach", "resort", "casino"],
    },
    1: {
        "name": "Coast Cruiser",
        "emoji": "🌊",
        "description": "The ocean calls. You plan routes along coastlines and hunt hidden beaches.",
        "stop_tags": ["beach", "coast", "ocean", "surf", "bay"],
        "avoid_tags": ["desert", "landlocked"],
    },
    2: {
        "name": "Forest Wanderer",
        "emoji": "🌲",
        "description": "Dense canopy, birdsong, and starlit campsites. You go where the trees go.",
        "stop_tags": ["forest", "national park", "camping", "wildlife", "waterfall"],
        "avoid_tags": ["urban", "resort"],
    },
    3: {
        "name": "Desert Drifter",
        "emoji": "🏜️",
        "description": "Vast silence and ancient rock. Canyons, mesas, and Milky Way skies await.",
        "stop_tags": ["canyon", "desert", "rock formation", "stargazing", "arches"],
        "avoid_tags": ["beach", "rainforest"],
    },
    4: {
        "name": "Thrill Seeker",
        "emoji": "⚡",
        "description": "Adrenaline is the itinerary. Anything extreme, vertical, or fast.",
        "stop_tags": ["extreme sports", "cliff", "whitewater", "zip line", "bungee"],
        "avoid_tags": ["museum", "relaxation"],
    },
}
 
# Prototype preference vectors [hiking, water, camping, wildlife, extreme]
_PROTOTYPES = np.array([
    [9, 3, 6, 5, 4],   # Peak Chaser
    [4, 9, 4, 5, 5],   # Coast Cruiser
    [6, 5, 9, 8, 2],   # Forest Wanderer
    [5, 2, 7, 4, 3],   # Desert Drifter
    [6, 5, 4, 3, 10],  # Thrill Seeker
])
 
 
@dataclass
class AdventureProfile:
    profile_id: int
    name: str
    emoji: str
    description: str
    stop_tags: list[str]
    avoid_tags: list[str]   # BUG FIX: was missing — used by score_stop_for_profile
    confidence: float       # 0–1
 
 
def build_profiler():
    scaler = StandardScaler()
    X = scaler.fit_transform(_PROTOTYPES)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(X)
    return kmeans, scaler
 
 
_KMEANS, _SCALER = build_profiler()
 
 
def classify_user(
    hiking: int,
    water: int,
    camping: int,
    wildlife: int,
    extreme: int,
) -> AdventureProfile:
    """
    All inputs are 1–10 preference scores.
    Returns the closest adventure profile.
    """
    user_vec = np.array([[hiking, water, camping, wildlife, extreme]])
    scaled = _SCALER.transform(user_vec)
    cluster_id = int(_KMEANS.predict(scaled)[0])
 
    distances = np.linalg.norm(_SCALER.transform(_PROTOTYPES) - scaled, axis=1)
    min_dist = distances[cluster_id]
    confidence = round(1 - (min_dist / (min_dist + distances.mean() + 1e-9)), 2)
 
    p = PROFILES[cluster_id]
    return AdventureProfile(
        profile_id=cluster_id,
        name=p["name"],
        emoji=p["emoji"],
        description=p["description"],
        stop_tags=p["stop_tags"],
        avoid_tags=p["avoid_tags"],   # BUG FIX: now included
        confidence=min(confidence, 0.99),
    )
 
 
def score_stop_for_profile(stop_name: str, profile: AdventureProfile) -> int:
    """Returns 0–100 match score for a stop given a user profile."""
    name_lower = stop_name.lower()
    matches = sum(tag in name_lower for tag in profile.stop_tags)
    penalties = sum(tag in name_lower for tag in profile.avoid_tags)
    return min(100, max(0, (matches * 25) - (penalties * 15) + 50))
 