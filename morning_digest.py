import os
import smtplib
import asyncio
import aiohttp
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Config from environment ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

CITY = "Prague"
BASE_CURRENCY = "CZK"
TARGET_CURRENCIES = ["USD", "EUR", "GBP"]
HN_TOP_N = 5


# --- Fetchers ---

async def fetch_weather(session):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "en"
    }
    async with session.get(url, params=params) as r:
        data = await r.json()
    
    if "coord" not in data:
        raise ValueError(f"OpenWeather error: {data}")
    
    url_uvi = "https://api.openweathermap.org/data/2.5/uvi"
    coords = data["coord"]
    params_uvi = {
        "appid": OPENWEATHER_API_KEY,
        "lat": coords["lat"],
        "lon": coords["lon"]
    }
    async with session.get(url_uvi, params=params_uvi) as r:
        uvi_data = await r.json()

    return {
        "condition": data["weather"][0]["description"].capitalize(),
        "temp": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),
        "humidity": data["main"]["humidity"],
        "wind": round(data["wind"]["speed"], 1),
        "uvi": round(uvi_data.get("value", 0), 1)
    }


async def fetch_rates(session):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/CZK"
    async with session.get(url) as r:
        data = await r.json()
    
    rates = data.get("conversion_rates", {})
    result = {}
    for currency in TARGET_CURRENCIES:
        if currency in rates and rates[currency] != 0:
            result[currency] = round(1 / rates[currency], 2)
    return result


async def fetch_hn(session):
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    async with session.get(url) as r:
        ids = await r.json()

    stories = []
    for story_id in ids[:HN_TOP_N]:
        url_item = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        async with session.get(url_item) as r:
            item = await r.json()
        stories.append({
            "title": item.get("title", "No title"),
            "url": item.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
            "score": item.get("score", 0)
        })
    return stories


# --- Formatter ---

def format_digest(weather, rates, hn_stories):
    today = datetime.now().strftime("%a %b %d, %Y")
    lines = []

    lines.append(f"=== Morning Digest — {today} ===\n")

    lines.append(f"WEATHER — {CITY}")
    lines.append(f"Condition : {weather['condition']}")
    lines.append(f"Temperature: {weather['temp']}°C (feels like {weather['feels_like']}°C)")
    lines.append(f"Humidity  : {weather['humidity']}% | Wind: {weather['wind']} m/s")
    lines.append(f"UV Index  : {weather['uvi']}\n")

    lines.append(f"CURRENCY RATES (base: {BASE_CURRENCY})")
    for currency, rate in rates.items():
        lines.append(f"1 {currency} = {rate} {BASE_CURRENCY}")
    lines.append("")

    lines.append(f"TOP {HN_TOP_N} ON HACKERNEWS")
    for i, story in enumerate(hn_stories, 1):
        lines.append(f"{i}. {story['title']} (score: {story['score']})")
        lines.append(f"   {story['url']}")
    lines.append("")

    return "\n".join(lines)


# --- Email sender ---

def send_email(body):
    today = datetime.now().strftime("%a %b %d")
    subject = f"Morning Digest — {today}"

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"Digest sent to {RECIPIENT_EMAIL}")


# --- Main ---

async def main():
    async with aiohttp.ClientSession() as session:
        weather, rates, hn = await asyncio.gather(
            fetch_weather(session),
            fetch_rates(session),
            fetch_hn(session)
        )

    digest = format_digest(weather, rates, hn)
    print(digest)
    send_email(digest)


if __name__ == "__main__":
    asyncio.run(main())
