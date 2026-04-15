# Morning Digest

Automated daily digest delivered every morning via email.

Combines three data sources into one clean report:
- Weather forecast for Prague (OpenWeatherMap)
- Currency rates (CZK/USD/EUR/GBP) via ExchangeRate API
- Top 5 HackerNews stories of the day

Runs fully serverless via GitHub Actions. No persistent infrastructure required.

## How it works

1. GitHub Actions triggers the workflow every morning at 7:00 AM CET
2. Python script fetches data from all three APIs in parallel
3. Digest is formatted and sent via email (SMTP)

## Setup

### 1. API Keys

| Service | URL | Free tier |
|---------|-----|-----------|
| OpenWeatherMap | https://openweathermap.org/api | Yes |
| ExchangeRate API | https://www.exchangerate-api.com | Yes |
| Email (SMTP) | Gmail App Password | Yes |

### 2. GitHub Actions Secrets

Add these secrets in your repository Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key |
| `EXCHANGERATE_API_KEY` | ExchangeRate API key |
| `SMTP_EMAIL` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password (not your login password) |
| `RECIPIENT_EMAIL` | Where to send the digest |

### 3. Gmail App Password

1. Go to myaccount.google.com → Security → 2-Step Verification → App passwords
2. Generate a new App Password for "Mail"
3. Use that as `SMTP_PASSWORD` — not your Gmail login password

## Deployment

Push to GitHub. The workflow runs automatically at 7:00 AM CET.

To trigger manually: Actions → Morning Digest → Run workflow

## Tech stack

- Python 3.10+
- GitHub Actions (cron)
- OpenWeatherMap API
- ExchangeRate API
- HackerNews public API (no key required)
- SMTP (Gmail)

## Output example

```
=== Morning Digest — Wed Apr 15 ===

WEATHER — Prague
Condition: Clear sky
Temperature: 14°C (feels like 11°C)
Humidity: 58% | Wind: 3.2 m/s
UV Index: 4.1

CURRENCY RATES (base: CZK)
1 USD = 22.84 CZK
1 EUR = 24.71 CZK
1 GBP = 28.93 CZK

TOP 5 ON HACKERNEWS
1. Show HN: I built a local-first AI coding assistant
   https://news.ycombinator.com/item?id=XXXXXXX
2. ...
```

## License

MIT
