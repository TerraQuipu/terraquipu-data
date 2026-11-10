"""
Terraquipu Data - NASA POWER Extractor & Climatology Analyzer
Downloads daily agroclimatic data from NASA POWER API and computes El Niño anomalies.
"""
import requests
import json
import argparse
from datetime import datetime

def extract_nasa_power(lat: float, lon: float, start_date: str = "20230101", end_date: str = "20231231", output_file: str = "cusco_nasa_power.json"):
    print(f"[*] Consultando NASA POWER API para coordenadas ({lat}, {lon}) entre {start_date} y {end_date}...")
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,ALLSKY_SFC_SW_DWN"
        f"&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start_date}&end={end_date}&format=JSON"
    )

    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Error al consultar NASA POWER API: HTTP {resp.status_code}")

    data = resp.json()
    params = data.get("properties", {}).get("parameter", {})

    precip = [v for v in params.get("PRECTOTCORR", {}).values() if v > -900]
    tmax = [v for v in params.get("T2M_MAX", {}).values() if v > -900]
    tmin = [v for v in params.get("T2M_MIN", {}).values() if v > -900]

    annual_rainfall = round(sum(precip), 1)
    avg_tmax = round(sum(tmax) / len(tmax), 1) if tmax else 0.0
    avg_tmin = round(sum(tmin) / len(tmin), 1) if tmin else 0.0

    # Baseline climatológico para valles interandinos (Cusco ~720 mm)
    baseline_annual_rainfall = 720.0
    anomaly_percent = round(((annual_rainfall - baseline_annual_rainfall) / baseline_annual_rainfall) * 100, 1)

    summary = {
        "metadata": {
            "source": "NASA POWER (Agroclimatology Community)",
            "latitude": lat,
            "longitude": lon,
            "period": f"{start_date} - {end_date}",
            "generated_at": datetime.utcnow().isoformat() + "Z"
        },
        "indicators": {
            "annual_rainfall_mm": annual_rainfall,
            "baseline_rainfall_mm": baseline_annual_rainfall,
            "rainfall_anomaly_percent": anomaly_percent,
            "avg_tmax_celsius": avg_tmax,
            "avg_tmin_celsius": avg_tmin,
            "frost_days_recorded": sum(1 for t in tmin if t <= 0.0)
        },
        "raw_parameter_count": len(precip)
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[+] Extracción exitosa. Resumen guardado en {output_file}:")
    print(f"    - Lluvia total: {annual_rainfall} mm")
    print(f"    - Anomalía histórica: {anomaly_percent}%")
    print(f"    - Temp máxima promedio: {avg_tmax} °C")
    print(f"    - Días con helada (Tmin <= 0°C): {summary['indicators']['frost_days_recorded']}")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NASA POWER Data Extractor")
    parser.add_argument("--lat", type=float, default=-13.5321, help="Latitud WGS84 (Cusco/Chinchero)")
    parser.add_argument("--lon", type=float, default=-71.9675, help="Longitud WGS84")
    parser.add_argument("--start", type=str, default="20230101", help="Fecha inicio YYYYMMDD")
    parser.add_argument("--end", type=str, default="20231231", help="Fecha fin YYYYMMDD")
    parser.add_argument("--out", type=str, default="cusco_nasa_power.json", help="Archivo JSON de salida")
    args = parser.parse_args()

    extract_nasa_power(args.lat, args.lon, args.start, args.end, args.out)
