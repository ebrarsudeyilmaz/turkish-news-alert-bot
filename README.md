# turkish-news-alert-bot
A simple Telegram bot that periodically checks Turkish news RSS feeds and send alerts for articles matching keywords you choose.

## Features

- Tracks multiple Turkish news sources at the same time
- Each user can manage their own keyword list
- New matches are bundled into a single message instead of spamming one message per article
- No database — all data is stored in memory while the bot is running

## Commands

| Command | Description |
|---|---|
| `/start` | Activates the bot in this chat |
| `/ekle <keyword>` | Adds a keyword to your tracking list |
| `/sil <keyword>` | Removes a keyword from your tracking list |
| `/liste` | Shows your current keyword list |

## How to get a Telegram bot token

1. Open Telegram and search for **@BotFather**.
2. Send the command `/newbot`.
3. Choose a display name for your bot (can be anything, e.g. "My News Bot").
4. Choose a username for your bot (must end with `bot`, e.g. `my_news_alert_bot`).
5. BotFather will reply with a token that looks like `123456789:ABCdefGhIJKlmNoPQRstuVwxyZ`. Copy it — you will need it in the next step.
