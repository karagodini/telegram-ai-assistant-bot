from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from . import config, db, openrouter
from .rag import KnowledgeBase

router = Router()
kb: KnowledgeBase | None = None


def init_kb() -> None:
    global kb
    kb = KnowledgeBase()
    if kb.col.count() == 0:
        kb.rebuild()


def _source_note(sources: list[str]) -> str:
    return "\n\n📚 Источники: " + ", ".join(sources) if sources else ""


@router.message(Command("start"))
async def cmd_start(m: Message) -> None:
    db.register_user(m.from_user.id, m.from_user.username or "")
    await m.answer(
        "👋 Привет! Я AI-ассистент.\n\n"
        "• Просто напишите сообщение — поболтаем\n"
        "• /ask <вопрос> — отвечу по документам с источником\n"
        "• /clear — забыть историю диалога"
    )


@router.message(Command("clear"))
async def cmd_clear(m: Message) -> None:
    db.clear_history(m.from_user.id)
    await m.answer("🧹 История диалога очищена.")


@router.message(Command("ask"))
async def cmd_ask(m: Message) -> None:
    question = (m.text or "").removeprefix("/ask").strip()
    if not question:
        await m.answer("Напишите вопрос после команды: /ask как записаться?")
        return
    if not db.check_rate_limit(m.from_user.id):
        await m.answer("⏳ Лимит запросов на сегодня исчерпан, попробуйте завтра.")
        return
    await m.bot.send_chat_action(m.chat.id, "typing")
    context, sources = kb.ask(question)
    if not context:
        await m.answer("📭 База знаний пуста. Положите файлы в папку data/ и выполните /rebuild.")
        return
    messages = [
        {
            "role": "system",
            "content": (
                "Ответь на вопрос, используя ТОЛЬКО контекст ниже. "
                "Если ответа нет в контексте — честно скажи об этом. "
                "В конце укажи номера фрагментов, на которые опирался.\n\n" + context
            ),
        },
        {"role": "user", "content": question},
    ]
    try:
        answer = await openrouter.chat(messages, config.MODEL, config.OPENROUTER_API_KEY)
        await m.answer(answer + _source_note(sources))
    except Exception as e:
        await m.answer(f"⚠️ Ошибка: {e}")


@router.message(Command("rebuild"))
async def cmd_rebuild(m: Message) -> None:
    await m.bot.send_chat_action(m.chat.id, "typing")
    total = kb.rebuild()
    await m.answer(f"✅ База знаний обновлена: {total} фрагментов.")


@router.message(Command("stats"))
async def cmd_stats(m: Message) -> None:
    if config.ADMIN_ID and m.from_user.id != config.ADMIN_ID:
        return
    s = db.stats()
    await m.answer(f"📊 Пользователей: {s['users']}\nСообщений за 24ч: {s['messages_24h']}")


@router.message(F.text)
async def free_chat(m: Message) -> None:
    db.register_user(m.from_user.id, m.from_user.username or "")
    if not db.check_rate_limit(m.from_user.id):
        await m.answer("⏳ Лимит запросов на сегодня исчерпан, попробуйте завтра.")
        return
    await m.bot.send_chat_action(m.chat.id, "typing")
    db.add_message(m.from_user.id, "user", m.text)
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    messages += db.get_history(m.from_user.id)
    try:
        answer = await openrouter.chat(messages, config.MODEL, config.OPENROUTER_API_KEY)
        db.add_message(m.from_user.id, "assistant", answer)
        await m.answer(answer)
    except Exception as e:
        await m.answer(f"⚠️ Ошибка: {e}")
