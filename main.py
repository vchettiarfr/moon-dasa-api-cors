
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import swisseph as swe
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nakshatra and planetary mappings
nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

planet_to_nakshatra = {
    "Ketu": ["Ashwini", "Magha", "Mula"],
    "Venus": ["Bharani", "Purva Phalguni", "Purva Ashadha"],
    "Sun": ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
    "Moon": ["Rohini", "Hasta", "Shravana"],
    "Mars": ["Mrigashira", "Chitra", "Dhanishta"],
    "Rahu": ["Ardra", "Swati", "Shatabhisha"],
    "Jupiter": ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
    "Saturn": ["Pushya", "Anuradha", "Uttara Bhadrapada"],
    "Mercury": ["Ashlesha", "Jyeshtha", "Revati"]
}

vimshottari_years = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
planet_order = list(vimshottari_years.keys())

def get_nakshatra_name(moon_long):
    deg = float(moon_long) % 360
    index = int(deg // (360 / 27))
    return nakshatras[index]

def nakshatra_to_planet(nakshatra_name):
    for planet, stars in planet_to_nakshatra.items():
        if nakshatra_name in stars:
            return planet
    return None

def rotate_planet_list(start_planet):
    idx = planet_order.index(start_planet)
    return planet_order[idx:] + planet_order[:idx]

def rotate_star_list(planet, start_star):
    stars = planet_to_nakshatra[planet]
    idx = stars.index(start_star)
    return stars[idx:] + stars[:idx]

def calculate_moon_nakshatra(date, latitude, longitude):
    swe.set_topo(longitude, latitude, 0)
    dt = datetime.strptime(date, "%Y-%m-%d")
    jd = swe.julday(dt.year, dt.month, dt.day, 0)
    moon_result = swe.calc_ut(jd, swe.MOON)
    moon_long = moon_result[0][0]
    return get_nakshatra_name(moon_long)

def expand_timeline(nakshatra, start, end):
    total_min = (end - start).total_seconds() / 60
    result = []

    dasa_nak = nakshatra
    dasa_planet = nakshatra_to_planet(dasa_nak)
    dasa_stars = rotate_star_list(dasa_planet, dasa_nak)

    bukti_planets = rotate_planet_list(dasa_planet)

    cursor = start
    for bukti in bukti_planets:
        bukti_frac = vimshottari_years[bukti] / 120
        bukti_min = total_min * bukti_frac
        bukti_start = cursor
        bukti_end = bukti_start + timedelta(minutes=bukti_min)

        bukti_naks = planet_to_nakshatra[bukti]
        bukti_nak = bukti_naks[0]  # pick first one always to simplify

        antra_cursor = bukti_start
        for antra in bukti_planets:
            antra_frac = vimshottari_years[antra] / 120
            antra_min = bukti_min * antra_frac
            antra_start = antra_cursor
            antra_end = antra_start + timedelta(minutes=antra_min)

            antra_nak = planet_to_nakshatra[antra][0]
            result.append({
                "dasa": dasa_nak,
                "bukti": bukti_nak,
                "antra": antra_nak,
                "start": antra_start.strftime("%d/%m/%Y %H:%M"),
                "end": antra_end.strftime("%d/%m/%Y %H:%M")
            })
            antra_cursor = antra_end

        cursor = bukti_end

    return result

@app.get("/moon_nakshatra_dasa")
def moon_nakshatra_dasa(date: str = Query(...), latitude: float = Query(...), longitude: float = Query(...)):
    try:
        base_time = datetime.strptime(date, "%Y-%m-%d")
        start = base_time
        end = base_time + timedelta(days=1)

        current_nakshatra = calculate_moon_nakshatra(date, latitude, longitude)
        timeline = expand_timeline(current_nakshatra, start, end)
        return {"timeline": timeline}
    except Exception as e:
        return {"error": str(e)}

