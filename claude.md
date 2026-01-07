# RPG Player Account System

## Current Status: Deployed to Railway

## Project Overview
Telegram bot + Svelte web app for RPG player accounts with Fallout-style retro UI. Uses Google Sheets as database.

## Tech Stack
- Backend: FastAPI + aiogram 3
- Frontend: Svelte + Vite
- Database: Google Sheets (Service Account)
- Deployment: Railway.app (free tier)

## Deployment
- **URL**: https://rpg-app-production.up.railway.app
- **GitHub**: git@github.com:whereismyguts/rpg-app.git (master branch)

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
- [x] Railway.app deployment
- [x] Base64-encoded credentials support for Railway
- [x] QR photo decoding in bot (pyzbar)
- [x] Disable auto Telegram auth (QR/UUID only login)

## Auth Flow
- Users must log in via QR code image or UUID text input
- Bot can decode QR codes from photos sent by users
- Telegram WebApp auth code preserved for future onboarding feature

## Future Tasks
- [ ] Telegram onboarding flow with character creation
- [ ] Perks system

## Key Files
- `backend/main.py` - FastAPI + aiogram entry point
- `backend/services/sheets.py` - Google Sheets integration
- `backend/services/qr_decoder.py` - QR decoding from images
- `backend/bot/handlers/qr_auth.py` - Photo QR auth handler
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

### Production (base64 encoded env var)
```
GOOGLE_CREDENTIALS_JSON=<base64 encoded service account json>
```
