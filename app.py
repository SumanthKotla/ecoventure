import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

from src.data_collection import (
    geocode_city, get_distance_matrix, get_route_geometry,
    get_weather, get_gas_prices, get_hotel_cost,
)
from src.profiler import classify_user, score_stop_for_profile
from src.eco_scorer import calculate_eco_score, eco_tip, CAR_TYPES
from src.route_optimizer import optimize_route, greedy_route, build_leg_summary
from src.cost_calculator import calculate_total_cost
from src.visualizer import build_map, save_map

st.set_page_config(
    page_title="EcoVenture",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; }
    .metric-card {
        background: #f8fffe; border: 1px solid #d4edda;
        border-radius: 12px; padding: 16px; text-align: center;
    }
    .eco-grade { font-size: 2.5rem; font-weight: 700; }
    .section-header { color: #2c7a4b; font-weight: 700; margin-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌿 EcoVenture")
    st.caption("Road trips optimized for adventure & the planet.")
    st.divider()

    st.markdown("### 🧠 Adventure Profile")
    hiking  = st.slider("🏔️ Hiking & Mountains", 1, 10, 7)
    water   = st.slider("🌊 Water & Coast",        1, 10, 4)
    camping = st.slider("⛺ Camping & Nature",      1, 10, 8)
    wildlife= st.slider("🦌 Wildlife Spotting",     1, 10, 6)
    extreme = st.slider("⚡ Extreme Sports",         1, 10, 3)

    profile = classify_user(hiking, water, camping, wildlife, extreme)
    st.success(f"{profile.emoji} **{profile.name}**\n\n{profile.description}")

    st.divider()
    st.markdown("### 🚗 Vehicle")
    car_type   = st.selectbox("Car Type", list(CAR_TYPES.keys()))
    custom_mpg = st.number_input("Custom MPG (0 = use default)", min_value=0, max_value=150, value=0)
    mpg = custom_mpg if custom_mpg > 0 else CAR_TYPES[car_type]["mpg"]

    st.divider()
    st.markdown("### 🗺️ Route Options")
    avoid_feature = st.selectbox(
        "Avoid",
        ["(nothing)", "tollways", "ferries", "highways"],
        help="Passed to ORS Directions for real road routing",
    )
    avoid_arg = None if avoid_feature == "(nothing)" else avoid_feature

    st.divider()
    st.markdown("### 💰 Budget")
    num_people   = st.number_input("# Travelers",             1, 10,  1)
    food_per_day = st.number_input("Food budget/person/day ($)", 20, 300, 50)
    nights       = st.number_input("Nights on the road",      1, 30,  3)

# ── Main ─────────────────────────────────────────────────────────────────────
st.title("🗺️ Plan Your EcoVenture")

col1, col2 = st.columns([2, 1])
with col1:
    raw_stops = st.text_area(
        "Enter your stops (one city per line)",
        placeholder="San Francisco, CA\nYosemite National Park, CA\nLake Tahoe, CA\nReno, NV",
        height=150,
    )
with col2:
    st.markdown("**Tips**")
    st.info("Add 2–10 stops. The optimizer finds the best order automatically.")

optimize_btn = st.button("🌿 Optimize My EcoVenture", type="primary", use_container_width=True)

# ── Execution ─────────────────────────────────────────────────────────────────
if optimize_btn and raw_stops.strip():
    stops = [s.strip() for s in raw_stops.strip().splitlines() if s.strip()]

    if len(stops) < 2:
        st.error("Please enter at least 2 stops.")
        st.stop()

    # 1. Geocode → [[lon, lat], ...]
    with st.spinner("🗺️ Geocoding stops..."):
        try:
            coords = [geocode_city(s) for s in stops]
        except Exception as e:
            st.error("Geocoding failed. Check your ORS_API_KEY in .env")
            st.exception(e)
            st.stop()

   # 2. Distance matrix
    import math

    def _haversine(a, b):
        R = 6_371_000
        lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
        dlat = lat2 - lat1; dlon = lon2 - lon1
        h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(h))

    def _fill_nulls(matrix, coords, is_duration=False):
        n = len(matrix)
        for i in range(n):
            for j in range(n):
                if matrix[i][j] is None:
                    d = _haversine(coords[i], coords[j])
                    matrix[i][j] = d / 25 if is_duration else d
        return matrix

    with st.spinner("📐 Building distance matrix..."):
        try:
            dist_matrix, dur_matrix = get_distance_matrix(coords)
            null_count = sum(
                1 for i in range(len(stops)) for j in range(len(stops))
                if i != j and (dist_matrix[i][j] is None or dur_matrix[i][j] is None)
            )
            if null_count:
                st.warning(
                    f"⚠️ ORS couldn't route {null_count} pair(s) — "
                    "filling gaps with straight-line estimates."
                )
            dist_matrix = _fill_nulls(dist_matrix, coords, is_duration=False)
            dur_matrix  = _fill_nulls(dur_matrix,  coords, is_duration=True)
        except Exception as e:
            st.error(f"EXCEPTION: {type(e).__name__}: {e}")
            st.warning(f"Distance matrix API failed ({e}). Using Haversine fallback.")
            n = len(stops)
            dist_matrix = [[_haversine(coords[i], coords[j]) for j in range(n)] for i in range(n)]
            dur_matrix  = [[d / 25 for d in row] for row in dist_matrix]

    # 3. Optimize order
    with st.spinner("🧠 Optimizing route..."):
        try:
            order, total_dist_m = optimize_route(dist_matrix)
        except Exception:
            order, total_dist_m = greedy_route(dist_matrix)

    legs = build_leg_summary(stops, order, dist_matrix, dur_matrix)
    total_miles = sum(leg["distance_miles"] for leg in legs)
    total_hours = sum(leg["drive_hours"] for leg in legs)

    # 4. Fetch real road geometry for map ✅ new
    road_geometry = None
    with st.spinner("🛣️ Fetching road geometry..."):
        try:
            ordered_lonlat = [coords[i] for i in order]
            road_geometry = get_route_geometry(ordered_lonlat, avoid=avoid_arg)
        except Exception as e:
            st.warning(f"Road geometry unavailable ({e}). Map will show straight lines.")

    # 5. Supporting data
    gas_price = get_gas_prices()
    eco       = calculate_eco_score(total_miles, car_type, custom_mpg if custom_mpg > 0 else None)
    avg_hotel = sum(get_hotel_cost(stops[i]) for i in order) / len(order)
    cost      = calculate_total_cost(
        total_miles, mpg, gas_price, nights, avg_hotel,
        nights + 1, stops, eco.offset_cost_usd, food_per_day, num_people,
    )

    # ── Results ───────────────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"## {profile.emoji} Your Optimized Route — *{profile.name}* Edition")

    metrics = st.columns(5)
    metrics[0].metric("🛣️ Distance",   f"{total_miles:.0f} mi")
    metrics[1].metric("⏱️ Drive Time", f"{total_hours:.1f} hrs")
    metrics[2].metric("💰 Total Cost", f"${cost.total_usd:,.0f}")
    metrics[3].metric("🌿 CO₂",        f"{eco.co2_kg} kg")
    metrics[4].metric("Grade",          f"{eco.grade_emoji} {eco.grade}")

    st.info(eco_tip(eco.grade))

    st.markdown("### 📍 Optimized Stop Order")
    for i, leg in enumerate(legs):
        match_score = score_stop_for_profile(leg["to"], profile)
        bar = "█" * (match_score // 10) + "░" * (10 - match_score // 10)
        st.markdown(
            f"**{i+1}. {leg['from']} → {leg['to']}** | "
            f"`{leg['distance_miles']} mi` | `{leg['drive_hours']} hrs` | "
            f"Match: `{bar}` {match_score}%"
        )

    st.markdown("### 🗺️ Interactive Route Map")
    try:
        m = build_map(stops, coords, order, legs, profile.name, eco.grade, road_geometry)
        components.html(m._repr_html_(), height=520)
    except Exception as e:
        st.warning(f"Map could not be rendered: {e}")

    st.markdown("### 🌱 Eco Impact Summary")
    ec = st.columns(4)
    ec[0].metric("🌳 Offset Need",  f"{eco.equivalent_trees} trees/yr")
    ec[1].metric("⛽ Fuel",          f"{eco.fuel_gallons} gal")
    ec[2].metric("💵 Offset Cost",  f"${eco.offset_cost_usd}")
    ec[3].metric("⛽ Gas Price",     f"${gas_price:.2f}/gal")

    st.markdown("### 💰 Cost Breakdown")
    breakdown = cost.breakdown()
    bcols = st.columns(len(breakdown))
    for col, (label, val) in zip(bcols, breakdown.items()):
        col.metric(label, f"${val:,.0f}")

elif optimize_btn:
    st.warning("Please enter your stops first.")