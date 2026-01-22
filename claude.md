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
- [x] Live camera QR scanner in web app (html5-qrcode)
- [x] QR photo support in bot /send flow (can scan recipient QR)

## Auth & Transfer Flow
Both bot and web have consistent QR/UUID input methods:

### Login
- **Bot**: Send photo of QR code OR use /login <UUID>
- **Web**: Scan QR with camera OR enter UUID manually

### Send Caps
- **Bot**: /send → enter UUID OR send photo of recipient's QR → enter amount → confirm
- **Web**: Enter UUID OR scan recipient QR with camera → enter amount → confirm

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
