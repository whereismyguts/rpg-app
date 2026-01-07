# Google Sheets Setup Guide

## Step 1: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it (e.g., "RPG Player Database")
4. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
   The ID is the long string between `/d/` and `/edit`

## Step 2: Create Worksheets

### Worksheet 1: Users

1. Rename "Sheet1" to **Users** (right-click tab → Rename)
2. Add headers in row 1:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| user_id | player_uuid | name | profession | balance | band | attributes_json |

3. Format columns:
   - Column A (user_id): Number
   - Column E (balance): Number
   - Other columns: Text

### Worksheet 2: Attributes

1. Click **+** button at bottom to add new sheet
2. Rename it to **Attributes**
3. Add headers in row 1:

| A | B | C | D |
|---|---|---|---|
| attribute_name | display_name | max_value | description |

4. Add your attributes (example SPECIAL):

| attribute_name | display_name | max_value | description |
|----------------|--------------|-----------|-------------|
| strength | Strength | 10 | Physical power and carrying capacity |
| perception | Perception | 10 | Environmental awareness and accuracy |
| endurance | Endurance | 10 | Health and resistance to damage |
| charisma | Charisma | 10 | Speech and barter effectiveness |
| intelligence | Intelligence | 10 | Skill points and dialogue options |
| agility | Agility | 10 | Action points and sneaking ability |
| luck | Luck | 10 | Critical chance and random encounters |

## Step 3: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Name: `rpg-app` (or any name)
4. Click **Create**
5. Wait for project creation, then select it

## Step 4: Enable Google Sheets API

1. In Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click on it → Click **Enable**
4. Wait for activation

## Step 5: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **Service account**
3. Fill in:
   - Service account name: `rpg-app-sheets`
   - Service account ID: auto-generated
   - Description: "Access to RPG player database"
4. Click **Create and Continue**
5. Skip "Grant access" steps → Click **Done**

## Step 6: Create Service Account Key

1. In Credentials page, find your service account
2. Click on the service account email
3. Go to **Keys** tab
4. Click **Add Key** → **Create new key**
5. Select **JSON** → Click **Create**
6. **A JSON file will download** - this is your credentials!

## Step 7: Share Sheet with Service Account

1. Open the downloaded JSON file
2. Find the `"client_email"` field - it looks like:
   ```
   "client_email": "rpg-app-sheets@your-project.iam.gserviceaccount.com"
   ```
3. Copy this email address
4. Go back to your Google Sheet
5. Click **Share** button (top right)
6. Paste the service account email
7. Set permission to **Editor**
8. Uncheck "Notify people"
9. Click **Share**

## Step 8: Add Credentials to Project

### Option A: Using JSON file directly (local development)

1. Create credentials folder:
   ```bash
   mkdir -p /home/karmanov/projects/rpg-app/credentials
   ```

2. Copy downloaded JSON to project:
   ```bash
   cp ~/Downloads/your-project-xxxxx.json /home/karmanov/projects/rpg-app/credentials/service_account.json
   ```

3. Update `.env` file:
   ```env
   GOOGLE_SHEET_ID=your_spreadsheet_id_here
   GOOGLE_CREDENTIALS_FILE=credentials/service_account.json
   ```

### Option B: Using JSON as environment variable (Railway/production)

1. Open the downloaded JSON file
2. Copy the entire content
3. Minify it (remove newlines) - use [JSON Minifier](https://jsonformatter.org/json-minify)
4. Add to `.env`:
   ```env
   GOOGLE_SHEET_ID=your_spreadsheet_id_here
   GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"..."}
   ```

## Step 9: Update Settings for JSON Variable

The project is already configured to accept credentials as JSON string. In `backend/config/settings.py`:

```python
@property
def google_credentials(self) -> dict:
    if self.google_credentials_json:
        return json.loads(self.google_credentials_json)
    return {}
```

And in `backend/services/sheets.py`:

```python
creds = Credentials.from_service_account_info(
    settings.google_credentials,
    scopes=self.SCOPES,
)
```

## Step 10: Verify Setup

1. Create `.env` file:
   ```bash
   cd /home/karmanov/projects/rpg-app
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   GOOGLE_SHEET_ID=1ABC123xyz...
   GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
   PASSWORD_ENABLED=false
   SECRET_KEY=any_random_string_here
   WEBAPP_URL=
   ```

3. Test connection (Python):
   ```bash
   cd backend
   python -c "
   from services.sheets import sheets_service
   print('Users sheet:', sheets_service.get_users_sheet())
   print('Attributes:', sheets_service.get_attribute_config())
   print('SUCCESS!')
   "
   ```

## Troubleshooting

### Error: "The caller does not have permission"
- Make sure you shared the sheet with the service account email
- Check that the email is exactly as shown in the JSON file

### Error: "Requested entity was not found"
- Verify the GOOGLE_SHEET_ID is correct
- Make sure the sheet exists and is accessible

### Error: "Could not deserialize key data"
- The JSON might be malformed
- Try re-downloading the key from Google Cloud Console

### Error: "Worksheet not found"
- Ensure worksheets are named exactly "Users" and "Attributes"
- Sheet names are case-sensitive

## Example .env File

```env
# Telegram Bot (get from @BotFather)
BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Sheets
GOOGLE_SHEET_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"rpg-app-123456","private_key_id":"abc123","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg...\n-----END PRIVATE KEY-----\n","client_email":"rpg-app-sheets@rpg-app-123456.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/rpg-app-sheets%40rpg-app-123456.iam.gserviceaccount.com"}

# Security
PASSWORD_ENABLED=false
APP_PASSWORD=
SECRET_KEY=my-super-secret-key-change-in-production

# App
WEBAPP_URL=
LOG_LEVEL=INFO
```

## Quick Checklist

- [ ] Created Google Sheet with correct name
- [ ] Created "Users" worksheet with 7 columns
- [ ] Created "Attributes" worksheet with 4 columns
- [ ] Added attribute rows (at least one)
- [ ] Created Google Cloud project
- [ ] Enabled Google Sheets API
- [ ] Created Service Account
- [ ] Downloaded JSON key file
- [ ] Shared sheet with service account email (as Editor)
- [ ] Added GOOGLE_SHEET_ID to .env
- [ ] Added GOOGLE_CREDENTIALS_JSON to .env
- [ ] Tested connection successfully
