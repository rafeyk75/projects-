from __future__ import annotations
import argparse, requests, sys, math
from typing import Tuple, Optional, Dict
from cache import Cache, DEFAULT_TTL

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def geocode(city: str, cache: Cache) -> Tuple[float, float, str]:
    key = f"geo::{city.lower()}"
    cached = cache.get(key, ttl=30*24*3600)
    if cached:
        return cached["lat"], cached["lon"], cached["name"]
    resp = requests.get(GEO_URL, params={"name": city, "count": 1})
    resp.raise_for_status()
    data = resp.json()
    if not data.get("results"):
        raise SystemExit(f"No match for city '{city}'.")
    r = data["results"][0]
    lat, lon = r["latitude"], r["longitude"]
    name = f"{r['name']}, {r.get('admin1', '')} {r.get('country_code','')}".strip()
    cache.set(key, {"lat": lat, "lon": lon, "name": name})
    return lat, lon, name

def forecast(lat: float, lon: float, days: int, units: str, cache: Cache) -> Dict:
    units_key = "us" if units == "imperial" else "si"
    key = f"fc::{lat:.3f},{lon:.3f}::{days}::{units_key}"
    cached = cache.get(key, ttl=DEFAULT_TTL)
    if cached:
        return cached
    params = {
        "latitude": lat, "longitude": lon,
        "daily": ["temperature_2m_max","temperature_2m_min","precipitation_sum","windspeed_10m_max"],
        "current_weather": True,
        "timezone": "auto",
        "forecast_days": days,
        "temperature_unit": "fahrenheit" if units=="imperial" else "celsius",
        "windspeed_unit": "mph" if units=="imperial" else "kmh",
        "precipitation_unit": "inch" if units=="imperial" else "mm"
    }
    resp = requests.get(FORECAST_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    cache.set(key, data)
    return data

def format_table(data: Dict, units: str) -> str:
    daily = data["daily"]
    rows = ["Date        MaxT  MinT  Wind  Precip"]
    rows.append("-------------------------------------")
    for i, date in enumerate(daily["time"]):
        tmax = daily["temperature_2m_max"][i]
        tmin = daily["temperature_2m_min"][i]
        wind = daily["windspeed_10m_max"][i]
        prcp = daily["precipitation_sum"][i]
        rows.append(f"{date}  {tmax:4.0f}  {tmin:4.0f}  {wind:4.0f}  {prcp:5.2f}")
    utemp = "°F" if units=="imperial" else "°C"
    uw = "mph" if units=="imperial" else "km/h"
    up = "in" if units=="imperial" else "mm"
    legend = f"(Temps {utemp}, wind {uw}, precip {up})"
    return "\n".join(rows + [legend])

def main() -> None:
    ap = argparse.ArgumentParser(description="Weather CLI using Open‑Meteo with SQLite cache")
    ap.add_argument("city", type=str, help="City name, e.g. 'Minneapolis'")
    ap.add_argument("--days", type=int, default=7, help="Days of forecast 1–16")
    ap.add_argument("--units", choices=["metric","imperial"], default="metric")
    ap.add_argument("--ttl", type=int, default=DEFAULT_TTL, help="Cache TTL seconds")
    args = ap.parse_args()

    if not (1 <= args.days <= 16):
        raise SystemExit("--days must be 1..16")

    cache = Cache()
    lat, lon, display = geocode(args.city, cache)
    data = forecast(lat, lon, args.days, args.units, cache)
    print(display)
    cw = data.get("current_weather", {})
    if cw:
        print(f"Now: {cw.get('temperature')} {'°F' if args.units=='imperial' else '°C'}, wind {cw.get('windspeed')} {'mph' if args.units=='imperial' else 'km/h'}")
    print(format_table(data, args.units))

if __name__ == "__main__":
    main()
