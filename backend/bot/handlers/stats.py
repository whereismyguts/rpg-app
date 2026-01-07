from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from services.sheets import sheets_service
from services.session import get_current_user

router = Router()


def format_stat_bar(value: int, max_value: int, width: int = 10) -> str:
    """Create a text-based stat bar."""
    filled = int((value / max_value) * width)
    bar = "[" + "#" * filled + "-" * (width - filled) + "]"
    return bar


def format_stats(stats: dict) -> str:
    """Format stats for display."""
    lines = [
        "S.P.E.C.I.A.L.",
        "==============",
        "",
    ]

    for attr in stats["attributes"]:
        bar = format_stat_bar(attr["value"], attr["max_value"])
        line = f"{attr['display_name'][:12]:<12} {bar} {attr['value']}/{attr['max_value']}"
        lines.append(line)

    if stats.get("profession"):
        lines.append("")
        lines.append(f"Profession: {stats['profession']}")

    if stats.get("band"):
        lines.append(f"Band: {stats['band']}")

    return "\n".join(lines)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    user = get_current_user(message.from_user.id, sheets_service)
    if not user:
        await message.answer("Not registered. Use /start first.")
        return

    stats = sheets_service.get_user_stats(user["player_uuid"])
    if stats:
        await message.answer(f"```\n{format_stats(stats)}\n```", parse_mode="MarkdownV2")
    else:
        await message.answer("Failed to load stats.")


@router.callback_query(F.data == "menu_stats")
async def callback_stats(callback: CallbackQuery):
    user = get_current_user(callback.from_user.id, sheets_service)
    if not user:
        await callback.message.answer("Not registered. Use /start first.")
        await callback.answer()
        return

    stats = sheets_service.get_user_stats(user["player_uuid"])
    if stats:
        await callback.message.answer(
            f"```\n{format_stats(stats)}\n```", parse_mode="MarkdownV2"
        )
    else:
        await callback.message.answer("Failed to load stats.")
    await callback.answer()
