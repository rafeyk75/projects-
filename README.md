# Weather CLI (Open‑Meteo, cached)

Simple CLI to fetch current weather and a 7‑day forecast for a city using Open‑Meteo and its free geocoding.
Results are cached in SQLite with a configurable TTL to avoid repeated network calls.

## Features
- `weather CITY [--days N] [--units metric|imperial]`
- Geocoding via Open‑Meteo
- Forecast via Open‑Meteo
- SQLite cache with TTL (default 2 hours)
- Graceful fallbacks when API is unavailable
- Type hints and docstrings
- Minimal tests

## Quick start
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python weather.py "Minneapolis" --days 5 --units imperial
```

## Tests
```bash
pytest -q
```

## Notes
- No API key required.
- Cache file: `.weather_cache.sqlite`.
