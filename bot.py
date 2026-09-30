
import logging
import os
 
import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
 
from config import FIRST_RUN_DELAY_SECONDS, POLL_INTERVAL_SECONDS, RSS_FEEDS
 
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
 
TR_MAP = str.maketrans("İIŞŞĞÜÖÇ", "iışşğüöç")
 
CHAT_KEYWORDS: dict[int, set[str]] = {}
SENT_LINKS: dict[int, set[str]] = {}
 
 
def normalize(text: str) -> str:
    """Türkçe karakterleri tutarlı küçük harfe çevirir (İ/I -> i, vs.)."""
    return text.translate(TR_MAP).lower()
 
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    CHAT_KEYWORDS.setdefault(chat_id, set())
    SENT_LINKS.setdefault(chat_id, set())
    await update.message.reply_text(
        "Merhaba! Haber botu aktif.\n\n"
        "/ekle <kelime> - takibe kelime ekle\n"
        "/sil <kelime> - kelimeyi çıkar\n"
        "/liste - takip ettiğin kelimeler\n\n"
        f"Kaynaklar her {POLL_INTERVAL_SECONDS // 60} dakikada bir taranır.\n"
        "Not: kelimeler bellekte tutuluyor, bot yeniden başlarsa sıfırlanır."
    )
 
 
async def ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /ekle deprem")
        return
    keyword = " ".join(context.args).strip().lower()
    chat_id = update.effective_chat.id
    keywords = CHAT_KEYWORDS.setdefault(chat_id, set())
    SENT_LINKS.setdefault(chat_id, set())
    if keyword in keywords:
        await update.message.reply_text(f'"{keyword}" zaten listende.')
    else:
        keywords.add(keyword)
        await update.message.reply_text(f'"{keyword}" eklendi.')
 
 
async def sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: /sil deprem")
        return
    keyword = " ".join(context.args).strip().lower()
    chat_id = update.effective_chat.id
    keywords = CHAT_KEYWORDS.get(chat_id, set())
    if keyword in keywords:
        keywords.discard(keyword)
        await update.message.reply_text(f'"{keyword}" silindi.')
    else:
        await update.message.reply_text(f'"{keyword}" listende bulunamadı.')
 
 
async def liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = sorted(CHAT_KEYWORDS.get(update.effective_chat.id, set()))
    if not keywords:
        await update.message.reply_text("Henüz kelime eklemedin. /ekle <kelime> ile başla.")
        return
    await update.message.reply_text("Takip ettiğin kelimeler:\n" + "\n".join(f"• {k}" for k in keywords))
 
 
 
TELEGRAM_MAX_LEN = 3500
 
def _format_entry(source_name: str, title: str, link: str, matched: list[str]) -> str:
    return f"📰 [{source_name}] {title}\n🔑 {', '.join(matched)}\n{link}"
 
 
def _build_bundle_messages(items: list[tuple]) -> list[str]:
    header = f"🗞️ {len(items)} yeni haber eşleşmesi\n\n"
    messages = []
    current = header
    for item in items:
        block = _format_entry(*item) + "\n\n"
        if len(current) + len(block) > TELEGRAM_MAX_LEN and current != header:
            messages.append(current.rstrip())
            current = ""
        current += block
    if current.strip():
        messages.append(current.rstrip())
    return messages
 
 
async def check_feeds(context: ContextTypes.DEFAULT_TYPE):
    if not CHAT_KEYWORDS:
        return
 
    chat_matches: dict[int, list[tuple]] = {}
 
    for source_name, feed_url in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            logger.warning("Feed okunamadı (%s): %s", source_name, e)
            continue
 
        if parsed.bozo and not parsed.entries:
            logger.warning("Feed boş/bozuk (%s): %s", source_name, feed_url)
            continue
 
        for entry in parsed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            if not link:
                continue
 
            haystack = normalize(f"{title} {summary}")
 
            for chat_id, keywords in CHAT_KEYWORDS.items():
                sent = SENT_LINKS.setdefault(chat_id, set())
                if link in sent:
                    continue
                matched = [kw for kw in keywords if normalize(kw) in haystack]
                if not matched:
                    continue
 
                chat_matches.setdefault(chat_id, []).append((source_name, title, link, matched))
                sent.add(link)
 
    for chat_id, items in chat_matches.items():
        for text in _build_bundle_messages(items):
            try:
                await context.bot.send_message(chat_id=chat_id, text=text)
            except Exception as e:
                logger.warning("Mesaj gönderilemedi (chat %s): %s", chat_id, e)
 
 
def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN ortam değişkeni tanımlı değil.")
 
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ekle", ekle))
    app.add_handler(CommandHandler("sil", sil))
    app.add_handler(CommandHandler("liste", liste))
 
    app.job_queue.run_repeating(
        check_feeds, interval=POLL_INTERVAL_SECONDS, first=FIRST_RUN_DELAY_SECONDS
    )
 
    logger.info("Bot başlatıldı.")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
 
