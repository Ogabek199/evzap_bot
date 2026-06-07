# 🌟 EVZAP — Premium Do'kon

## 📦 Loyiha Tuzilishi

```
evzap/
├── bot/
│   ├── bot.py              ← Telegram bot (asosiy fayl)
│   ├── requirements.txt    ← Python kutubxonalari
│   └── .env.example        ← Muhit o'zgaruvchilari namunasi
└── webapp/
    └── index.html          ← Web sayt (to'liq)
```

---

## 🤖 TELEGRAM BOT - O'rnatish

### 1. Bot Yaratish
1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username'ini kiriting
4. Olingan **TOKEN** ni saqlang

### 2. Admin ID Olish
1. [@userinfobot](https://t.me/userinfobot) ga yozing
2. U sizning Telegram ID'ingizni ko'rsatadi

### 3. O'rnatish

```bash
# Python kutubxonalarini o'rnatish
cd bot/
pip install -r requirements.txt

# .env faylini yaratish
cp .env.example .env
nano .env  # O'z ma'lumotlaringizni kiriting
```

### 4. .env fayl namunasi:
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
ADMIN_ID=123456789
CHANNEL_ID=@evzap_channel
```

### 5. Ishga tushirish

```bash
python bot.py
```

---

## 🌐 WEB SAYT - O'rnatish

### Mahalliy foydalanish:
```bash
cd webapp/
# Brauzerda index.html faylini oching
open index.html
```

### Server'ga joylashtirish:
```bash
# Nginx yoki Apache orqali
cp webapp/index.html /var/www/html/
```

---

## ✨ Bot Funksionalliklari

| Funksiya | Tavsif |
|----------|--------|
| `/start` | Botni ishga tushirish |
| `/catalog` | Mahsulotlar katalogi |
| `/cart` | Savat ko'rish |
| `/orders` | Buyurtmalar tarixi |
| `/profile` | Profil boshqaruvi |
| `/admin` | Admin panel |

### Kategoriyalar:
- 📱 Elektronika
- 👔 Kiyim
- 🍎 Oziq-ovqat
- 🏠 Uy uchun
- ⚽ Sport
- 💄 Go'zallik

### Ko'p Tilli Qo'llab-quvvatlash:
- 🇺🇿 O'zbek tili
- 🇷🇺 Rus tili
- 🇬🇧 Ingliz tili

### Admin Imkoniyatlari:
- 📊 Statistika ko'rish
- 📦 Buyurtmalarni boshqarish
- ✅ Buyurtmani qabul qilish/bekor qilish
- 📢 Barcha foydalanuvchilarga xabar yuborish

---

## 🌐 Web Sayt Funksionalliklari

- 🛍 Mahsulotlar katalogi (grid ko'rinish)
- 🔍 Qidiruv va filtrlash
- 📂 Kategoriyalar bo'yicha saralash
- 💰 Narx bo'yicha saralash
- 🛒 Savat (miqdor o'zgartirish, o'chirish)
- ❤️ Sevimlilar ro'yxati
- 📋 Buyurtma berish formasi
- 🌐 Ko'p tilli (UZ/RU/EN)
- 📱 Responsive dizayn
- ✨ Toast xabarnomalar

---

## 🎨 Dizayn

- **Stil**: Oltin + Qora + Neon
- **Font**: Cinzel Decorative + Rajdhani
- **Framework**: Tailwind CSS
- **Animatsiyalar**: CSS transitions + keyframes

---

## 📞 Qo'llab-quvvatlash

Savollar uchun: @evzap_support
