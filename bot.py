"""
Gemini Telegram Bot (modernized).

A Telegram bot powered by Google's Gemini model:
- /start            -> greeting
- text messages     -> Gemini chat reply
- photo messages    -> Gemini vision description (uses the photo caption as the prompt, if any)

Configuration is done entirely through environment variables:
    GOOGLE_API_KEY       - Google AI Studio / Gemini API key
    TELEGRAM_BOT_TOKEN   - Telegram bot token from @BotFather

Extended from the open-source project zhuchangyi/Gemini2tg (MIT).
Modernized: python-telegram-bot v13 -> v20+ async API, dead
`google.generativeai` SDK -> `google-genai` SDK, models updated to gemini-2.5-flash.
"""

import io
import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from google import genai
from google.genai import types

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MODEL_ID = "gemini-2.5-flash"
DEFAULT_VISION_PROMPT = "What's in this picture? Describe it in detail."


def get_client() -> genai.Client:
    """Build a Gemini client from the GOOGLE_API_KEY environment variable."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    await update.message.reply_text(
        "Hello! I am a Gemini-powered chatbot.\n"
        "Send me a text message to chat, or send a photo and I will describe it."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages: send them to Gemini and reply with the answer."""
    user_message = update.message.text
    # NOTE: keep the client in a local variable for the whole call.
    # google-genai closes the underlying HTTP client when the Client object
    # is garbage-collected, so chaining get_client().models... breaks.
    client = get_client()
    try:
        response = client.models.generate_content(
            model=MODEL_ID, contents=user_message
        )
        reply = response.text or "Sorry, I couldn't generate a reply."
    except Exception as e:  # noqa: BLE001 - surface a friendly message to the user
        logger.error("Error calling Gemini for text message: %s", e)
        reply = "An error occurred while processing your message. Please try again."
    await update.message.reply_text(reply)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming photo messages: send the image to Gemini's vision and reply."""
    photo = update.message.photo[-1]
    prompt = update.message.caption or DEFAULT_VISION_PROMPT
    # NOTE: keep the client referenced for the whole call (see handle_message).
    client = get_client()
    try:
        tg_file = await context.bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await tg_file.download_to_memory(buf)
        buf.seek(0)
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                prompt,
                types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"),
            ],
        )
        reply = response.text or "Sorry, I couldn't process the image."
    except Exception as e:  # noqa: BLE001 - surface a friendly message to the user
        logger.error("Error calling Gemini for photo message: %s", e)
        reply = "An error occurred while processing the image. Please try again."
    await update.message.reply_text(reply)


def build_application(token: str) -> Application:
    """Create the Telegram application and register all handlers."""
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set.")
    app = build_application(token)
    logger.info("Bot started. Listening for updates...")
    app.run_polling()


if __name__ == "__main__":
    main()
