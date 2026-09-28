import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os
import json
from datetime import datetime
import re

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin ID - o'zingizning Telegram ID ingizni kiriting
ADMIN_ID = 8386037110  # Jahongir's Telegram ID

# Statistika faylini yaratish
STATS_FILE = 'bot_stats.json'

def load_stats():
    """Statistikani yuklash"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'total_users': set(),
        'total_searches': 0,
        'total_downloads': 0,
        'user_activity': {},
        'start_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def save_stats(stats):
    """Statistikani saqlash"""
    # Set'ni list'ga o'tkazish (JSON uchun)
    stats_copy = stats.copy()
    stats_copy['total_users'] = list(stats['total_users'])

    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats_copy, f, ensure_ascii=False, indent=2)

def add_user_activity(user_id, username, activity_type):
    """Foydalanuvchi faoliyatini qo'shish"""
    stats = load_stats()

    # Set qayta yuklash kerak
    if isinstance(stats['total_users'], list):
        stats['total_users'] = set(stats['total_users'])

    stats['total_users'].add(user_id)

    if activity_type == 'search':
        stats['total_searches'] += 1
    elif activity_type == 'download':
        stats['total_downloads'] += 1

    # Foydalanuvchi ma'lumotlari
    user_key = str(user_id)
    if user_key not in stats['user_activity']:
        stats['user_activity'][user_key] = {
            'username': username,
            'searches': 0,
            'downloads': 0,
            'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    stats['user_activity'][user_key]['last_seen'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if activity_type == 'search':
        stats['user_activity'][user_key]['searches'] += 1
    elif activity_type == 'download':
        stats['user_activity'][user_key]['downloads'] += 1

    save_stats(stats)

def is_admin(user_id):
    """Admin tekshiruvi"""
    return user_id == ADMIN_ID

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    add_user_activity(user_id, username, 'visit')

    await update.message.reply_text(
        f"Salom! 👋\n\n"
        f"Men musiqa va video topib beradigan botman 🎵🎬\n\n"
        f"<b>Nima qila olaman:</b>\n"
        f"🎵 Qo'shiq qidirish va yuklab olish\n"
        f"🎬 YouTube video/kino yuklab olish\n"
        f"📹 Format tanlash (MP3, MP4, HD, Full HD)\n\n"
        f"<b>Foydalanish:</b>\n"
        f"• Qo'shiq/video nomini yuboring\n"
        f"• Yoki YouTube linkini yuboring\n\n"
        f"Masalan: \"Yulduz Usmonova - Aldamagin\"\n\n"
        f"🆔 Sizning ID ingiz: <code>{user_id}</code>",
        parse_mode='HTML'
    )

# /sojida13 buyrug'i
async def sojida13(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("qalesz")

# Admin buyruqlari
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uchun statistika"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return

    stats = load_stats()

    # Set'ni list'ga o'girish
    if isinstance(stats['total_users'], set):
        total_users = len(stats['total_users'])
    else:
        total_users = len(stats['total_users'])

    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"🔍 Jami qidiruvlar: {stats['total_searches']}\n"
        f"⬇️ Jami yuklab olishlar: {stats['total_downloads']}\n"
        f"📅 Bot ishga tushgan: {stats['start_date']}\n"
    )

    await update.message.reply_text(text, parse_mode='HTML')

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uchun foydalanuvchilar ro'yxati"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return

    stats = load_stats()

    if not stats['user_activity']:
        await update.message.reply_text("📭 Hali hech kim botdan foydalanmagan.")
        return

    text = "👥 <b>Foydalanuvchilar ro'yxati:</b>\n\n"

    # Foydalanuvchilarni yuklab olishlar bo'yicha saralash
    sorted_users = sorted(
        stats['user_activity'].items(),
        key=lambda x: x[1]['downloads'],
        reverse=True
    )

    for i, (uid, data) in enumerate(sorted_users[:20], 1):  # Faqat birinchi 20 ta
        username = data.get('username', 'Noma\'lum')
        searches = data.get('searches', 0)
        downloads = data.get('downloads', 0)
        last_seen = data.get('last_seen', 'Noma\'lum')

        text += (
            f"{i}. <b>@{username}</b> (ID: {uid})\n"
            f"   🔍 Qidiruvlar: {searches} | ⬇️ Yuklab olishlar: {downloads}\n"
            f"   📅 Oxirgi faollik: {last_seen}\n\n"
        )

    if len(stats['user_activity']) > 20:
        text += f"\n... va yana {len(stats['user_activity']) - 20} ta foydalanuvchi"

    await update.message.reply_text(text, parse_mode='HTML')

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin uchun xabar yuborish"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return

    if not context.args:
        await update.message.reply_text(
            "📢 <b>Xabar yuborish:</b>\n\n"
            "Foydalanish: /broadcast <xabar>\n\n"
            "Masalan: /broadcast Yangi versiya chiqdi!",
            parse_mode='HTML'
        )
        return

    message = ' '.join(context.args)
    stats = load_stats()

    if isinstance(stats['total_users'], list):
        users = stats['total_users']
    else:
        users = list(stats['total_users'])

    success = 0
    failed = 0

    status_msg = await update.message.reply_text(f"📤 Xabar yuborilmoqda... 0/{len(users)}")

    for i, uid in enumerate(users, 1):
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>Admin xabari:</b>\n\n{message}", parse_mode='HTML')
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Xabar yuborishda xatolik (ID: {uid}): {e}")

        if i % 10 == 0:
            await status_msg.edit_text(f"📤 Xabar yuborilmoqda... {i}/{len(users)}")

    await status_msg.edit_text(
        f"✅ Xabar yuborildi!\n\n"
        f"Muvaffaqiyatli: {success}\n"
        f"Xatolik: {failed}"
    )

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin buyruqlari ro'yxati"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return

    text = (
        "🔧 <b>Admin Buyruqlari:</b>\n\n"
        "/admin_stats - Bot statistikasi\n"
        "/admin_users - Foydalanuvchilar ro'yxati\n"
        "/broadcast <xabar> - Hammaga xabar yuborish\n"
        "/announce <xabar> - Hammaga ko'rinadigan e'lon\n"
        "/admin_help - Bu yordam\n"
    )

    await update.message.reply_text(text, parse_mode='HTML')

async def admin_announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin e'loni - hammaga ko'rinadigan xabar"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return

    if not context.args:
        await update.message.reply_text(
            "📢 <b>E'lon yaratish:</b>\n\n"
            "Foydalanish: /announce <xabar>\n\n"
            "Masalan: /announce Bot yangilandi! Endi video ham yuklay olasizlar!",
            parse_mode='HTML'
        )
        return

    message = ' '.join(context.args)

    # E'lon matnini yaratish
    announcement_text = (
        "📣 <b>E'LON</b> 📣\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{message}\n\n"
        "━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    stats = load_stats()

    if isinstance(stats['total_users'], list):
        users = stats['total_users']
    else:
        users = list(stats['total_users'])

    success = 0
    failed = 0

    status_msg = await update.message.reply_text(f"📣 E'lon yuborilmoqda... 0/{len(users)}")

    for i, uid in enumerate(users, 1):
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=announcement_text,
                parse_mode='HTML'
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"E'lon yuborishda xatolik (ID: {uid}): {e}")

        if i % 10 == 0:
            await status_msg.edit_text(f"📣 E'lon yuborilmoqda... {i}/{len(users)}")

    await status_msg.edit_text(
        f"✅ E'lon yuborildi!\n\n"
        f"📊 Statistika:\n"
        f"✓ Muvaffaqiyatli: {success}\n"
        f"✗ Xatolik: {failed}\n\n"
        f"📢 E'lon matni:\n{message}"
    )

# YouTube playlist'ni qayta ishlash
async def handle_youtube_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube playlist'dagi barcha qo'shiqlarni ko'rsatish"""
    url = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    status_msg = await update.message.reply_text("🔍 Playlist ma'lumotlari olinmoqda...")

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info or 'entries' not in info:
                await status_msg.edit_text("❌ Playlist topilmadi yoki bo'sh.")
                return

            playlist_title = info.get('title', 'Playlist')
            entries = info['entries'][:50]  # Maksimal 50 ta qo'shiq

            if not entries:
                await status_msg.edit_text("❌ Playlist bo'sh.")
                return

            # Playlist qo'shiqlarini ko'rsatish
            keyboard = []
            for i, entry in enumerate(entries, 1):
                if not entry:
                    continue

                title = entry.get('title', 'Noma\'lum')
                video_id = entry.get('id', '')

                if not video_id:
                    continue

                duration = entry.get('duration', 0)
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}" if duration else "?"

                button_text = f"{i}. {title[:45]}... ({duration_str})"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_{video_id}")])

            if not keyboard:
                await status_msg.edit_text("❌ Playlist'da yuklab olinadigan qo'shiqlar topilmadi.")
                return

            reply_markup = InlineKeyboardMarkup(keyboard)

            await status_msg.edit_text(
                f"🎵 <b>{playlist_title}</b>\n\n"
                f"📝 Jami: {len(keyboard)} ta qo'shiq\n\n"
                "Yuklab olish uchun tanlang:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

            add_user_activity(user_id, username, 'search')

    except Exception as e:
        logger.error(f"Playlist qayta ishlashda xatolik: {e}")
        await status_msg.edit_text(
            "❌ Playlist'ni qayta ishlab bo'lmadi.\n\n"
            "Iltimos:\n"
            "• Link to'g'ri ekanligini tekshiring\n"
            "• Playlist ochiq (public) ekanligini tekshiring"
        )

# YouTube linkni qayta ishlash va format tanlash
async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """YouTube linkidan format tanlash"""
    url = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    status_msg = await update.message.reply_text("🔍 Video ma'lumotlari olinmoqda...")

    try:
        # Video ma'lumotlarini olish
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_id = info.get('id', '')
            title = info.get('title', 'Noma\'lum')
            duration = info.get('duration', 0)

            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}" if duration else "?"

            # Format tanlash tugmalari
            keyboard = [
                [
                    InlineKeyboardButton("🎧 30s Tinglash", callback_data=f"preview_{video_id}")
                ],
                [
                    InlineKeyboardButton("🎵 M4A Audio", callback_data=f"fmt_m4a_{video_id}")
                ],
                [
                    InlineKeyboardButton("📹 360p Video", callback_data=f"fmt_360_{video_id}"),
                    InlineKeyboardButton("📹 480p Video", callback_data=f"fmt_480_{video_id}")
                ],
                [
                    InlineKeyboardButton("🎬 720p HD", callback_data=f"fmt_720_{video_id}"),
                    InlineKeyboardButton("🎬 1080p Full HD", callback_data=f"fmt_1080_{video_id}")
                ],
                [
                    InlineKeyboardButton("🎞️ Eng yuqori sifat", callback_data=f"fmt_best_{video_id}")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await status_msg.edit_text(
                f"📹 <b>{title}</b>\n\n"
                f"⏱ Davomiyligi: {duration_str}\n\n"
                "Format tanlang:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

            add_user_activity(user_id, username, 'search')

    except Exception as e:
        logger.error(f"YouTube link qayta ishlashda xatolik: {e}")
        await status_msg.edit_text(
            "❌ YouTube linkini qayta ishlab bo'lmadi.\n\n"
            "Iltimos:\n"
            "• Link to'g'ri ekanligini tekshiring\n"
            "• Video ochiq (public) ekanligini tekshiring"
        )

# Instagram linkdan musiqa topish
async def get_music_from_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instagram linkidan musiqa topish"""
    url = update.message.text
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    status_msg = await update.message.reply_text("🔍 Instagram linkidan musiqa topilmoqda...")

    try:
        # Instagram videosidan ma'lumot olish
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            track_info = None
            artist_info = None

            # Instagram'dagi title yoki description'dan musiqa nomini qidirish
            if 'title' in info and info['title']:
                title = info['title']
                # Musiqa ma'lumotlarini qidirish
                # Ko'pincha "Original audio - Artist" yoki "Song - Artist" formatida bo'ladi
                music_patterns = [
                    r'(?:Original audio|Audio|Music|Song)[:\s\-]+(.+?)(?:\s*[\|•]|$)',
                    r'🎵\s*(.+?)(?:\s*[\|•]|$)',
                    r'♫\s*(.+?)(?:\s*[\|•]|$)',
                ]

                for pattern in music_patterns:
                    match = re.search(pattern, title, re.IGNORECASE)
                    if match:
                        track_info = match.group(1).strip()
                        break

                # Agar pattern topilmasa, title'ning o'zini ishlatish
                if not track_info and len(title) > 3:
                    # Hashtag va mention'larni olib tashlash
                    cleaned = re.sub(r'[#@]\w+', '', title).strip()
                    if cleaned:
                        track_info = cleaned

            # Description'dan ham qidirish
            if not track_info and 'description' in info:
                description = info['description']
                # Description'dagi birinchi qatorni olish (ko'pincha qo'shiq nomi)
                first_line = description.split('\n')[0].strip()
                if first_line and len(first_line) > 3 and len(first_line) < 100:
                    # Hashtag va mention'larni olib tashlash
                    cleaned = re.sub(r'[#@]\w+', '', first_line).strip()
                    if cleaned:
                        track_info = cleaned

            if track_info:
                # Topilgan qo'shiqni YouTube'da qidirish
                add_user_activity(user_id, username, 'search')

                await status_msg.edit_text(f"✅ Instagram'dan topildi!\n\n🔍 YouTube'da qidiryapman: <b>{track_info}</b>", parse_mode='HTML')

                # YouTube'da qidirish
                search_opts = {
                    'format': 'bestaudio[ext=m4a]/best',
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'default_search': 'ytsearch5',
                }

                with yt_dlp.YoutubeDL(search_opts) as ydl_search:
                    search_info = ydl_search.extract_info(f"ytsearch5:{track_info}", download=False)

                    if not search_info or 'entries' not in search_info or len(search_info['entries']) == 0:
                        await status_msg.edit_text(
                            f"❌ YouTube'da topilmadi: <b>{track_info}</b>\n\n"
                            "💡 Qo'shiq nomini to'g'ridan-to'g'ri yozib qidiring.",
                            parse_mode='HTML'
                        )
                        return

                    # Natijalarni ko'rsatish
                    results = search_info['entries'][:5]
                    keyboard = []

                    for i, result in enumerate(results, 1):
                        title = result.get('title', 'Noma\'lum')
                        video_id = result.get('id', '')
                        duration = result.get('duration', 0)

                        minutes = duration // 60
                        seconds = duration % 60
                        duration_str = f"{minutes}:{seconds:02d}" if duration else "?"

                        button_text = f"{i}. {title[:50]}... ({duration_str})"
                        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"dl_{video_id}")])

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    await status_msg.edit_text(
                        f"📸 Instagram'dan: <b>{track_info}</b>\n\n"
                        "🎵 YouTube natijalaridan tanlang:",
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
            else:
                await status_msg.edit_text(
                    "❌ Bu Instagram postida musiqa ma'lumoti topilmadi.\n\n"
                    "💡 Maslahat:\n"
                    "1. Qo'shiq nomini caption yoki description'da ko'rsating\n"
                    "2. Yoki qo'shiq nomini to'g'ridan-to'g'ri yozib qidiring"
                )

    except Exception as e:
        logger.error(f"Instagram linkdan musiqa topishda xatolik: {e}")
        await status_msg.edit_text(
            "❌ Instagram linkini qayta ishlab bo'lmadi.\n\n"
            "Mumkin bo'lgan sabablar:\n"
            "• Link noto'g'ri yoki post o'chirilgan\n"
            "• Instagram private akkaunt\n"
            "• Instagram API muammosi\n\n"
            "💡 Yechim: Qo'shiq nomini to'g'ridan-to'g'ri yozib qidiring"
        )

# Qo'shiq qidirish va natijalarni ko'rsatish
async def search_and_send_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Instagram linkni tekshirish
    instagram_pattern = r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/(p|reel|reels|tv)/[A-Za-z0-9_-]+'
    if re.match(instagram_pattern, query):
        await get_music_from_instagram(update, context)
        return

    # YouTube linkni tekshirish
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    if re.match(youtube_pattern, query):
        # Playlist yoki oddiy video ekanligini tekshirish
        if 'list=' in query or 'playlist' in query:
            await handle_youtube_playlist(update, context)
        else:
            await handle_youtube_link(update, context)
        return

    # Statistikaga qo'shish
    add_user_activity(user_id, username, 'search')

    # Foydalanuvchiga kutish xabarini yuborish
    status_msg = await update.message.reply_text("🔍 Qidiryapman...")

    try:
        # YouTube'dan 5 ta natija qidirish
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Faqat ma'lumotlarni olish, yuklab olmaslik
            'default_search': 'ytsearch5',  # 5 ta natija
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)

            if not info or 'entries' not in info or len(info['entries']) == 0:
                await status_msg.edit_text("❌ Hech narsa topilmadi. Boshqa nom bilan urinib ko'ring.")
                return

            # Natijalarni saqlash
            results = info['entries'][:5]

            # Inline tugmalarni yaratish
            keyboard = []
            for i, result in enumerate(results, 1):
                if not result:
                    continue

                title = result.get('title', 'Noma\'lum')
                video_id = result.get('id', '')

                if not video_id:
                    continue

                duration = result.get('duration', 0)

                # Davomiylikni formatlash
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}" if duration else "?"

                button_text = f"{i}. {title[:50]}... ({duration_str})"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_{video_id}")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await status_msg.edit_text(
                f"🎵 <b>'{query}'</b> uchun topilgan natijalar:\n\n"
                "Yuklab olish uchun tanlang:",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await status_msg.edit_text(
            "❌ Kechirasiz, qo'shiqni topa olmadim.\n\n"
            "Iltimos, boshqa nom bilan urinib ko'ring."
        )

# Callback handlerlar
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha callback'larni boshqarish"""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Preview (30 soniyalik namuna)
    if data.startswith("preview_"):
        video_id = data.replace("preview_", "")

        try:
            await query.edit_message_text("🎧 30 soniyalik namuna tayyorlanmoqda...")

            # 30 soniyalik audio kesishni yuklab olish
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'outtmpl': f'downloads/{chat_id}_preview.%(ext)s',
                'postprocessor_args': [
                    '-ss', '30',  # 30-soniyadan boshla
                    '-t', '30',   # 30 soniya davom etsin
                ],
            }

            os.makedirs('downloads', exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                title = info.get('title', 'Noma\'lum')
                file_path = ydl.prepare_filename(info)

            # Audio yuborish
            await query.edit_message_text("📤 Namuna yuborilmoqda...")

            with open(file_path, 'rb') as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    title=f"{title} (Preview)",
                    caption=f"🎧 <b>{title}</b>\n\n⏱ 30 soniyalik namuna\n\n💡 To'liq yuklab olish uchun formatni tanlang",
                    parse_mode='HTML'
                )

            # Faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)

            # Format tanlash tugmalarini qayta ko'rsatish
            keyboard = [
                [
                    InlineKeyboardButton("🎵 M4A Audio", callback_data=f"fmt_m4a_{video_id}")
                ],
                [
                    InlineKeyboardButton("📹 360p Video", callback_data=f"fmt_360_{video_id}"),
                    InlineKeyboardButton("📹 480p Video", callback_data=f"fmt_480_{video_id}")
                ],
                [
                    InlineKeyboardButton("🎬 720p HD", callback_data=f"fmt_720_{video_id}"),
                    InlineKeyboardButton("🎬 1080p Full HD", callback_data=f"fmt_1080_{video_id}")
                ],
                [
                    InlineKeyboardButton("🎞️ Eng yuqori sifat", callback_data=f"fmt_best_{video_id}")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ Namuna yuborildi!\n\n"
                "To'liq yuklab olish uchun formatni tanlang:",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Preview xatolik: {e}")
            await query.edit_message_text(
                "❌ Namuna tayyorlashda xatolik.\n\n"
                "To'g'ridan-to'g'ri formatni tanlang."
            )
        return

    # Video tanlash (format tanlash ekranini ko'rsatish)
    if data.startswith("select_"):
        video_id = data.replace("select_", "")

        # Format tanlash tugmalari
        keyboard = [
            [
                InlineKeyboardButton("🎧 30s Tinglash", callback_data=f"preview_{video_id}")
            ],
            [
                InlineKeyboardButton("🎵 M4A Audio", callback_data=f"fmt_m4a_{video_id}")
            ],
            [
                InlineKeyboardButton("📹 360p Video", callback_data=f"fmt_360_{video_id}"),
                InlineKeyboardButton("📹 480p Video", callback_data=f"fmt_480_{video_id}")
            ],
            [
                InlineKeyboardButton("🎬 720p HD", callback_data=f"fmt_720_{video_id}"),
                InlineKeyboardButton("🎬 1080p Full HD", callback_data=f"fmt_1080_{video_id}")
            ],
            [
                InlineKeyboardButton("🎞️ Eng yuqori sifat", callback_data=f"fmt_best_{video_id}")
            ],
            [
                InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_search")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "📥 Format tanlang:\n\n"
            "🎵 <b>Audio</b> - faqat musiqa (M4A format)\n"
            "📹 <b>Video</b> - past sifat, kichik hajm\n"
            "🎬 <b>HD</b> - yuqori sifat\n"
            "🎞️ <b>Eng yuqori</b> - mavjud eng yaxshi sifat",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # Format tanlangan, yuklab olish
    if data.startswith("fmt_"):
        parts = data.split("_")
        format_type = parts[1]
        video_id = parts[2]

        try:
            await query.edit_message_text("⏬ Yuklab olyapman...")

            # Format sozlamalari
            format_options = {
                'mp3': {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                'm4a': {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                '360': {
                    'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                '480': {
                    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                '720': {
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                '1080': {
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                },
                'best': {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
                }
            }

            ydl_opts = format_options.get(format_type, format_options['m4a'])
            ydl_opts['quiet'] = True
            ydl_opts['no_warnings'] = True

            # downloads papkasini yaratish
            os.makedirs('downloads', exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                title = info.get('title', 'Noma\'lum')

                # Yuklab olingan fayl nomini topish
                file_path = ydl.prepare_filename(info)

                # MP3 uchun fayl nomini to'g'rilash
                if format_type == 'mp3':
                    # Fayl .mp3 ga o'zgartirilganini tekshirish
                    base_path = file_path.rsplit('.', 1)[0]
                    file_path = f"{base_path}.mp3"

            # Fayl yuborish
            await query.edit_message_text("📤 Yuboryapman...")

            if format_type in ['mp3', 'm4a']:
                # Audio yuborish
                with open(file_path, 'rb') as audio:
                    await context.bot.send_audio(
                        chat_id=chat_id,
                        audio=audio,
                        title=title,
                        caption=f"🎵 {title}\n\n📁 Format: {format_type.upper()}"
                    )
            else:
                # Video yuborish
                with open(file_path, 'rb') as video:
                    # Fayl hajmini tekshirish (Telegram limiti: 50MB)
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:  # 50MB
                        await query.edit_message_text(
                            f"❌ Fayl hajmi juda katta ({file_size / (1024*1024):.1f} MB)\n\n"
                            "Telegram limiti: 50 MB\n\n"
                            "💡 Maslahat: Past sifatli formatni tanlang"
                        )
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        return

                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=video,
                        caption=f"🎬 {title}\n\n📁 Sifat: {format_type.upper()}"
                    )

            # Faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)

            await query.delete_message()
            add_user_activity(user_id, username, 'download')

        except Exception as e:
            logger.error(f"Yuklab olishda xatolik: {e}")
            await query.edit_message_text(
                "❌ Yuklab olishda xatolik yuz berdi.\n\n"
                "Mumkin bo'lgan sabablar:\n"
                "• Fayl hajmi juda katta (>50MB)\n"
                "• Formatni qayta ishlashda xatolik\n"
                "• Internet aloqasi muammosi\n\n"
                "💡 Boshqa formatni sinab ko'ring"
            )

# Eski download_and_send funksiyasini olib tashlaymiz va yuqoridagi handle_callback ishlatamiz

# Xatoliklarni qayta ishlash
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xatolik: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

def main():
    # Bot tokenini bu yerga qo'ying
    TOKEN = "8987460619:AAG2ZFIYFMLCkjn-03gUZvrcNvaxkghA3D0"

    if TOKEN == "SIZNING_TOKEN_INGIZ":
        print("❌ XATO: Iltimos, TOKEN o'rniga haqiqiy bot tokeningizni kiriting!")
        print("music_bot.py faylidagi TOKEN qatorini tahrirlang.")
        return

    # Bot yaratish
    application = Application.builder().token(TOKEN).build()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sojida13", sojida13))
    application.add_handler(CommandHandler("admin_stats", admin_stats))
    application.add_handler(CommandHandler("admin_users", admin_users))
    application.add_handler(CommandHandler("admin_help", admin_help))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    application.add_handler(CommandHandler("announce", admin_announce))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_and_send_music))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(error_handler)

    # Botni ishga tushirish
    print("✅ Bot ishga tushdi! Ctrl+C bilan to'xtatish mumkin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
