#!/usr/bin/env python3
"""
EVZAP Telegram Bot - To'liq funksional bot
Mahsulotlar katalogi, savat, ko'p tilli interfeys
"""

import logging
import json
import os
import threading
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
from flask import Flask
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand,
    BotCommandScopeDefault, BotCommandScopeChat
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ============================================================
# SOZLAMALAR
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@evzap_channel")  # Kanal username

def _parse_admin_ids_from_env():
    ids = set()
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    if admin_ids_str.strip():
        for part in admin_ids_str.split(","):
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
    legacy_admin = os.getenv("ADMIN_ID", "").strip()
    if legacy_admin.isdigit():
        ids.add(int(legacy_admin))
    if not ids:
        ids.add(123456789)
    return ids

ENV_ADMIN_IDS = _parse_admin_ids_from_env()
PRIMARY_ADMIN_ID = min(ENV_ADMIN_IDS)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("evzap_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# TILLAR
# ============================================================
LANGUAGES = {
    "uz": {
        "welcome": "🌟 EVZAP'ga xush kelibsiz!\n\nBiz siz uchun eng yaxshi mahsulotlarni taklif etamiz.",
        "menu": "📋 Asosiy menyu",
        "catalog": "🛍 Katalog",
        "cart": "🛒 Savatcha",
        "orders": "📦 Buyurtmalarim",
        "about": "ℹ️ Biz haqimizda",
        "contact": "📞 Aloqa",
        "language": "🌐 Til",
        "back": "◀️ Orqaga",
        "add_to_cart": "🛒 Savatga qo'shish",
        "remove_from_cart": "❌ Savatdan olib tashlash",
        "checkout": "💳 Buyurtma berish",
        "clear_cart": "🗑 Savatni tozalash",
        "cart_empty": "🛒 Savatchingiz bo'sh",
        "order_placed": "✅ Buyurtmangiz qabul qilindi!\n\nBizning menejer tez orada siz bilan bog'lanadi.",
        "total": "💰 Jami",
        "quantity": "Miqdor",
        "price": "Narx",
        "categories": "📂 Kategoriyalar",
        "search": "🔍 Qidirish",
        "profile": "👤 Profil",
        "settings": "⚙️ Sozlamalar",
        "choose_lang": "🌐 Tilni tanlang:",
        "lang_changed": "✅ Til o'zgartirildi!",
        "enter_phone": "📞 Telefon raqamingizni yuboring:",
        "phone_saved": "✅ Telefon raqami saqlandi!",
        "enter_name": "👤 Ismingizni kiriting:",
        "name_saved": "✅ Ism saqlandi!",
        "about_text": "🏢 EVZAP - Sizning ishonchli do'koningiz!\n\n✨ Biz sifatli mahsulotlarni qulay narxlarda taklif etamiz.\n\n📍 Manzil: Toshkent, O'zbekiston\n📞 Tel: +998 90 123 45 67\n📧 Email: info@evzap.uz",
        "contact_text": "📞 Biz bilan bog'laning:\n\n📱 Telegram: @evzap_support\n📞 Tel: +998 90 123 45 67\n📧 Email: info@evzap.uz\n\n⏰ Ish vaqti: 9:00 - 22:00",
        "no_orders": "📦 Hali buyurtmalaringiz yo'q",
        "order_id": "Buyurtma #",
        "order_status": "Holat",
        "pending": "⏳ Kutilmoqda",
        "processing": "🔄 Qayta ishlanmoqda",
        "shipped": "🚚 Yo'lda",
        "delivered": "✅ Yetkazib berildi",
        "cancelled": "❌ Bekor qilindi",
        "write_comment": "💬 Izoh yozing (ixtiyoriy):",
        "skip": "⏭ O'tkazib yuborish",
        "confirm_order": "✅ Tasdiqlash",
        "cancel": "❌ Bekor qilish",
        "order_confirmation": "📋 Buyurtmani tasdiqlang:\n\n",
        "comment": "💬 Izoh",
        "no_comment": "Izoh yo'q",
        "pieces": "dona",
        "subscribe_required": "⚠️ Botdan foydalanish uchun kanalimizga obuna bo'ling:\n\n",
        "subscribe_btn": "📢 Kanalga obuna bo'lish",
        "check_subscribe": "✅ Obunani tekshirish",
        "not_subscribed": "❌ Siz hali kanalga obuna bo'lmagansiz. Iltimos, avval obuna bo'ling.",
        "subscribed": "✅ Rahmat! Obuna tasdiqlandi.",
        "share_contact": "📱 Kontaktni ulashish",
    },
    "ru": {
        "welcome": "🌟 Добро пожаловать в EVZAP!\n\nМы предлагаем вам лучшие товары.",
        "menu": "📋 Главное меню",
        "catalog": "🛍 Каталог",
        "cart": "🛒 Корзина",
        "orders": "📦 Мои заказы",
        "about": "ℹ️ О нас",
        "contact": "📞 Контакты",
        "language": "🌐 Язык",
        "back": "◀️ Назад",
        "add_to_cart": "🛒 В корзину",
        "remove_from_cart": "❌ Убрать из корзины",
        "checkout": "💳 Оформить заказ",
        "clear_cart": "🗑 Очистить корзину",
        "cart_empty": "🛒 Ваша корзина пуста",
        "order_placed": "✅ Ваш заказ принят!\n\nНаш менеджер скоро свяжется с вами.",
        "total": "💰 Итого",
        "quantity": "Количество",
        "price": "Цена",
        "categories": "📂 Категории",
        "search": "🔍 Поиск",
        "profile": "👤 Профиль",
        "settings": "⚙️ Настройки",
        "choose_lang": "🌐 Выберите язык:",
        "lang_changed": "✅ Язык изменён!",
        "enter_phone": "📞 Отправьте ваш номер телефона:",
        "phone_saved": "✅ Номер телефона сохранён!",
        "enter_name": "👤 Введите ваше имя:",
        "name_saved": "✅ Имя сохранено!",
        "about_text": "🏢 EVZAP - Ваш надёжный магазин!\n\n✨ Мы предлагаем качественные товары по доступным ценам.\n\n📍 Адрес: Ташкент, Узбекистан\n📞 Тел: +998 90 123 45 67\n📧 Email: info@evzap.uz",
        "contact_text": "📞 Свяжитесь с нами:\n\n📱 Telegram: @evzap_support\n📞 Тел: +998 90 123 45 67\n📧 Email: info@evzap.uz\n\n⏰ Время работы: 9:00 - 22:00",
        "no_orders": "📦 У вас пока нет заказов",
        "order_id": "Заказ #",
        "order_status": "Статус",
        "pending": "⏳ Ожидает",
        "processing": "🔄 В обработке",
        "shipped": "🚚 В пути",
        "delivered": "✅ Доставлен",
        "cancelled": "❌ Отменён",
        "write_comment": "💬 Напишите комментарий (необязательно):",
        "skip": "⏭ Пропустить",
        "confirm_order": "✅ Подтвердить",
        "cancel": "❌ Отменить",
        "order_confirmation": "📋 Подтвердите заказ:\n\n",
        "comment": "💬 Комментарий",
        "no_comment": "Нет комментария",
        "pieces": "шт",
        "subscribe_required": "⚠️ Для использования бота подпишитесь на наш канал:\n\n",
        "subscribe_btn": "📢 Подписаться на канал",
        "check_subscribe": "✅ Проверить подписку",
        "not_subscribed": "❌ Вы ещё не подписаны на канал. Пожалуйста, подпишитесь.",
        "subscribed": "✅ Спасибо! Подписка подтверждена.",
        "share_contact": "📱 Поделиться контактом",
    },
    "en": {
        "welcome": "🌟 Welcome to EVZAP!\n\nWe offer you the best products.",
        "menu": "📋 Main Menu",
        "catalog": "🛍 Catalog",
        "cart": "🛒 Cart",
        "orders": "📦 My Orders",
        "about": "ℹ️ About Us",
        "contact": "📞 Contact",
        "language": "🌐 Language",
        "back": "◀️ Back",
        "add_to_cart": "🛒 Add to Cart",
        "remove_from_cart": "❌ Remove from Cart",
        "checkout": "💳 Checkout",
        "clear_cart": "🗑 Clear Cart",
        "cart_empty": "🛒 Your cart is empty",
        "order_placed": "✅ Your order has been placed!\n\nOur manager will contact you shortly.",
        "total": "💰 Total",
        "quantity": "Quantity",
        "price": "Price",
        "categories": "📂 Categories",
        "search": "🔍 Search",
        "profile": "👤 Profile",
        "settings": "⚙️ Settings",
        "choose_lang": "🌐 Choose language:",
        "lang_changed": "✅ Language changed!",
        "enter_phone": "📞 Share your phone number:",
        "phone_saved": "✅ Phone number saved!",
        "enter_name": "👤 Enter your name:",
        "name_saved": "✅ Name saved!",
        "about_text": "🏢 EVZAP - Your trusted store!\n\n✨ We offer quality products at affordable prices.\n\n📍 Address: Tashkent, Uzbekistan\n📞 Tel: +998 90 123 45 67\n📧 Email: info@evzap.uz",
        "contact_text": "📞 Contact us:\n\n📱 Telegram: @evzap_support\n📞 Tel: +998 90 123 45 67\n📧 Email: info@evzap.uz\n\n⏰ Working hours: 9:00 - 22:00",
        "no_orders": "📦 You have no orders yet",
        "order_id": "Order #",
        "order_status": "Status",
        "pending": "⏳ Pending",
        "processing": "🔄 Processing",
        "shipped": "🚚 Shipped",
        "delivered": "✅ Delivered",
        "cancelled": "❌ Cancelled",
        "write_comment": "💬 Write a comment (optional):",
        "skip": "⏭ Skip",
        "confirm_order": "✅ Confirm",
        "cancel": "❌ Cancel",
        "order_confirmation": "📋 Confirm your order:\n\n",
        "comment": "💬 Comment",
        "no_comment": "No comment",
        "pieces": "pcs",
        "subscribe_required": "⚠️ To use the bot, please subscribe to our channel:\n\n",
        "subscribe_btn": "📢 Subscribe to Channel",
        "check_subscribe": "✅ Check Subscription",
        "not_subscribed": "❌ You are not subscribed to the channel yet. Please subscribe first.",
        "subscribed": "✅ Thank you! Subscription confirmed.",
        "share_contact": "📱 Share Contact",
    }
}

# ============================================================
# MAHSULOTLAR MA'LUMOTLARI
# ============================================================
CATEGORIES = {
    "electronics": {"uz": "📱 Elektronika", "ru": "📱 Электроника", "en": "📱 Electronics"},
    "clothing": {"uz": "👔 Kiyim", "ru": "👔 Одежда", "en": "👔 Clothing"},
    "food": {"uz": "🍎 Oziq-ovqat", "ru": "🍎 Продукты", "en": "🍎 Food"},
    "home": {"uz": "🏠 Uy uchun", "ru": "🏠 Для дома", "en": "🏠 Home"},
    "sports": {"uz": "⚽ Sport", "ru": "⚽ Спорт", "en": "⚽ Sports"},
    "beauty": {"uz": "💄 Go'zallik", "ru": "💄 Красота", "en": "💄 Beauty"},
}

PRODUCTS = [
    {
        "id": 1, "category": "electronics",
        "name": {"uz": "Samsung Galaxy A54", "ru": "Samsung Galaxy A54", "en": "Samsung Galaxy A54"},
        "desc": {
            "uz": "6.4\" AMOLED, 128GB, 50MP kamera, 5000mAh batareya",
            "ru": "6.4\" AMOLED, 128GB, камера 50МП, аккумулятор 5000мАч",
            "en": "6.4\" AMOLED, 128GB, 50MP camera, 5000mAh battery"
        },
        "price": 3299000, "image": "https://via.placeholder.com/300x300/gold/black?text=Samsung+A54", "stock": 15
    },
    {
        "id": 2, "category": "electronics",
        "name": {"uz": "Apple AirPods Pro", "ru": "Apple AirPods Pro", "en": "Apple AirPods Pro"},
        "desc": {
            "uz": "Aktiv shovqin bekor qilish, 30 soat batareya",
            "ru": "Активное шумоподавление, 30 часов работы",
            "en": "Active noise cancellation, 30 hours battery life"
        },
        "price": 1899000, "image": "https://via.placeholder.com/300x300/gold/black?text=AirPods+Pro", "stock": 8
    },
    {
        "id": 3, "category": "clothing",
        "name": {"uz": "Nike Air Max 270", "ru": "Nike Air Max 270", "en": "Nike Air Max 270"},
        "desc": {
            "uz": "Qulay sport poyabzal, o'lchamlar: 36-46",
            "ru": "Удобные кроссовки, размеры: 36-46",
            "en": "Comfortable sports shoes, sizes: 36-46"
        },
        "price": 899000, "image": "https://via.placeholder.com/300x300/gold/black?text=Nike+Air+Max", "stock": 25
    },
    {
        "id": 4, "category": "clothing",
        "name": {"uz": "Adidas Hoodie", "ru": "Adidas Худи", "en": "Adidas Hoodie"},
        "desc": {
            "uz": "Yumshoq paxta, o'lchamlar: S, M, L, XL, XXL",
            "ru": "Мягкий хлопок, размеры: S, M, L, XL, XXL",
            "en": "Soft cotton, sizes: S, M, L, XL, XXL"
        },
        "price": 459000, "image": "https://via.placeholder.com/300x300/gold/black?text=Adidas+Hoodie", "stock": 30
    },
    {
        "id": 5, "category": "food",
        "name": {"uz": "Premium Asal", "ru": "Премиум Мёд", "en": "Premium Honey"},
        "desc": {
            "uz": "Tabiiy tog' asali, 500g, sertifikatlangan",
            "ru": "Натуральный горный мёд, 500г, сертифицированный",
            "en": "Natural mountain honey, 500g, certified"
        },
        "price": 89000, "image": "https://via.placeholder.com/300x300/gold/black?text=Premium+Honey", "stock": 50
    },
    {
        "id": 6, "category": "food",
        "name": {"uz": "Organik Yong'oq", "ru": "Органические Орехи", "en": "Organic Nuts"},
        "desc": {
            "uz": "Aralash yong'oqlar to'plami, 1kg",
            "ru": "Смесь орехов, 1кг",
            "en": "Mixed nuts collection, 1kg"
        },
        "price": 129000, "image": "https://via.placeholder.com/300x300/gold/black?text=Organic+Nuts", "stock": 40
    },
    {
        "id": 7, "category": "home",
        "name": {"uz": "Philips Hue Lampa", "ru": "Лампа Philips Hue", "en": "Philips Hue Bulb"},
        "desc": {
            "uz": "Smart lampa, 16M rang, Wi-Fi boshqaruv",
            "ru": "Умная лампа, 16М цветов, управление Wi-Fi",
            "en": "Smart bulb, 16M colors, Wi-Fi control"
        },
        "price": 199000, "image": "https://via.placeholder.com/300x300/gold/black?text=Philips+Hue", "stock": 20
    },
    {
        "id": 8, "category": "sports",
        "name": {"uz": "Fitness Tracker", "ru": "Фитнес Трекер", "en": "Fitness Tracker"},
        "desc": {
            "uz": "Yurak urishi, uyqu monitoring, 7 kun batareya",
            "ru": "Пульс, мониторинг сна, 7 дней работы",
            "en": "Heart rate, sleep monitoring, 7 days battery"
        },
        "price": 349000, "image": "https://via.placeholder.com/300x300/gold/black?text=Fitness+Tracker", "stock": 12
    },
    {
        "id": 9, "category": "beauty",
        "name": {"uz": "La Mer Krem", "ru": "Крем La Mer", "en": "La Mer Cream"},
        "desc": {
            "uz": "Regeneratsiya kremi, 60ml, barcha teri turlari uchun",
            "ru": "Регенерирующий крем, 60мл, для всех типов кожи",
            "en": "Regenerating cream, 60ml, for all skin types"
        },
        "price": 2299000, "image": "https://via.placeholder.com/300x300/gold/black?text=La+Mer", "stock": 5
    },
    {
        "id": 10, "category": "electronics",
        "name": {"uz": "iPad Pro 11\"", "ru": "iPad Pro 11\"", "en": "iPad Pro 11\""},
        "desc": {
            "uz": "M2 chip, 256GB, Liquid Retina ekran",
            "ru": "Чип M2, 256ГБ, дисплей Liquid Retina",
            "en": "M2 chip, 256GB, Liquid Retina display"
        },
        "price": 8999000, "image": "https://via.placeholder.com/300x300/gold/black?text=iPad+Pro", "stock": 7
    },
]

# ============================================================
# FOYDALANUVCHILAR MA'LUMOTLARI (xotirada saqlash)
# ============================================================
users_db = {}      # {user_id: {lang, name, phone, registered_at}}
carts_db = {}      # {user_id: [{product_id, qty}]}
orders_db = {}     # {order_id: {user_id, items, total, status, created_at, comment}}
order_counter = [1000]

DATA_DIR = Path(__file__).parent / "data"
CARTS_FILE = DATA_DIR / "carts.json"
ADMINS_FILE = DATA_DIR / "admins.json"

admin_ids = set()

def load_admins():
    global admin_ids
    admin_ids = set(ENV_ADMIN_IDS)
    if ADMINS_FILE.exists():
        with open(ADMINS_FILE, encoding="utf-8") as f:
            extra = json.load(f)
        admin_ids.update(int(admin_id) for admin_id in extra)

def save_extra_admins():
    DATA_DIR.mkdir(exist_ok=True)
    extra = sorted(admin_ids - ENV_ADMIN_IDS)
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(extra, f, ensure_ascii=False, indent=2)

def is_admin(user_id):
    return user_id in admin_ids

def add_admin(user_id):
    admin_ids.add(int(user_id))
    save_extra_admins()

def remove_admin(user_id):
    user_id = int(user_id)
    if user_id in ENV_ADMIN_IDS:
        return False
    if user_id in admin_ids:
        admin_ids.discard(user_id)
        save_extra_admins()
        return True
    return False

async def notify_admins(bot, text, reply_markup=None):
    for admin_id in admin_ids:
        try:
            await bot.send_message(
                admin_id, text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Admin {admin_id} ga xabar yuborishda xato: {e}")

USER_COMMANDS = [
    BotCommand("start", "Botni ishga tushirish"),
    BotCommand("help", "Yordam"),
    BotCommand("catalog", "Mahsulotlar katalogi"),
    BotCommand("cart", "Savatcha"),
    BotCommand("orders", "Buyurtmalarim"),
    BotCommand("profile", "Profil"),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand("admin", "Admin panel"),
    BotCommand("admins", "Adminlar ro'yxati"),
]

async def setup_bot_commands(bot):
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in admin_ids:
        await bot.set_my_commands(
            ADMIN_COMMANDS,
            scope=BotCommandScopeChat(chat_id=admin_id),
        )
    logger.info("Telegram buyruqlari menyusi yangilandi")

DEMO_CART = [
    {"product_id": 1, "qty": 1},
    {"product_id": 2, "qty": 1},
    {"product_id": 3, "qty": 1},
    {"product_id": 5, "qty": 2},
]

def load_carts():
    global carts_db
    if not CARTS_FILE.exists():
        carts_db = {}
        return
    with open(CARTS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    carts_db = {int(user_id): items for user_id, items in data.items()}

def save_carts():
    DATA_DIR.mkdir(exist_ok=True)
    with open(CARTS_FILE, "w", encoding="utf-8") as f:
        json.dump(carts_db, f, ensure_ascii=False, indent=2)

def seed_demo_cart(user_id):
    if get_cart(user_id):
        return False
    carts_db[user_id] = [item.copy() for item in DEMO_CART]
    save_carts()
    return True

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {"lang": "uz", "name": "", "phone": "", "registered_at": datetime.now().isoformat()}
    return users_db[user_id]

def get_lang(user_id):
    return get_user(user_id).get("lang", "uz")

def t(user_id, key):
    lang = get_lang(user_id)
    return LANGUAGES.get(lang, LANGUAGES["uz"]).get(key, key)

def format_price(price):
    return f"{price:,} so'm".replace(",", " ")

def get_cart(user_id):
    return carts_db.get(user_id, [])

def get_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

def cart_total(user_id):
    total = 0
    for item in get_cart(user_id):
        product = get_product(item["product_id"])
        if product:
            total += product["price"] * item["qty"]
    return total

def add_to_cart(user_id, product_id):
    if user_id not in carts_db:
        carts_db[user_id] = []
    for item in carts_db[user_id]:
        if item["product_id"] == product_id:
            item["qty"] += 1
            save_carts()
            return
    carts_db[user_id].append({"product_id": product_id, "qty": 1})
    save_carts()

def remove_from_cart(user_id, product_id):
    if user_id in carts_db:
        carts_db[user_id] = [i for i in carts_db[user_id] if i["product_id"] != product_id]
        save_carts()

def clear_cart(user_id):
    carts_db[user_id] = []
    save_carts()

def create_order(user_id, comment=""):
    order_counter[0] += 1
    order_id = order_counter[0]
    cart = get_cart(user_id)
    items = []
    total = 0
    for item in cart:
        product = get_product(item["product_id"])
        if product:
            subtotal = product["price"] * item["qty"]
            total += subtotal
            items.append({
                "product_id": item["product_id"],
                "name": product["name"],
                "price": product["price"],
                "qty": item["qty"],
                "subtotal": subtotal
            })
    orders_db[order_id] = {
        "user_id": user_id,
        "items": items,
        "total": total,
        "status": "pending",
        "comment": comment,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    clear_cart(user_id)
    return order_id, orders_db[order_id]

# ============================================================
# KLAVIATURALAR
# ============================================================
def main_menu_keyboard(user_id):
    lang = get_lang(user_id)
    keyboard = [
        [t(user_id, "catalog"), t(user_id, "cart")],
        [t(user_id, "orders"), t(user_id, "profile")],
        [t(user_id, "about"), t(user_id, "contact")],
        [t(user_id, "language"), t(user_id, "search")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def categories_keyboard(user_id):
    lang = get_lang(user_id)
    buttons = []
    for cat_id, cat_names in CATEGORIES.items():
        buttons.append([InlineKeyboardButton(cat_names[lang], callback_data=f"cat_{cat_id}")])
    buttons.append([InlineKeyboardButton(t(user_id, "back"), callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def products_keyboard(user_id, category):
    lang = get_lang(user_id)
    products = [p for p in PRODUCTS if p["category"] == category]
    buttons = []
    for p in products:
        buttons.append([InlineKeyboardButton(
            f"{p['name'][lang]} — {format_price(p['price'])}",
            callback_data=f"prod_{p['id']}"
        )])
    buttons.append([InlineKeyboardButton(t(user_id, "back"), callback_data="catalog")])
    return InlineKeyboardMarkup(buttons)

def product_keyboard(user_id, product_id):
    cart = get_cart(user_id)
    in_cart = any(i["product_id"] == product_id for i in cart)
    product = get_product(product_id)
    buttons = []
    if in_cart:
        buttons.append([InlineKeyboardButton(t(user_id, "remove_from_cart"), callback_data=f"rem_{product_id}")])
    else:
        buttons.append([InlineKeyboardButton(t(user_id, "add_to_cart"), callback_data=f"add_{product_id}")])
    buttons.append([
        InlineKeyboardButton(t(user_id, "cart"), callback_data="view_cart"),
        InlineKeyboardButton(t(user_id, "back"), callback_data=f"cat_{product['category']}")
    ])
    return InlineKeyboardMarkup(buttons)

def cart_keyboard(user_id):
    cart = get_cart(user_id)
    buttons = []
    for item in cart:
        product = get_product(item["product_id"])
        if product:
            lang = get_lang(user_id)
            name = product["name"][lang]
            buttons.append([
                InlineKeyboardButton(f"❌ {name} (x{item['qty']})", callback_data=f"rem_{item['product_id']}")
            ])
    if cart:
        buttons.append([InlineKeyboardButton(t(user_id, "checkout"), callback_data="checkout")])
        buttons.append([InlineKeyboardButton(t(user_id, "clear_cart"), callback_data="clear_cart")])
    buttons.append([InlineKeyboardButton(t(user_id, "catalog"), callback_data="catalog")])
    return InlineKeyboardMarkup(buttons)

def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ])

def confirm_order_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "confirm_order"), callback_data="confirm_order")],
        [InlineKeyboardButton(t(user_id, "cancel"), callback_data="view_cart")],
    ])

def skip_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(user_id, "skip"), callback_data="skip_comment")]
    ])

# ============================================================
# OBUNA TEKSHIRISH
# ============================================================
async def check_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return True  # Agar kanal mavjud bo'lmasa, o'tkazib yuboramiz

async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(context.bot, user_id):
        lang = get_lang(user_id)
        msg = t(user_id, "subscribe_required") + CHANNEL_ID
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "subscribe_btn"), url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton(t(user_id, "check_subscribe"), callback_data="check_sub")]
        ])
        if update.message:
            await update.message.reply_text(msg, reply_markup=keyboard)
        elif update.callback_query:
            await update.callback_query.message.reply_text(msg, reply_markup=keyboard)
        return False
    return True

# ============================================================
# BUYRUQLAR
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    get_user(user_id)  # Foydalanuvchi yaratish
    
    # Obuna tekshirish
    if not await check_subscription(context.bot, user_id):
        msg = t(user_id, "subscribe_required") + CHANNEL_ID
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "subscribe_btn"), url=f"https://t.me/{CHANNEL_ID.lstrip('@')}")],
            [InlineKeyboardButton(t(user_id, "check_subscribe"), callback_data="check_sub")]
        ])
        await update.message.reply_text(msg, reply_markup=keyboard)
        return
    
    welcome_text = f"""
🌟 *EVZAP* — Premium Do'kon

{t(user_id, 'welcome')}

👤 Foydalanuvchi: {user.first_name}
🆔 ID: `{user_id}`
    """
    if is_admin(user_id):
        welcome_text += "\n\n👑 *Siz admin siz* — /admin bilan panel oching"
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(user_id)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    help_text = """
📖 *EVZAP Bot - Yordam*

/start — Botni ishga tushirish
/help — Yordam ma'lumotlari
/catalog — Mahsulotlar katalogi
/cart — Savatchani ko'rish
/orders — Buyurtmalarni ko'rish
/profile — Profilni ko'rish

💡 Tilni o'zgartirish uchun pastdagi *Til* tugmasini bosing.
"""
    if is_admin(user_id):
        help_text += """
👑 *Admin buyruqlari:*
/admin — Admin panel
/admins — Adminlar ro'yxati
/makeadmin — Yangi admin qo'shish
"""
    help_text += "\n❓ Savol va takliflar: @evzap_support"
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return
    
    total_users = len(users_db)
    total_orders = len(orders_db)
    total_revenue = sum(o["total"] for o in orders_db.values())
    pending_orders = sum(1 for o in orders_db.values() if o["status"] == "pending")
    
    admin_text = f"""
⚙️ *EVZAP Admin Panel*

👥 Foydalanuvchilar: {total_users}
📦 Jami buyurtmalar: {total_orders}
⏳ Kutilayotgan: {pending_orders}
💰 Jami daromad: {format_price(total_revenue)}

📋 So'nggi buyurtmalar:
    """
    
    recent_orders = list(orders_db.items())[-5:]
    for order_id, order in reversed(recent_orders):
        admin_text += f"\n#{order_id} — {format_price(order['total'])} — {order['status']}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📦 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
    ])
    await update.message.reply_text(admin_text, parse_mode="Markdown", reply_markup=keyboard)

async def makeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return

    target_id = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args and context.args[0].isdigit():
        target_id = int(context.args[0])

    if not target_id:
        await update.message.reply_text(
            "👤 *Admin qo'shish*\n\n"
            "1️⃣ `/makeadmin 123456789`\n"
            "2️⃣ Yoki foydalanuvchi xabariga *reply* qilib `/makeadmin` yuboring",
            parse_mode="Markdown"
        )
        return

    if is_admin(target_id):
        await update.message.reply_text(f"ℹ️ `{target_id}` allaqachon admin.", parse_mode="Markdown")
        return

    add_admin(target_id)
    await update.message.reply_text(
        f"✅ `{target_id}` endi admin!\n\nJami adminlar: {len(admin_ids)}",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(
            target_id,
            "🎉 Sizga *admin huquqi* berildi!\n\n/admin — admin panel",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Yangi adminga xabar yuborib bo'lmadi: {e}")

async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Siz admin emassiz!")
        return

    lines = ["👥 *Adminlar ro'yxati:*\n"]
    for admin_id in sorted(admin_ids):
        marker = " (asosiy)" if admin_id in ENV_ADMIN_IDS else ""
        lines.append(f"• `{admin_id}`{marker}")
    lines.append(f"\nJami: *{len(admin_ids)}* ta admin")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ============================================================
# XABAR HANDLERI (Reply Keyboard)
# ============================================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if not await require_subscription(update, context):
        return
    
    # Telefon raqami
    if update.message.contact:
        phone = update.message.contact.phone_number
        users_db[user_id]["phone"] = phone
        await update.message.reply_text(t(user_id, "phone_saved"), reply_markup=main_menu_keyboard(user_id))
        return
    
    # Matn buyruqlar
    catalog_texts = [v["catalog"] for v in LANGUAGES.values()]
    cart_texts = [v["cart"] for v in LANGUAGES.values()]
    orders_texts = [v["orders"] for v in LANGUAGES.values()]
    about_texts = [v["about"] for v in LANGUAGES.values()]
    contact_texts = [v["contact"] for v in LANGUAGES.values()]
    language_texts = [v["language"] for v in LANGUAGES.values()]
    profile_texts = [v["profile"] for v in LANGUAGES.values()]
    search_texts = [v["search"] for v in LANGUAGES.values()]
    
    if text in catalog_texts:
        await show_catalog(update, context)
    elif text in cart_texts:
        await show_cart_message(update, context)
    elif text in orders_texts:
        await show_orders(update, context)
    elif text in about_texts:
        await update.message.reply_text(t(user_id, "about_text"), reply_markup=main_menu_keyboard(user_id))
    elif text in contact_texts:
        await update.message.reply_text(t(user_id, "contact_text"), reply_markup=main_menu_keyboard(user_id))
    elif text in language_texts:
        await update.message.reply_text(t(user_id, "choose_lang"), reply_markup=language_keyboard())
    elif text in profile_texts:
        await show_profile(update, context)
    elif text in search_texts:
        context.user_data["searching"] = True
        await update.message.reply_text("🔍 Qidiruv so'zini kiriting:")
    elif context.user_data.get("searching"):
        context.user_data["searching"] = False
        await search_products(update, context, text)
    elif context.user_data.get("waiting_name"):
        context.user_data["waiting_name"] = False
        users_db[user_id]["name"] = text
        await update.message.reply_text(t(user_id, "name_saved"), reply_markup=main_menu_keyboard(user_id))
    elif context.user_data.get("waiting_comment"):
        context.user_data["waiting_comment"] = False
        await process_checkout(update, context, comment=text)

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    query_lower = query.lower()
    results = [
        p for p in PRODUCTS
        if query_lower in p["name"][lang].lower() or query_lower in p["desc"][lang].lower()
    ]
    if not results:
        await update.message.reply_text(f"🔍 '{query}' uchun hech narsa topilmadi.")
        return
    
    text = f"🔍 '{query}' bo'yicha {len(results)} ta natija:\n\n"
    buttons = []
    for p in results:
        text += f"• {p['name'][lang]} — {format_price(p['price'])}\n"
        buttons.append([InlineKeyboardButton(p['name'][lang], callback_data=f"prod_{p['id']}")])
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        t(user_id, "categories"),
        reply_markup=categories_keyboard(user_id)
    )

async def show_cart_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_cart(user_id):
        seed_demo_cart(user_id)
    cart = get_cart(user_id)
    
    lang = get_lang(user_id)
    text = f"🛒 *{t(user_id, 'cart')}*\n\n"
    for item in cart:
        product = get_product(item["product_id"])
        if product:
            text += f"• {product['name'][lang]} x{item['qty']} = {format_price(product['price'] * item['qty'])}\n"
    
    text += f"\n{t(user_id, 'total')}: *{format_price(cart_total(user_id))}*"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=cart_keyboard(user_id))

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_orders = [(oid, o) for oid, o in orders_db.items() if o["user_id"] == user_id]
    
    if not user_orders:
        await update.message.reply_text(t(user_id, "no_orders"), reply_markup=main_menu_keyboard(user_id))
        return
    
    lang = get_lang(user_id)
    status_map = {
        "pending": t(user_id, "pending"),
        "processing": t(user_id, "processing"),
        "shipped": t(user_id, "shipped"),
        "delivered": t(user_id, "delivered"),
        "cancelled": t(user_id, "cancelled"),
    }
    
    text = f"📦 *{t(user_id, 'orders')}*\n\n"
    for order_id, order in reversed(user_orders[-10:]):
        status = status_map.get(order["status"], order["status"])
        text += f"*#{order_id}* — {order['created_at']}\n"
        text += f"💰 {format_price(order['total'])} | {status}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    tg_user = update.effective_user
    lang_names = {"uz": "O'zbekcha 🇺🇿", "ru": "Русский 🇷🇺", "en": "English 🇬🇧"}
    
    text = f"""
👤 *Profil*

🆔 ID: `{user_id}`
👤 Telegram: {tg_user.first_name}
📝 Ism: {user_data.get('name') or 'Kiritilmagan'}
📞 Telefon: {user_data.get('phone') or 'Kiritilmagan'}
🌐 Til: {lang_names.get(user_data.get('lang', 'uz'), 'O\'zbekcha')}
📅 Ro'yxatdan o'tgan: {user_data.get('registered_at', '')[:10]}
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Ism o'zgartirish", callback_data="edit_name")],
        [InlineKeyboardButton("📞 Telefon qo'shish", callback_data="edit_phone")],
    ])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

# ============================================================
# CALLBACK QUERY HANDLER
# ============================================================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    lang = get_lang(user_id)
    
    # Obuna tekshirish
    if data == "check_sub":
        if await check_subscription(context.bot, user_id):
            await query.edit_message_text(t(user_id, "subscribed"))
            await context.bot.send_message(user_id, t(user_id, "welcome"), reply_markup=main_menu_keyboard(user_id))
        else:
            await query.answer(t(user_id, "not_subscribed"), show_alert=True)
        return
    
    # Til o'zgartirish
    if data.startswith("lang_"):
        new_lang = data.split("_")[1]
        users_db[user_id]["lang"] = new_lang
        await query.edit_message_text(t(user_id, "lang_changed"))
        await context.bot.send_message(user_id, t(user_id, "welcome"), reply_markup=main_menu_keyboard(user_id))
        return
    
    # Asosiy menyu
    if data == "main_menu":
        await query.edit_message_text(t(user_id, "menu"))
        await context.bot.send_message(user_id, t(user_id, "menu"), reply_markup=main_menu_keyboard(user_id))
        return
    
    # Katalog
    if data == "catalog":
        await query.edit_message_text(t(user_id, "categories"), reply_markup=categories_keyboard(user_id))
        return
    
    # Kategoriya
    if data.startswith("cat_"):
        cat_id = data[4:]
        cat_name = CATEGORIES.get(cat_id, {}).get(lang, cat_id)
        products_in_cat = [p for p in PRODUCTS if p["category"] == cat_id]
        if not products_in_cat:
            await query.edit_message_text("Bu kategoriyada mahsulot yo'q.", reply_markup=categories_keyboard(user_id))
            return
        await query.edit_message_text(
            f"📂 *{cat_name}*\n\n{len(products_in_cat)} ta mahsulot",
            parse_mode="Markdown",
            reply_markup=products_keyboard(user_id, cat_id)
        )
        return
    
    # Mahsulot
    if data.startswith("prod_"):
        product_id = int(data[5:])
        product = get_product(product_id)
        if not product:
            await query.answer("Mahsulot topilmadi!")
            return
        
        text = f"""
🏷 *{product['name'][lang]}*

📝 {product['desc'][lang]}

💰 *{format_price(product['price'])}*
📦 Mavjud: {product['stock']} {t(user_id, 'pieces')}
        """
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=product_keyboard(user_id, product_id)
        )
        return
    
    # Savatga qo'shish
    if data.startswith("add_"):
        product_id = int(data[4:])
        add_to_cart(user_id, product_id)
        product = get_product(product_id)
        await query.answer(f"✅ {product['name'][lang]} savatga qo'shildi!")
        await query.edit_message_reply_markup(reply_markup=product_keyboard(user_id, product_id))
        return
    
    # Savatdan olib tashlash
    if data.startswith("rem_"):
        product_id = int(data[4:])
        remove_from_cart(user_id, product_id)
        product = get_product(product_id)
        await query.answer(f"❌ {product['name'][lang]} savatdan olib tashlandi!")
        
        # Agar savatdan olib tashlayotgan bo'lsa, savatni yangilash
        if query.message.text and "Savat" in query.message.text or "Корзина" in (query.message.text or "") or "Cart" in (query.message.text or ""):
            cart = get_cart(user_id)
            if not cart:
                await query.edit_message_text(t(user_id, "cart_empty"), reply_markup=cart_keyboard(user_id))
            else:
                await query.edit_message_reply_markup(reply_markup=cart_keyboard(user_id))
        else:
            await query.edit_message_reply_markup(reply_markup=product_keyboard(user_id, product_id))
        return
    
    # Savatni ko'rish
    if data == "view_cart":
        if not get_cart(user_id):
            seed_demo_cart(user_id)
        cart = get_cart(user_id)
        
        text = f"🛒 *{t(user_id, 'cart')}*\n\n"
        for item in cart:
            product = get_product(item["product_id"])
            if product:
                text += f"• {product['name'][lang]} x{item['qty']} = {format_price(product['price'] * item['qty'])}\n"
        text += f"\n{t(user_id, 'total')}: *{format_price(cart_total(user_id))}*"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=cart_keyboard(user_id))
        return
    
    # Savatni tozalash
    if data == "clear_cart":
        clear_cart(user_id)
        await query.edit_message_text(t(user_id, "cart_empty"), reply_markup=cart_keyboard(user_id))
        return
    
    # Buyurtma berish
    if data == "checkout":
        cart = get_cart(user_id)
        if not cart:
            await query.answer(t(user_id, "cart_empty"))
            return
        context.user_data["waiting_comment"] = True
        await query.edit_message_text(
            t(user_id, "write_comment"),
            reply_markup=skip_keyboard(user_id)
        )
        return
    
    # Izohsiz o'tkazish
    if data == "skip_comment":
        context.user_data["waiting_comment"] = False
        await process_checkout_callback(query, context, comment="")
        return
    
    # Buyurtmani tasdiqlash
    if data == "confirm_order":
        comment = context.user_data.get("pending_comment", "")
        order_id, order = create_order(user_id, comment)
        
        # Foydalanuvchiga xabar
        await query.edit_message_text(
            f"✅ {t(user_id, 'order_placed')}\n\n#{order_id} buyurtma",
            parse_mode="Markdown"
        )
        
        # Adminga bildirishnoma
        user_data = get_user(user_id)
        tg_user = query.from_user
        admin_msg = f"""
🛒 *Yangi buyurtma #{order_id}*

👤 Foydalanuvchi: {tg_user.first_name} (@{tg_user.username or 'yo\'q'})
🆔 ID: `{user_id}`
📞 Tel: {user_data.get('phone') or 'Kiritilmagan'}
📅 Vaqt: {order['created_at']}

📦 Mahsulotlar:
        """
        for item in order["items"]:
            admin_msg += f"\n• {item['name'][lang]} x{item['qty']} = {format_price(item['subtotal'])}"
        
        admin_msg += f"\n\n💰 Jami: *{format_price(order['total'])}*"
        if order["comment"]:
            admin_msg += f"\n💬 Izoh: {order['comment']}"
        
        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Qabul qilish", callback_data=f"admin_accept_{order_id}")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data=f"admin_cancel_{order_id}")],
        ])
        
        try:
            await notify_admins(context.bot, admin_msg, admin_keyboard)
        except Exception as e:
            logger.error(f"Adminlarga xabar yuborishda xato: {e}")
        return
    
    # Admin buyurtma boshqaruvi
    if data.startswith("admin_accept_"):
        if not is_admin(user_id):
            await query.answer("⛔ Ruxsat yo'q!")
            return
        order_id = int(data.split("_")[2])
        if order_id in orders_db:
            orders_db[order_id]["status"] = "processing"
            customer_id = orders_db[order_id]["user_id"]
            await query.edit_message_text(f"✅ Buyurtma #{order_id} qabul qilindi!")
            try:
                await context.bot.send_message(
                    customer_id,
                    f"🔄 Buyurtmangiz #{order_id} qabul qilindi va tayyorlanmoqda!"
                )
            except:
                pass
        return
    
    if data.startswith("admin_cancel_"):
        if not is_admin(user_id):
            await query.answer("⛔ Ruxsat yo'q!")
            return
        order_id = int(data.split("_")[2])
        if order_id in orders_db:
            orders_db[order_id]["status"] = "cancelled"
            customer_id = orders_db[order_id]["user_id"]
            await query.edit_message_text(f"❌ Buyurtma #{order_id} bekor qilindi.")
            try:
                await context.bot.send_message(
                    customer_id,
                    f"❌ Kechirasiz, buyurtmangiz #{order_id} bekor qilindi. Batafsil: @evzap_support"
                )
            except:
                pass
        return
    
    # Profil tahrirlash
    if data == "edit_name":
        context.user_data["waiting_name"] = True
        await query.edit_message_text(t(user_id, "enter_name"))
        return
    
    if data == "edit_phone":
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(t(user_id, "share_contact"), request_contact=True)]],
            one_time_keyboard=True, resize_keyboard=True
        )
        await context.bot.send_message(user_id, t(user_id, "enter_phone"), reply_markup=keyboard)
        return
    
    # Admin statistika
    if data == "admin_stats":
        if not is_admin(user_id):
            await query.answer("⛔ Ruxsat yo'q!")
            return
        
        total_users = len(users_db)
        total_orders = len(orders_db)
        total_revenue = sum(o["total"] for o in orders_db.values())
        status_counts = {}
        for o in orders_db.values():
            status_counts[o["status"]] = status_counts.get(o["status"], 0) + 1
        
        stats_text = f"""
📊 *Statistika*

👥 Foydalanuvchilar: {total_users}
📦 Jami buyurtmalar: {total_orders}
💰 Jami daromad: {format_price(total_revenue)}

📋 Holat bo'yicha:
⏳ Kutilmoqda: {status_counts.get('pending', 0)}
🔄 Qayta ishlanmoqda: {status_counts.get('processing', 0)}
🚚 Yo'lda: {status_counts.get('shipped', 0)}
✅ Yetkazildi: {status_counts.get('delivered', 0)}
❌ Bekor: {status_counts.get('cancelled', 0)}
        """
        await query.edit_message_text(stats_text, parse_mode="Markdown")
        return
    
    if data == "admin_broadcast":
        if not is_admin(user_id):
            await query.answer("⛔ Ruxsat yo'q!")
            return
        context.user_data["broadcasting"] = True
        await query.edit_message_text("📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:")
        return

async def process_checkout_callback(query, context, comment=""):
    user_id = query.from_user.id
    lang = get_lang(user_id)
    cart = get_cart(user_id)
    
    text = t(user_id, "order_confirmation")
    for item in cart:
        product = get_product(item["product_id"])
        if product:
            text += f"• {product['name'][lang]} x{item['qty']} = {format_price(product['price'] * item['qty'])}\n"
    text += f"\n{t(user_id, 'total')}: *{format_price(cart_total(user_id))}*"
    if comment:
        text += f"\n\n{t(user_id, 'comment')}: {comment}"
    
    context.user_data["pending_comment"] = comment
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=confirm_order_keyboard(user_id))

async def process_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE, comment=""):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    cart = get_cart(user_id)
    
    text = t(user_id, "order_confirmation")
    for item in cart:
        product = get_product(item["product_id"])
        if product:
            text += f"• {product['name'][lang]} x{item['qty']} = {format_price(product['price'] * item['qty'])}\n"
    text += f"\n{t(user_id, 'total')}: *{format_price(cart_total(user_id))}*"
    if comment:
        text += f"\n\n{t(user_id, 'comment')}: {comment}"
    
    context.user_data["pending_comment"] = comment
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=confirm_order_keyboard(user_id))

# ============================================================
# RENDER UCHUN HTTP SERVER
# ============================================================
web_app = Flask(__name__)


@web_app.route("/")
def index():
    return "EVZAP Bot ishlayapti ✅", 200


@web_app.route("/health")
def health():
    return {"status": "ok", "service": "evzap-bot"}, 200


# ============================================================
# ASOSIY FUNKSIYA
# ============================================================
def build_application():
    async def init_bot(application):
        await setup_bot_commands(application.bot)

    app = Application.builder().token(BOT_TOKEN).post_init(init_bot).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("makeadmin", makeadmin_command))
    app.add_handler(CommandHandler("admins", admins_command))
    app.add_handler(CommandHandler("catalog", lambda u, c: show_catalog(u, c)))
    app.add_handler(CommandHandler("cart", lambda u, c: show_cart_message(u, c)))
    app.add_handler(CommandHandler("orders", lambda u, c: show_orders(u, c)))
    app.add_handler(CommandHandler("profile", lambda u, c: show_profile(u, c)))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT | filters.CONTACT, handle_message))

    return app


def run_telegram_bot():
    application = build_application()
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ BOT_TOKEN o'rnatilmagan!")
        print("📌 .env faylini yarating yoki muhit o'zgaruvchisini o'rnating:")
        print("   BOT_TOKEN=your_token_here")
        print("   ADMIN_IDS=111111111,222222222")
        return
    
    print("🚀 EVZAP Bot ishga tushmoqda...")

    load_admins()
    load_carts()
    if seed_demo_cart(PRIMARY_ADMIN_ID):
        print(f"🛒 Demo savat to'ldirildi (admin ID: {PRIMARY_ADMIN_ID})")

    print("✅ Bot sozlandi!")
    print(f"👤 Adminlar: {', '.join(str(a) for a in sorted(admin_ids))}")
    print(f"📢 Kanal: {CHANNEL_ID}")

    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True, name="telegram-bot")
    bot_thread.start()
    print("🤖 Telegram bot fon rejimida ishga tushdi")

    port = int(os.getenv("PORT", 10000))
    print(f"🌐 HTTP server: http://0.0.0.0:{port}")
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
