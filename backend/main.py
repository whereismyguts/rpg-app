import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import settings
from bot.handlers import main_router
from api import auth, users, transfer

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Bot setup
bot = Bot(token=settings.bot_token)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)


async def start_bot():
    """Start bot polling in background."""
    logger.info("Starting Telegram bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start bot polling in background task
    bot_task = asyncio.create_task(start_bot())
    logger.info("Application started")
    yield
    # Cleanup
    await dp.stop_polling()
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass
    logger.info("Application stopped")


app = FastAPI(
    title="RPG Player Account API",
    description="Vault-Tec Player Terminal API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(transfer.router, prefix="/api/transfer", tags=["transfer"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "rpg-app"}


@app.get("/api/config")
async def get_config():
    """Get public app config."""
    return {
        "password_enabled": settings.password_enabled,
    }


# Serve static frontend files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/assets", StaticFiles(directory=static_path / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve frontend SPA."""
        file_path = static_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_path / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
