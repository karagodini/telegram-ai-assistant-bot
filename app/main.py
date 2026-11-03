import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from . import config
from .handlers import init_kb, router


async def main() -> None:
    if not config.BOT_TOKEN:
        raise SystemExit("Заполните BOT_TOKEN в .env")
    if not config.OPENROUTER_API_KEY:
        raise SystemExit("Заполните OPENROUTER_API_KEY в .env")

    init_kb()

    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
