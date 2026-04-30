from dataclasses import dataclass
 
CO2_PER_GALLON_KG = 8.89
 
CAR_TYPES = {
    "Sedan":      {"mpg": 32,  "multiplier": 1.0},
    "SUV":        {"mpg": 24,  "multiplier": 1.15},
    "Truck":      {"mpg": 18,  "multiplier": 1.30},
    "Hybrid":     {"mpg": 50,  "multiplier": 0.70},
    "Electric":   {"mpg": 120, "multiplier": 0.20},
    "Motorcycle": {"mpg": 45,  "multiplier": 0.75},
}
 
@dataclass
class EcoResult:
    co2_kg: float
    grade: str
    grade_emoji: str
    fuel_gallons: float
    equivalent_trees: float
    offset_cost_usd: float
 
def calculate_eco_score(distance_miles: float, car_type: str, custom_mpg: float = None) -> EcoResult:
    car = CAR_TYPES.get(car_type, CAR_TYPES["Sedan"])
    mpg = custom_mpg if custom_mpg else car["mpg"]
    multiplier = car["multiplier"]
    gallons = distance_miles / mpg
    co2_kg = gallons * CO2_PER_GALLON_KG * multiplier
    co2_tonnes = co2_kg / 1000
    if co2_kg < 40:     grade, emoji = "A+", "🌱"
    elif co2_kg < 70:   grade, emoji = "A",  "🌿"
    elif co2_kg < 110:  grade, emoji = "B",  "🍃"
    elif co2_kg < 160:  grade, emoji = "C",  "🌾"
    elif co2_kg < 220:  grade, emoji = "D",  "⚠️"
    else:               grade, emoji = "F",  "🔴"
    return EcoResult(
        co2_kg=round(co2_kg, 2), grade=grade, grade_emoji=emoji,
        fuel_gallons=round(gallons, 2),
        equivalent_trees=round(co2_kg / 21.77, 1),
        offset_cost_usd=round(co2_tonnes * 15, 2),
    )
 
def eco_tip(grade: str) -> str:
    tips = {
        "A+": "🌟 Outstanding! Your trip is already very low impact.",
        "A":  "✅ Great job! Consider carpooling to push it to A+.",
        "B":  "👍 Good score. Traveling off-peak reduces idle emissions.",
        "C":  "💡 Try combining stops to cut 10–20% of your distance.",
        "D":  "🔁 Consider a hybrid rental — cuts CO2 by up to 40%.",
        "F":  "🚌 A train or bus alternative could cut emissions by 80%.",
    }
    return tips.get(grade, "")
 