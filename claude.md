# RPG Player Account System

## Current Status: Deployed to Railway

## Project Overview
Telegram Mini App for RPG player accounts with Fallout-style retro UI. Bot is minimal (only /start with WebApp button), all functionality in web app.

## Tech Stack
- Backend: FastAPI + aiogram 3 (minimal)
- Frontend: Svelte + Vite
- Database: Google Sheets (Service Account)
- Deployment: Railway.app (free tier)

## Deployment
- **URL**: https://rpg-app-production.up.railway.app
- **GitHub**: git@github.com:whereismyguts/rpg-app.git (master branch)

## Architecture
- **Bot**: Only `/start` command with WebApp button
- **Web App**: Full functionality (login, balance, stats, send caps, QR scanner)

## Web App Features
- Login via QR code (camera) or UUID text input
- View balance and SPECIAL stats
- Send caps to other players (QR scan or UUID)
- Fallout terminal retro styling

## Key Files
- `backend/main.py` - FastAPI + aiogram entry point
- `backend/bot/handlers/start.py` - Minimal /start handler
- `backend/bot/keyboards.py` - WebApp button only
- `backend/services/sheets.py` - Google Sheets integration
- `backend/api/` - REST API for web app
- `frontend/src/App.svelte` - Main app component
- `frontend/src/components/` - Svelte components

## Google Sheet Structure

### Users Sheet (7 columns)
| user_id | player_uuid | name | profession | balance | band | attributes_json |

### Attributes Sheet (4 columns)
| attribute_name | display_name | max_value | description |

## Local Development
```bash
docker compose up -d --build
# Frontend: http://localhost:5174
# Backend: http://localhost:8001
```
