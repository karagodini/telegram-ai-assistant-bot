# 🤖 Telegram AI Assistant Bot

**RU:** Готовый Telegram-бот с AI-консультантом, который отвечает клиентам **с опорой на ваши документы** (PDF, TXT, MD). Клонируйте → вставьте токен → получите бота за 5 минут.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.x-26A5E4)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

> 📹 **Демо:** вставьте сюда `demo.gif` (запись экрана: вопрос → ответ с цитатой)

## ✨ Возможности

- 💬 **Свободный диалог** с контекстом (помнит историю, сброс через `/clear`)
- 📚 **RAG по вашим документам** — команда `/ask`, ответ **с указанием источника**
- 🧠 **Локальные эмбеддинги** (fastembed) — работает без платных API для поиска
- 🔑 **OpenRouter-совместимость** — подходит любой ключ и любая openai-совместимая модель
- 🛡️ **Антиспам**: лимит запросов в день на пользователя
- 📊 **Статистика** для админа: пользователи, сообщения, /rebuild базы
- 🐳 **Docker / docker-compose** — деплой одной командой

## 🚀 Быстрый старт (Docker)

```bash
git clone https://github.com/karagodini/telegram-ai-assistant-bot.git
cd telegram-ai-assistant-bot
cp .env.example .env   # вставьте BOT_TOKEN и OPENROUTER_API_KEY
# положите свои PDF/TXT в папку data/
docker compose up -d
```

Бот готов. Команда `/rebuild` переиндексирует документы (или перезапустите контейнер).

## 💻 Локальный запуск

```bash
pip install -r requirements.txt
cp .env.example .env   # заполните
python -m app.main
```

## ⚙️ Настройка (.env)

| Переменная | Описание | По умолчанию |
|---|---|---|
| `BOT_TOKEN` | Токен от @BotFather | — |
| `OPENROUTER_API_KEY` | Ключ с openrouter.ai | — |
| `MODEL` | Модель в формате OpenRouter | `openrouter/free` |
| `SYSTEM_PROMPT` | Роль бота | ассистент компании |
| `ADMIN_ID` | Ваш Telegram ID (для `/stats`) | — |
| `MAX_REQUESTS_PER_DAY` | Лимит запросов/пользователь/день | `30` |
| `CHUNK_SIZE` | Размер фрагмента документа | `500` |

## 📱 Команды бота

| Команда | Кому | Что делает |
|---|---|---|
| `/start` | всем | Приветствие и инструкция |
| свободное сообщение | всем | Диалог с AI |
| `/ask <вопрос>` | всем | Ответ **по вашим документам** с источником |
| `/clear` | всем | Сбросить историю диалога |
| `/rebuild` | всем | Переиндексировать документы |
| `/stats` | админу | Пользователи и сообщения за сутки |

## 🏗 Архитектура

```
пользователь → aiogram → handlers ──free chat──→ OpenRouter API
                     └─/ask──→ RAG: Chroma (эмбеддинги fastembed)
                                    ↑ индекс из ./data (PDF/TXT/MD)
```

- `app/main.py` — точка входа, запуск поллинга
- `app/handlers.py` — команды и логика диалога
- `app/rag.py` — чанкинг, индексация, поиск фрагментов
- `app/db.py` — SQLite: пользователи, история, лимиты
- `app/openrouter.py` — клиент LLM API

## 🛣 Roadmap

- [ ] Веб-админка со статистикой диалогов
- [ ] Поддержка Google Docs как источника
- [ ] Кнопки быстрых вопросов (FAQ-режим)
- [ ] Whisper: голосовые вопросы

## 📄 Лицензия

MIT — используйте в своих проектах и для клиентов свободно.

---

⭐ Если проект пригодился — поставьте звезду, это помогает развитию.
