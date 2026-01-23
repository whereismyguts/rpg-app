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
- Universal QR scanner with routing by QR type
- Login via QR code (camera) or UUID text input
- View balance and SPECIAL stats
- Send caps to other players
- Purchase items (scan item QR)
- Apply perks (scan perk QR)
- Fallout terminal retro styling

## QR Code Formats
```
LOGIN:UUID        # login as user
PAY:ITEM_ID       # purchase item
SEND:UUID         # send money to user
PERK:PERK_ID      # apply perk
```

## Google Sheet Structure

### Users Sheet
| user_id | player_uuid | name | profession | balance | band | attributes_json |

### Attributes Sheet
| attribute_name | display_name | max_value | description |

### Items Sheet
| item_id | name | description | price | image_url |

### Perks Sheet
| perk_id | name | description | effect_type | effect_value | one_time |

### UserPerks Sheet
| player_uuid | perk_id | applied_at |

## Effect Types for Perks
- `attr_strength`, `attr_perception`, etc. - modify attribute
- `balance` - add/subtract caps

## Key Files
- `backend/main.py` - FastAPI + aiogram entry point
- `backend/bot/handlers/start.py` - Minimal /start handler
- `backend/services/sheets.py` - Google Sheets integration
- `backend/api/qr.py` - QR parsing API
- `backend/api/items.py` - Items purchase API
- `backend/api/perks.py` - Perks application API
- `frontend/src/App.svelte` - Main app with QR routing
- `frontend/src/components/QRScanner.svelte` - Camera scanner
- `frontend/src/components/PayItem.svelte` - Item purchase
- `frontend/src/components/ApplyPerk.svelte` - Perk application

## Local Development
```bash
docker compose up -d --build
# Frontend: http://localhost:5174
# Backend: http://localhost:8001
```
