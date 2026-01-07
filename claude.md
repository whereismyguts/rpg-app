# RPG Player Account System

## Current Status: Implementation Complete

## Project Overview
Telegram bot + Svelte web app for RPG player accounts with Fallout-style retro UI. Uses Google Sheets as database.

## Tech Stack
- Backend: FastAPI + aiogram 3
- Frontend: Svelte + Vite
- Database: Google Sheets (Service Account)
- Deployment: Railway.app (free tier)

## Completed Tasks
- [x] Project structure created
- [x] Backend FastAPI + aiogram setup
- [x] Google Sheets service (gspread)
- [x] Telegram bot handlers (/start, /balance, /stats, /send)
- [x] FastAPI endpoints (auth, users, transfer)
- [x] Svelte frontend setup
- [x] Fallout terminal CSS styling
- [x] All components (Login, Home, Stats, Transfer, QRScanner)
- [x] Docker configuration (dev + production)
- [x] Google Sheets setup documentation

## Next Steps
1. Follow `docs/GOOGLE_SHEETS_SETUP.md` for detailed setup
2. Create Telegram bot via @BotFather
3. Set up .env file with credentials
4. Test locally with `docker compose up`
5. Deploy to Railway.app
6. Set WebApp URL in BotFather

## Key Files
- `backend/main.py` - FastAPI + aiogram entry point
- `backend/services/sheets.py` - Google Sheets integration
- `backend/config/settings.py` - Environment configuration
- `backend/bot/handlers/` - Telegram commands
- `frontend/src/App.svelte` - Main app component
- `frontend/src/styles/global.css` - Fallout terminal styling
- `docs/GOOGLE_SHEETS_SETUP.md` - Detailed Google Sheets setup guide

## Google Sheet Structure

### Users Sheet (7 columns)
| user_id | player_uuid | name | profession | balance | band | attributes_json |

### Attributes Sheet (4 columns)
| attribute_name | display_name | max_value | description |

## Credentials Options

### Local Development (file-based)
```
credentials/service_account.json
```

### Production (environment variable)
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```
