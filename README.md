# 🌿 EcoVenture — AI-Powered Road Trip Optimizer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=folium&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**The first road trip planner built for adventure travelers that optimizes for experience AND environmental impact.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [API Keys](#-api-keys) • [Project Structure](#-project-structure) • [ML Models](#-ml-models)

</div>

---

## 🎯 What is EcoVenture?

EcoVenture is a full-stack Python application that combines **Machine Learning**, **route optimization**, and **real-time data APIs** to plan the perfect eco-conscious adventure road trip. Unlike existing apps (Roadtrippers, Wanderlog, Google Maps), EcoVenture uniquely merges:

- 🧠 **AI Adventure Personality Profiling** — K-Means clustering to match stops to your travel style
- 🌿 **Real-Time Eco Scoring** — CO₂ tracking with letter grades and carbon offset estimates
- 🗺️ **TSP Route Optimization** — Google OR-Tools to find the most efficient stop order
- 💰 **True Cost Estimation** — Fuel, hotels, food, park fees, wear & tear in one dashboard

---

## ✨ Features

### 🧠 Adventure Personality Profiler
Uses **K-Means clustering** to classify users into one of 5 adventure profiles based on their preferences:

| Profile | Style |
|---------|-------|
| 🏔️ Peak Chaser | Mountains, summits, alpine trails |
| 🌊 Coast Cruiser | Beaches, coastal roads, surf spots |
| 🌲 Forest Wanderer | National parks, camping, wildlife |
| 🏜️ Desert Drifter | Canyons, desert landscapes, stargazing |
| ⚡ Thrill Seeker | Extreme sports, cliff diving, zip lines |

### 🌿 Eco Score System
Every route receives a **real-time CO₂ grade**:

```
A+ 🌱  < 40 kg CO₂    Exceptional
A  🌿  < 70 kg CO₂    Great
B  🍃  < 110 kg CO₂   Good
C  🌾  < 160 kg CO₂   Average
D  ⚠️  < 220 kg CO₂   Poor
F  🔴  220+ kg CO₂    High Impact
```

### 🗺️ Route Optimization (TSP)
Powered by **Google OR-Tools** with a greedy nearest-neighbor fallback — finds the optimal order to visit all your stops minimizing total drive time and distance.

### 💰 True Cost Calculator
Goes beyond just gas — calculates your **real total trip cost**:

| Cost Factor | Data Source |
|---|---|
| ⛽ Fuel | Distance ÷ MPG × Live Gas Price (EIA API) |
| 🏨 Hotel / Camping | City-level estimates + Airbnb dataset |
| 🍔 Food | Days × per-person daily budget |
| 🎟️ Park Entry Fees | NPS API |
| 🔧 Car Wear & Tear | $0.08/mile standard rate |
| 🌿 Carbon Offset | $15/tonne market rate |

### 🗺️ Animated Interactive Map
Built with **Folium + AntPath** — animated route lines color-coded to your adventure profile with live weather overlays at each stop.

---

## 🖥️ Demo

```
👤 Adventure Profile:  🏔️ Peak Chaser (confidence: 94%)
🛣️  Optimized Route:   SF → Yosemite → Lake Tahoe → Crater Lake → Mt. Rainier
📍 Total Distance:    1,247 miles
⏱️  Total Drive Time:  18.5 hours
💰 Total Trip Cost:   $634
⛽ Fuel Cost:         $189
🌿 Eco Score:         B+ 🍃 (87 kg CO₂)
🌱 Carbon Offset:     $1.31 to neutralize
👥 Best Time:         October — 40% fewer crowds
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ecoventure.git
cd ecoventure

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Add your API keys to .env

# 5. Launch the app
streamlit run app.py
```

---

## 🔑 API Keys

All APIs used are **100% free**:

| Service | Purpose | Free Tier | Signup |
|---|---|---|---|
| **OpenRouteService** | Geocoding + Distance Matrix | 2,000 req/day | [openrouteservice.org](https://openrouteservice.org) |
| **OpenWeatherMap** | Live weather at stops | 1,000 calls/day | [openweathermap.org](https://openweathermap.org/api) |
| **EIA API** | Real-time US gas prices | Unlimited | [eia.gov/opendata](https://www.eia.gov/opendata) |
| **NPS API** | National Park data & fees | Unlimited | [nps.gov/developer](https://www.nps.gov/subjects/developer/get-started.htm) |

Add keys to your `.env` file:

```env
ORS_API_KEY=your_openrouteservice_key
OWM_API_KEY=your_openweathermap_key
EIA_API_KEY=your_eia_key
NPS_API_KEY=your_nps_key
```

---

## 📁 Project Structure

```
ecoventure/
│
├── app.py                     # Streamlit UI — main entry point
├── requirements.txt
├── .env.example
│
└── src/
    ├── data_collection.py     # Geocoding, distances, weather, gas prices
    ├── profiler.py            # K-Means adventure personality classifier
    ├── eco_scorer.py          # CO₂ calculator + A+ to F grading system
    ├── route_optimizer.py     # OR-Tools TSP + greedy fallback
    ├── cost_calculator.py     # Full trip budget breakdown
    └── visualizer.py         # Folium animated map builder
```

---

## 🤖 ML Models

### K-Means Clustering — Adventure Profiler (`src/profiler.py`)
- **Input**: 5 user preference scores (hiking, water, camping, wildlife, extreme) rated 1–10
- **Method**: K-Means with 5 clusters trained on prototype preference vectors
- **Output**: Adventure profile + confidence score (0–1)

### TSP Optimization — Route Optimizer (`src/route_optimizer.py`)
- **Input**: N×N distance matrix (meters)
- **Method**: Google OR-Tools Guided Local Search with PATH_CHEAPEST_ARC initialization
- **Fallback**: Greedy nearest-neighbor algorithm
- **Output**: Optimal stop order + total distance

### CO₂ Regression — Eco Scorer (`src/eco_scorer.py`)
- **Formula**: `CO₂ (kg) = (distance_miles / mpg) × 8.89 × car_multiplier`
- **Car multipliers**: Sedan (1.0×), SUV (1.15×), Hybrid (0.70×), EV (0.20×)
- **Output**: CO₂ kg, letter grade, equivalent trees, offset cost

---

## 📊 Tech Stack

```
Frontend       →  Streamlit
Maps           →  Folium + AntPath
ML / Optimize  →  scikit-learn, Google OR-Tools
Data           →  Pandas, NumPy
APIs           →  OpenRouteService, OpenWeatherMap, EIA, NPS
Visualization  →  Folium, Streamlit metrics
```

---

## 🗺️ Roadmap

- [ ] EV charging station stop integration
- [ ] Multi-day itinerary builder with overnight suggestions
- [ ] Crowd prediction by month (Google Trends + NPS visitor data)
- [ ] Export route to Google Maps / PDF
- [ ] Side-by-side comparison: Gas vs Hybrid vs EV route
- [ ] AllTrails API integration for trail-level stop recommendations
- [ ] Mobile-responsive PWA version

---

## 🙋 Author

**Sumanth Kotla
MS Business Analytics — University of North Texas

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Built with 🌿 for adventure travelers who care about the planet.
</div>
