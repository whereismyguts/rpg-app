# RPG Player Account System

Telegram bot + Web app for RPG player accounts with Fallout-style retro UI.

## Features

- Telegram bot with `/start`, `/balance`, `/stats`, `/send` commands
- Web app (Telegram WebApp) with retro-futuristic Fallout terminal UI
- Google Sheets as database
- QR code generation and scanning for player identification
- Money transfer between players
- Customizable SPECIAL-style attributes

## Tech Stack

- **Backend**: FastAPI + aiogram 3
- **Frontend**: Svelte + Vite
- **Database**: Google Sheets (via Service Account)
- **Deployment**: Railway.app / Docker

## Setup

### 1. Google Sheets Setup

Create a Google Sheet with two worksheets:

**Users** (columns A-G):
| user_id | player_uuid | name | profession | balance | band | attributes_json |

**Attributes** (columns A-D):
| attribute_name | display_name | max_value | description |

Example attributes:
```
strength, Strength, 10, Physical power
perception, Perception, 10, Awareness
endurance, Endurance, 10, Stamina
charisma, Charisma, 10, Social skills
intelligence, Intelligence, 10, Mental acuity
agility, Agility, 10, Speed and reflexes
luck, Luck, 10, Fortune
```

### 2. Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API
4. Create a Service Account
5. Download the JSON credentials
6. Share your Google Sheet with the service account email

### 3. Telegram Bot

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get the bot token
3. Set the WebApp URL (after deployment)

### 4. Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
BOT_TOKEN=your_telegram_bot_token
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
PASSWORD_ENABLED=false
APP_PASSWORD=
SECRET_KEY=generate_a_random_string
WEBAPP_URL=https://your-app.up.railway.app
```

## Local Development

### Using Docker Compose

```bash
docker compose up -d --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Deployment (Railway)

1. Push to GitHub
2. Create account on [Railway.app](https://railway.app/)
3. New Project → Deploy from GitHub
4. Add environment variables in Railway dashboard
5. Railway auto-builds using `Dockerfile`
6. Get the deployed URL (`*.up.railway.app`)
7. Set this URL in BotFather (`/setmenubutton`)

## Project Structure

```
rpg-app/
├── Dockerfile              # Production multi-stage build
├── docker-compose.yml      # Local development
├── railway.json            # Railway config
├── backend/
│   ├── main.py             # FastAPI + aiogram entry
│   ├── config/settings.py  # Environment config
│   ├── bot/handlers/       # Telegram bot commands
│   ├── api/                # REST endpoints
│   └── services/           # Google Sheets, QR generation
└── frontend/
    ├── src/
    │   ├── App.svelte
    │   ├── components/     # Login, Home, Stats, Transfer
    │   └── styles/         # Fallout terminal CSS
    └── vite.config.js
```
