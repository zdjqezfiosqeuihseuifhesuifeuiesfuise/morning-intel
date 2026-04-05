import asyncio
import os

import telegram

CHUNK_LIMIT = 4096


def _split_chunks(text: str, limit: int = CHUNK_LIMIT) -> list[str]:
    """
    Split text into chunks <= limit characters.
    Breaks at newlines where possible — never mid-line.
    """
    chunks = []
    current = []
    current_len = 0

    for line in text.splitlines(keepends=True):
        # Single line longer than limit — must hard-split it
        if len(line) > limit:
            if current:
                chunks.append("".join(current))
                current, current_len = [], 0
            for i in range(0, len(line), limit):
                chunks.append(line[i:i + limit])
            continue

        if current_len + len(line) > limit:
            chunks.append("".join(current))
            current, current_len = [], 0

        current.append(line)
        current_len += len(line)

    if current:
        chunks.append("".join(current))

    return chunks


async def send_message(text: str) -> None:
    token   = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    try:
        bot    = telegram.Bot(token=token)
        chunks = _split_chunks(text)

        for i, chunk in enumerate(chunks):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"[telegram] failed to send chunk {i + 1}/{len(chunks)}: {e}")

            if i < len(chunks) - 1:
                await asyncio.sleep(1)

    except Exception as e:
        print(f"[telegram] send_message error: {e}")
