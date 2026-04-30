import folium
from folium.plugins import AntPath


PROFILE_COLORS = {
    "Peak Chaser":    "#5B8DB8",
    "Coast Cruiser":  "#48A999",
    "Forest Wanderer":"#4CAF7D",
    "Desert Drifter": "#E8A838",
    "Thrill Seeker":  "#E85454",
}

ECO_GRADE_COLORS = {
    "A+": "#2ECC71", "A": "#27AE60",
    "B":  "#F1C40F", "C": "#E67E22",
    "D":  "#E74C3C", "F": "#922B21",
}


def build_map(
    stops: list[str],
    coords: list[list[float]],   # [[lon, lat], ...]  (GeoJSON order)
    order: list[int],
    legs: list[dict],
    profile_name: str,
    eco_grade: str,
    road_geometry: list[list[float]] | None = None,  # [[lat, lon], ...] for Folium
) -> folium.Map:
    """
    Builds and returns a Folium map with the optimized route.

    coords: [[lon, lat], ...] — GeoJSON order from geocode_city.
    road_geometry: [[lat, lon], ...] — already flipped, from get_route_geometry().
                   If None, falls back to straight lines between stops.
    """
    ordered_stops = [stops[i] for i in order]
    ordered_coords_lonlat = [coords[i] for i in order]

    # Folium needs [lat, lon] — flip from [lon, lat]
    folium_markers = [[c[1], c[0]] for c in ordered_coords_lonlat]

    center = [
        sum(c[1] for c in coords) / len(coords),
        sum(c[0] for c in coords) / len(coords),
    ]

    m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")

    route_color = PROFILE_COLORS.get(profile_name, "#3498DB")
    eco_color = ECO_GRADE_COLORS.get(eco_grade, "#3498DB")

    # Road geometry (real roads) or fallback straight lines
    polyline_points = road_geometry if road_geometry else folium_markers

    AntPath(
        locations=polyline_points,
        color=route_color,
        weight=4,
        opacity=0.85,
        delay=800,
    ).add_to(m)

    # Stop markers
    for i, (coord, name) in enumerate(zip(folium_markers, ordered_stops)):
        is_start = i == 0
        is_end = i == len(folium_markers) - 1

        if is_start:
            icon = folium.Icon(color="green", icon="play", prefix="fa")
            label = f"🟢 START: {name}"
        elif is_end:
            icon = folium.Icon(color="red", icon="flag", prefix="fa")
            label = f"🏁 END: {name}"
        else:
            leg = legs[i - 1] if i - 1 < len(legs) else {}
            icon = folium.Icon(color="blue", icon="circle", prefix="fa")
            label = (
                f"Stop {i}: {name}<br>"
                f"From previous: {leg.get('distance_miles', '?')} mi | "
                f"{leg.get('drive_hours', '?')} hrs"
            )

        folium.Marker(location=coord, popup=folium.Popup(label, max_width=250), icon=icon).add_to(m)

    # Eco grade legend
    legend_html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
         background:white; padding:12px 16px; border-radius:8px;
         box-shadow:0 2px 8px rgba(0,0,0,0.15); font-family:sans-serif; font-size:13px;">
        <b style="font-size:14px;">🌿 EcoVenture</b><br>
        Profile: {profile_name}<br>
        Eco Grade: <span style="color:{eco_color}; font-weight:bold; font-size:16px;">{eco_grade}</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def save_map(m: folium.Map, path: str = "outputs/route_map.html"):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    m.save(path)
    print(f"✅ Map saved to {path}")