import asyncio
import json
import logging
import httpx  # مكتبة لإرسال الطلبات للمواقع
from datetime import datetime  # لمعالجة التواريخ والوقت
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from parsel import Selector  # مكتبة استخراج النصوص من HTML

# ==========================================
# ⚙️ إعدادات البوت
# ==========================================
# 🔴 التوكن الخاص بك تم وضعه هنا
TOKEN = "8502902855:AAEZAMUR2A9i2IsvseBlentxZZjH2CZs100"

# تفعيل نظام التسجيل لمراقبة الأخطاء
logging.basicConfig(level=logging.INFO)

# ==========================================
# 🌍 قاموس الدول (Database)
# ==========================================
COUNTRIES = {
    "IQ": "العراق 🇮🇶", "SA": "السعودية 🇸🇦", "EG": "مصر 🇪🇬", "AE": "الإمارات 🇦🇪",
    "KW": "الكويت 🇰🇼", "QA": "قطر 🇶🇦", "BH": "البحرين 🇧🇭", "OM": "عمان 🇴🇲",
    "YE": "اليمن 🇾🇪", "SY": "سوريا 🇸🇾", "LB": "لبنان 🇱🇧", "JO": "الأردن 🇯🇴",
    "PS": "فلسطين 🇵🇸", "DZ": "الجزائر 🇩🇿", "MA": "المغرب 🇲🇦", "TN": "تونس 🇹🇳",
    "LY": "ليبيا 🇱🇾", "SD": "السودان 🇸🇩", "SO": "الصومال 🇸🇴", "MR": "موريتانيا 🇲🇷",
    "US": "الولايات المتحدة 🇺🇸", "TR": "تركيا 🇹🇷", "DE": "ألمانيا 🇩🇪", "FR": "فرنسا 🇫🇷",
    "GB": "بريطانيا 🇬🇧", "RU": "روسيا 🇷🇺", "CN": "الصين 🇨🇳", "IN": "الهند 🇮🇳",
}

# ==========================================
# 🛠️ دوال التحليل (Logic Functions)
# ==========================================

def calculate_account_age(creation_date_str):
    try:
        if creation_date_str == "غير معروف": return "غير معروف"
        creation_date = datetime.strptime(creation_date_str, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - creation_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        days = (delta.days % 365) % 30
        parts = []
        if years > 0: parts.append(f"{years} سنة")
        if months > 0: parts.append(f"{months} شهر")
        if days > 0: parts.append(f"{days} يوم")
        return "، ".join(parts) if parts else "جديد جداً"
    except: return "غير معروف"

def analyze_quality(followers, likes, videos):
    try:
        f = int(str(followers).replace(',', ''))
        l = int(str(likes).replace(',', ''))
        v = int(str(videos).replace(',', ''))
        if f > 1000000: size_tag = "💎 هوامير تيك توك"
        elif f > 100000: size_tag = "🔥 مؤثر قوي"
        else: size_tag = "👤 حساب شخصي نشط"
        if v == 0: quality_tag = "👻 صامت"
        elif l > f * 10: quality_tag = "🚀 تفاعل متفجر (Viral)"
        elif l > f * 2: quality_tag = "✅ تفاعل ممتاز (جمهور حقيقي)"
        else: quality_tag = "⚖️ تفاعل طبيعي"
        return f"{size_tag} | {quality_tag}"
    except: return "غير محدد"

# ==========================================
# 🕵️‍♂️ المحرك الرئيسي (Core Scraper)
# ==========================================
async def fetch_tiktok_vip(username_or_url):
    target = username_or_url.strip()
    if "tiktok.com" in target:
        if "@" in target: target = target.split("@")[1].split("?")[0]
    if not target.startswith("@"): target = f"@{target.replace('https://www.tiktok.com/', '')}"
    username = target.lstrip("@")
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.tiktok.com/",
        "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8"
    }
    async with httpx.AsyncClient(headers=headers, timeout=25.0) as client:
        try:
            response = await client.get(url)
            selector = Selector(response.text)
            script_data = selector.xpath("//script[@id='__UNIVERSAL_DATA_FOR_REHYDRATION__']/text()").get() or \
                          selector.xpath("//script[@id='SIGI_STATE']/text()").get()
            if not script_data: return None
            data = json.loads(script_data)
            user_info = {}
            if "__DEFAULT_SCOPE__" in data:
                user_info = data["__DEFAULT_SCOPE__"].get("webapp.user-detail", {}).get("userInfo", {})
            if not user_info:
                 user_info = data.get("UserModule", {}).get("users", {}).get(username, {})
            user = user_info