# Gemini Telegram Bot

A Telegram chatbot powered by Google's Gemini (`gemini-2.5-flash`):

- `/start` — greeting
- **Text messages** — answered by Gemini
- **Photo messages** — described by Gemini's vision (uses your caption as the prompt, if you add one)

Extended from the open-source project [zhuchangyi/Gemini2tg](https://github.com/zhuchangyi/Gemini2tg) (MIT), modernized and maintained by [Muhammad Huzaifa Aqeel](https://github.com/HuzaifaAqeel).

## What changed from the original

- Migrated `python-telegram-bot` **v13 → v22** async API (`Updater`/`Filters`/`CallbackContext` → `Application`/`filters`/`ContextTypes`)
- Replaced the retired `google.generativeai` SDK (`gemini-pro`, `gemini-pro-vision` — both dead) with the current `google-genai` SDK
- Single model `gemini-2.5-flash` handles both text and vision
- Configuration via environment variables — no `config.json` with secrets:
  - `GOOGLE_API_KEY` — from [Google AI Studio](https://aistudio.google.com/)
  - `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather) on Telegram
- Photos are processed in memory (no leftover files on disk)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your keys (never commit .env)
export $(cat .env | xargs)   # or use your preferred env loader
python bot.py
```

Then open your bot in Telegram and send `/start`.

## How it works

```
You (Telegram) ──text/photo──▶ bot.py ──▶ Gemini 2.5 Flash ──reply──▶ You
```

Text goes straight to the model; photos are downloaded via the Telegram Bot API and sent to Gemini together with your caption (or a default "describe this image" prompt).

## License

MIT — see [LICENSE](LICENSE). Original project copyright its respective authors.
