import os
import asyncio
from google import genai
import database
from dotenv import load_dotenv  # pip install python-dotenv

DEFAULT_MODEL = "gemini-2.5-flash"

class AiModel:
    def __init__(self):
        # Load variables from .env file
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY. Please set it in .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = DEFAULT_MODEL

    async def get_best_completions(self, text_to_complete: str, username: str) -> str:
        # DB read wrapped inside thread with fresh connection
        def db_get_history():
            conn = database.init_db()
            try:
                return database.get_history(conn, username)
            finally:
                conn.close()

        history = await asyncio.to_thread(db_get_history)

        prompt = f"""
You are an AI auto-completion engine.
You will be given two inputs:
1. A history of previously entered text or conversation:
---
{history}
---
2. A current partial input that needs completion:
---
{text_to_complete}
---

Your task:
- Generate up to 5 of the best, most likely completions for the partial input,
  considering the history for context and style.
- Completions must be concise and directly follow the partial input.
- Rank them by likelihood and naturalness (most likely first).
- Keep formatting plain text, one completion per line.
- Completions should be the whole text including the partial input entered.
"""

        # Gemini API call wrapped in thread to avoid blocking
        def gemini_call():
            return self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

        response = await asyncio.to_thread(gemini_call)
        suggested_completions = response.text.strip()

        # DB write wrapped inside thread with fresh connection
        def db_add_messages():
            conn = database.init_db()
            try:
                database.add_message(conn, username, text_to_complete, role="user")
                database.add_message(conn, username, suggested_completions, role="model")
            finally:
                conn.close()

        await asyncio.to_thread(db_add_messages)

        return suggested_completions

    async def add_user(self, username: str) -> None:
        def db_add_user():
            conn = database.init_db()
            try:
                database.add_user(conn, username)
            finally:
                conn.close()

        await asyncio.to_thread(db_add_user)
