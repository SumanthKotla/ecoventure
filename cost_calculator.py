from dataclasses import dataclass
 
WEAR_TEAR_PER_MILE = 0.08
FOOD_BUDGET_DEFAULT = 50
 
@dataclass
class TripCost:
    fuel_usd: float
    hotel_usd: float
    food_usd: float
    park_fees_usd: float
    wear_tear_usd: float
    carbon_offset_usd: float
    total_usd: float
 
    def breakdown(self) -> dict:
        return {
            "⛽ Fuel":           self.fuel_usd,
            "🏕️ Hotels/Camps":  self.hotel_usd,
            "🍔 Food":           self.food_usd,
            "🎟️ Park Fees":     self.park_fees_usd,
            "🔧 Wear & Tear":   self.wear_tear_usd,
            "🌿 Carbon Offset": self.carbon_offset_usd,
        }
 
NPS_FEES = {
    "yellowstone": 35, "yosemite": 35, "grand canyon": 35,
    "zion": 35, "arches": 35, "glacier": 35, "olympic": 30,
    "crater lake": 30, "joshua tree": 30, "acadia": 35,
    "great smoky": 0, "rocky mountain": 30,
}
 
def estimate_park_fee(stop_name: str) -> float:
    name_lower = stop_name.lower()
    for park, fee in NPS_FEES.items():
        if park in name_lower:
            return float(fee)
    return 0.0
 
def calculate_total_cost(
    total_distance_miles: float, mpg: float, gas_price: float,
    nights: int, avg_hotel_cost: float, days: int, stops: list[str],
    co2_offset_cost: float, food_per_day: float = FOOD_BUDGET_DEFAULT,
    num_people: int = 1,
) -> TripCost:
    fuel  = round((total_distance_miles / mpg) * gas_price, 2)
    hotel = round(nights * avg_hotel_cost, 2)
    food  = round(days * food_per_day * num_people, 2)
    park_fees = round(sum(estimate_park_fee(s) for s in stops), 2)
    wear  = round(total_distance_miles * WEAR_TEAR_PER_MILE, 2)
    offset = round(co2_offset_cost, 2)
    total = round(fuel + hotel + food + park_fees + wear + offset, 2)
    return TripCost(
        fuel_usd=fuel, hotel_usd=hotel, food_usd=food,
        park_fees_usd=park_fees, wear_tear_usd=wear,
        carbon_offset_usd=offset, total_usd=total,
    )
 