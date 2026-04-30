# 🌿 EcoVenture — Road Trip Optimizer

> The first road trip planner built for adventure travelers that optimizes for **experience AND environmental impact**.

---

## 🚀 Quick Start

```bash
# 1. Clone & enter the project
cd ecoventure

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
# Edit .env and add your keys (see API Keys section below)

# 4. Run the app
streamlit run app.py
```

---

## 📁 Project Structure

```
ecoventure/
├── app.py                    ← Streamlit UI (main entry point)
├── requirements.txt
├── .env.example
└── src/
    ├── data_collection.py    ← Geocoding, distances, weather, gas prices
    ├── profiler.py           ← K-Means adventure personality classifier
    ├── eco_scorer.py         ← CO2 calculator + eco grade (A+ to F)
    ├── route_optimizer.py    ← OR-Tools TSP + greedy fallback
    ├── cost_calculator.py    ← Full trip budget breakdown
    └── visualizer.py         ← Folium interactive map builder
```

---

## 🔑 API Keys (All Free)

| API | Purpose | Signup |
|-----|---------|--------|
| OpenRouteService | Geocoding + distance matrix | https://openrouteservice.org |
| OpenWeatherMap | Weather at each stop | https://openweathermap.org/api |
| EIA | Real-time US gas prices | https://www.eia.gov/opendata |
| NPS | National Park info | https://www.nps.gov/subjects/developer/get-started.htm |

---

## ✨ Unique Features

| Feature | How It Works |
|---------|-------------|
| 🧠 Adventure Profiler | K-Means clustering on 5 preference scores → 1 of 5 profiles |
| 🌿 Eco Score | CO2 kg → letter grade A+ to F + carbon offset cost |
| 🗺️ TSP Optimizer | OR-Tools solver finds optimal stop order |
| 💰 True Cost | Fuel + hotel + food + park fees + wear & tear + offset |
| 🌤️ Weather | Live weather at every stop |
| 🗺️ Animated Map | Folium + AntPath animated route |

---

## 🧠 ML Models Used

- **K-Means Clustering** — Adventure personality profiler (`profiler.py`)
- **TSP via OR-Tools** — Constrained route optimization (`route_optimizer.py`)
- **Greedy Nearest Neighbor** — Fallback optimizer

---

## 📊 Sample Output

```
👤 Adventure Profile:  🏔️ Peak Chaser
🛣️  Total Distance:    847 miles
⏱️  Drive Time:        13.2 hours
💰 Total Cost:        $512
🌿 Eco Score:         B 🍃 (98.4 kg CO₂)
🌱 Carbon Offset:     $1.47 to neutralize
```

---

## 🛣️ Roadmap

- [ ] EV charging station stops
- [ ] Multi-day itinerary builder
- [ ] Crowd prediction by month
- [ ] Export to Google Maps / PDF
- [ ] Compare electric vs gas routes
