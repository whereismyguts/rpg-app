from aiogram import Router

from .start import router as start_router
from .balance import router as balance_router
from .stats import router as stats_router
from .send import router as send_router

main_router = Router()
main_router.include_router(start_router)
main_router.include_router(balance_router)
main_router.include_router(stats_router)
main_router.include_router(send_router)

__all__ = ["main_router"]
