"""
Terraquipu - Deterministic Multicriteria Scoring Engine
Combines agronomic thresholds with environmental diagnostics to evaluate crop suitability.
"""
import json
from typing import Dict, Any, List

def calculate_suitability(crop: Dict[str, Any], diagnosis: Dict[str, Any], previous_crop_id: str) -> Dict[str, Any]:
    projected_rain = diagnosis["climate_context"]["projected_season_rainfall_mm"]
    elevation = diagnosis["location"]["elevation_masl"]
    soil_ph = diagnosis["soil_health_profile"]["ph"]
    
    # 1. Water adequacy score (0 to 100)
    w_min = crop["water_requirement_mm"]["min"]
    w_opt = crop["water_requirement_mm"]["optimal"]
    if projected_rain >= w_opt:
        water_score = 100.0
    elif projected_rain >= w_min:
        water_score = 60.0 + 40.0 * ((projected_rain - w_min) / (w_opt - w_min))
    else:
        deficit_ratio = max(0.0, projected_rain / w_min)
        water_score = max(0.0, deficit_ratio * 50.0)

    # 2. Elevation score
    alt_min = crop["altitude_range_masl"]["min"]
    alt_max = crop["altitude_range_masl"]["max"]
    alt_score = 100.0 if alt_min <= elevation <= alt_max else 30.0

    # 3. Soil pH score
    ph_min = crop["soil_tolerance"]["ph_min"]
    ph_max = crop["soil_tolerance"]["ph_max"]
    ph_score = 100.0 if ph_min <= soil_ph <= ph_max else 40.0

    # 4. Crop rotation & pest break score
    if previous_crop_id in crop.get("unfavorable_successors", []):
        rotation_score = 10.0  # Monoculture penalty
    elif previous_crop_id in crop.get("favorable_successors", []):
        rotation_score = 100.0  # Favorable rotation bonus
    else:
        rotation_score = 60.0

    # Soil regeneration bonus (e.g. Legumes fixing N)
    n_balance = crop["soil_impact"]["nitrogen_balance_kg_ha"]
    soil_regen_bonus = 10.0 if n_balance > 0 else 0.0

    # Weighted final score
    final_score = (
        0.40 * water_score +
        0.25 * rotation_score +
        0.20 * alt_score +
        0.15 * ph_score +
        soil_regen_bonus
    )
    final_score = min(100.0, round(final_score, 1))

    return {
        "crop_id": crop["crop_id"],
        "common_name": crop["common_name"],
        "suitability_score": final_score,
        "water_score": round(water_score, 1),
        "rotation_score": rotation_score,
        "nitrogen_balance_kg_ha": n_balance
    }

if __name__ == "__main__":
    # Test execution
    with open("crop_matrix.json", "r", encoding="utf-8") as f:
        matrix = json.load(f)

    sample_diagnosis = {
        "location": {"elevation_masl": 3410},
        "climate_context": {"projected_season_rainfall_mm": 510.0},
        "soil_health_profile": {"ph": 6.1}
    }

    print("Evaluando compatibilidad tras siembra de Papa Nativa con sequía El Niño:")
    for crop in matrix["crops"]:
        res = calculate_suitability(crop, sample_diagnosis, previous_crop_id="papa_nativa")
        print(f"- {res['common_name']}: Score {res['suitability_score']}/100 (Balance N: {res['nitrogen_balance_kg_ha']} kg/ha)")
