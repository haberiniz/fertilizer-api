# main.py
# ═══════════════════════════════════════════════════════════════════
# 🌾 نظام التوصيات الزراعية الجزائري - FastAPI Backend
# ═══════════════════════════════════════════════════════════════════
# ✅ يقرأ المفتاح من متغيرات البيئة (Render Safe)
# ✅ ذكي وديناميكي: أفضل 3 محاصيل حسب المدخلات
# ✅ شرح مفصل: "لماذا هذا المحصول؟"

import os
import math
import requests
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════
# 🔐 قراءة متغيرات البيئة بأمان (مهم لـ Render)
# ═══════════════════════════════════════════════════════════════════
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
PORT = int(os.environ.get("PORT", 8000))
FASTAPI_ENV = os.environ.get("FASTAPI_ENV", "development")

print(f"🌾 Starting AgriPAI API - Environment: {FASTAPI_ENV}")
print(f"🔑 OPENWEATHER_API_KEY: {'✅ Set' if OPENWEATHER_API_KEY else '❌ Not set'}")

# ═══════════════════════════════════════════════════════════════════
# 📊 DATABASES — 58 Wilayas + 65+ Crops
# ═══════════════════════════════════════════════════════════════════

MONTHS_AR = ["يناير","فبراير","مارس","أبريل","مايو","يونيو",
             "يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]

WILAYAS = {
    "أدرار": {"رقم":1, "lat":27.8789,"lng":-0.2673, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":50},
    "الشلف": {"رقم":2, "lat":36.1699,"lng":1.3373, "تربة":"طينية", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":450},
    "الأغواط": {"رقم":3, "lat":33.8003,"lng":2.8699, "تربة":"رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":200},
    "أم البواقي": {"رقم":4, "lat":35.8667,"lng":7.1167, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":400},
    "باتنة": {"رقم":5, "lat":35.5550,"lng":6.1742, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":380},
    "بجاية": {"رقم":6, "lat":36.7539,"lng":5.0561, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"عالية", "avgRainfall":800},
    "بسكرة": {"رقم":7, "lat":34.8167,"lng":5.7333, "تربة":"رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":180},
    "بشار": {"رقم":8, "lat":31.6167,"lng":-2.2167, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":80},
    "البليدة": {"رقم":9, "lat":36.4833,"lng":2.8333, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"عالية", "avgRainfall":700},
    "البويرة": {"رقم":10, "lat":36.3667,"lng":3.9000, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"عالية", "avgRainfall":750},
    "تمنراست": {"رقم":11, "lat":22.7917,"lng":5.5167, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":30},
    "تبسة": {"رقم":12, "lat":35.4000,"lng":8.1167, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":350},
    "تلمسان": {"رقم":13, "lat":35.2833,"lng":-1.3167, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":420},
    "تيارت": {"رقم":14, "lat":35.3667,"lng":1.3167, "تربة":"طينية", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":400},
    "تيزي وزو": {"رقم":15, "lat":36.7117,"lng":4.0450, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"عالية", "avgRainfall":900},
    "الجزائر": {"رقم":16, "lat":36.7538,"lng":3.0588, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":600},
    "الجلفة": {"رقم":17, "lat":34.6667,"lng":3.2667, "تربة":"طينية رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":250},
    "جيجل": {"رقم":18, "lat":36.8167,"lng":5.7667, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"عالية جداً", "avgRainfall":1100},
    "سطيف": {"رقم":19, "lat":36.1917,"lng":5.4083, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":450},
    "سعيدة": {"رقم":20, "lat":34.8333,"lng":0.1500, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":380},
    "سكيكدة": {"رقم":21, "lat":36.8833,"lng":6.9167, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"عالية", "avgRainfall":650},
    "سيدي بلعباس": {"رقم":22, "lat":35.1833,"lng":-0.6417, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":400},
    "عنابة": {"رقم":23, "lat":36.9000,"lng":7.7600, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"عالية", "avgRainfall":700},
    "قالمة": {"رقم":24, "lat":36.4667,"lng":7.4333, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"عالية", "avgRainfall":680},
    "قسنطينة": {"رقم":25, "lat":36.3650,"lng":6.6147, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":520},
    "المدية": {"رقم":26, "lat":36.2667,"lng":2.7667, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":550},
    "مستغانم": {"رقم":27, "lat":35.9333,"lng":0.1000, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":420},
    "المسيلة": {"رقم":28, "lat":35.7167,"lng":4.5667, "تربة":"طينية رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":280},
    "معسكر": {"رقم":29, "lat":35.3833,"lng":0.1333, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":450},
    "ورقلة": {"رقم":30, "lat":31.9454,"lng":5.3268, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":60},
    "وهران": {"رقم":31, "lat":35.7333,"lng":-0.6333, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":400},
    "البيض": {"رقم":32, "lat":33.6667,"lng":1.0000, "تربة":"رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":220},
    "إليزي": {"رقم":33, "lat":26.1833,"lng":8.4667, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":25},
    "برج بوعريريج": {"رقم":34, "lat":36.0667,"lng":4.7667, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":480},
    "بومرداس": {"رقم":35, "lat":36.7667,"lng":3.4667, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":580},
    "الطارف": {"رقم":36, "lat":36.7667,"lng":8.3167, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"عالية", "avgRainfall":720},
    "تندوف": {"رقم":37, "lat":27.6667,"lng":-8.0000, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":40},
    "تيسمسيلت": {"رقم":38, "lat":35.6167,"lng":1.0833, "تربة":"طينية", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":420},
    "الوادي": {"رقم":39, "lat":33.3667,"lng":6.8667, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة", "avgRainfall":90},
    "خنشلة": {"رقم":40, "lat":35.4333,"lng":7.1500, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":420},
    "سوق أهراس": {"رقم":41, "lat":36.2833,"lng":7.9500, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"عالية", "avgRainfall":650},
    "تيبازة": {"رقم":42, "lat":36.5833,"lng":2.4333, "تربة":"سوداء", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":620},
    "ميلة": {"رقم":43, "lat":36.4500,"lng":6.2667, "تربة":"سوداء", "منطقة":"شمالية شرقية", "أمطار":"متوسطة", "avgRainfall":500},
    "عين الدفلى": {"رقم":44, "lat":36.2667,"lng":1.9667, "تربة":"طينية", "منطقة":"شمالية", "أمطار":"متوسطة", "avgRainfall":520},
    "النعامة": {"رقم":45, "lat":33.2667,"lng":-0.3167, "تربة":"رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":180},
    "عين تيموشنت": {"رقم":46, "lat":35.3000,"lng":-1.1333, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":410},
    "غرداية": {"رقم":47, "lat":32.4833,"lng":3.8000, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة", "avgRainfall":100},
    "رليزان": {"رقم":48, "lat":35.7500,"lng":0.7833, "تربة":"طينية", "منطقة":"شمالية غربية", "أمطار":"متوسطة", "avgRainfall":380},
    "تيميمون": {"رقم":49, "lat":29.2636,"lng":0.2408, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":45},
    "برج باجي مختار": {"رقم":50, "lat":23.0250,"lng":0.9583, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":35},
    "أولاد جلال": {"رقم":51, "lat":34.4167,"lng":5.0667, "تربة":"رملية", "منطقة":"شبه صحراوية", "أمطار":"جافة", "avgRainfall":150},
    "بني عباس": {"رقم":52, "lat":30.1333,"lng":-2.1667, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":55},
    "عين صالح": {"رقم":53, "lat":27.2000,"lng":2.4667, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":30},
    "عين قزام": {"رقم":54, "lat":26.6167,"lng":2.3833, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":20},
    "تقرت": {"رقم":55, "lat":33.0667,"lng":6.0667, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة", "avgRainfall":85},
    "جانت": {"رقم":56, "lat":24.5500,"lng":9.4833, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":15},
    "المغير": {"رقم":57, "lat":33.9500,"lng":5.9167, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة", "avgRainfall":95},
    "المنيعة": {"رقم":58, "lat":29.7833,"lng":2.8833, "تربة":"رملية", "منطقة":"صحراوية", "أمطار":"جافة جداً", "avgRainfall":50},
}

CROPS = {
    "القمح الصلب": {"فئة":"حبوب","إنتاج":2.5,"دورة":180,"مياه":"منخفضة","تربة":["سوداء","طينية","طينية رملية"],"أمراض":["الصدأ البني","التفحم المغطى"],"زراعة":"أكتوبر","عائلة":"Poaceae","صعوبة":"سهل","سعر":4500,"تصدير":True,"tempMin":5,"tempMax":25,"rainfallMin":300,"rainfallMax":600,"rotGood":["الحمص","العدس"],"rotBad":["الشعير"]},
    "الطماطم": {"فئة":"خضروات","إنتاج":35.0,"دورة":120,"مياه":"عالية","تربة":["سوداء","طينية"],"أمراض":["الآفة المتأخرة","الذبول"],"زراعة":"فبراير","عائلة":"Solanaceae","صعوبة":"متوسط","سعر":25000,"تصدير":True,"tempMin":15,"tempMax":32,"rainfallMin":500,"rainfallMax":900,"rotGood":["البصل","الجزر"],"rotBad":["البطاطس","الفلفل"]},
    "الفلفل": {"فئة":"خضروات","إنتاج":22.0,"دورة":150,"مياه":"عالية","تربة":["سوداء","طينية"],"أمراض":["الذبول","البياض الدقيقي"],"زراعة":"فبراير","عائلة":"Solanaceae","صعوبة":"متوسط","سعر":40000,"تصدير":True,"tempMin":18,"tempMax":32,"rainfallMin":500,"rainfallMax":800,"rotGood":["الجزر","البصل"],"rotBad":["الطماطم","الباذنجان"]},
    "الباذنجان": {"فئة":"خضروات","إنتاج":20.0,"دورة":140,"مياه":"عالية","تربة":["سوداء","طينية"],"أمراض":["الذبول","البياض الدقيقي"],"زراعة":"مارس","عائلة":"Solanaceae","صعوبة":"متوسط","سعر":20000,"تصدير":False,"tempMin":18,"tempMax":35,"rainfallMin":400,"rainfallMax":700,"rotGood":["الجزر","البصل"],"rotBad":["الطماطم","الفلفل"]},
    "البطاطس": {"فئة":"خضروات","إنتاج":22.0,"دورة":90,"مياه":"متوسطة","تربة":["سوداء","طينية","طينية رملية"],"أمراض":["الآفة المتأخرة","الجرب"],"زراعة":"فبراير","عائلة":"Solanaceae","صعوبة":"متوسط","سعر":15000,"تصدير":True,"tempMin":10,"tempMax":25,"rainfallMin":400,"rainfallMax":700,"rotGood":["الحمص","الفول"],"rotBad":["الطماطم","الفلفل"]},
    "الجزر": {"فئة":"خضروات","إنتاج":22.0,"دورة":100,"مياه":"متوسطة","تربة":["سوداء","طينية"],"أمراض":["الذبول","البياض الدقيقي"],"زراعة":"سبتمبر","عائلة":"Apiaceae","صعوبة":"سهل","سعر":18000,"تصدير":False,"tempMin":8,"tempMax":25,"rainfallMin":300,"rainfallMax":600,"rotGood":["البازلاء","الفول"],"rotBad":["الكرفس"]},
    "البصل": {"فئة":"خضروات","إنتاج":20.0,"دورة":120,"مياه":"متوسطة","تربة":["سوداء","طينية"],"أمراض":["البياض الدقيقي","العفن"],"زراعة":"سبتمبر","عائلة":"Amaryllidaceae","صعوبة":"سهل","سعر":25000,"تصدير":True,"tempMin":10,"tempMax":28,"rainfallMin":300,"rainfallMax":600,"rotGood":["البازلاء","القمح"],"rotBad":["الثوم"]},
    "الثوم": {"فئة":"خضروات","إنتاج":8.0,"دورة":180,"مياه":"منخفضة","تربة":["سوداء","طينية"],"أمراض":["البياض الدقيقي","الصدأ"],"زراعة":"أكتوبر","عائلة":"Amaryllidaceae","صعوبة":"سهل","سعر":120000,"تصدير":True,"tempMin":5,"tempMax":25,"rainfallMin":300,"rainfallMax":500,"rotGood":["القمح","الشعير"],"rotBad":["البصل"]},
    "الفول": {"فئة":"بقوليات","إنتاج":2.5,"دورة":180,"مياه":"منخفضة","تربة":["سوداء","طينية","طينية رملية"],"أمراض":["الصدأ","الذبول"],"زراعة":"أكتوبر","عائلة":"Fabaceae","صعوبة":"سهل","سعر":60000,"تصدير":False,"tempMin":5,"tempMax":22,"rainfallMin":300,"rainfallMax":600,"rotGood":["القمح","الشعير"],"rotBad":["الحمص"]},
    "الحمص": {"فئة":"بقوليات","إنتاج":1.8,"دورة":170,"مياه":"منخفضة","تربة":["سوداء","طينية","طينية رملية"],"أمراض":["الذبول","العفن"],"زراعة":"أكتوبر","عائلة":"Fabaceae","صعوبة":"سهل","سعر":85000,"تصدير":True,"tempMin":10,"tempMax":30,"rainfallMin":250,"rainfallMax":500,"rotGood":["القمح","الشعير"],"rotBad":["العدس"]},
    "العدس": {"فئة":"بقوليات","إنتاج":1.5,"دورة":160,"مياه":"منخفضة","تربة":["سوداء","طينية","طينية رملية"],"أمراض":["الذبول","الصدأ"],"زراعة":"أكتوبر","عائلة":"Fabaceae","صعوبة":"سهل","سعر":100000,"تصدير":True,"tempMin":5,"tempMax":28,"rainfallMin":250,"rainfallMax":500,"rotGood":["القمح","الشعير"],"rotBad":["الحمص"]},
    "البازلاء": {"فئة":"بقوليات","إنتاج":3.5,"دورة":120,"مياه":"متوسطة","تربة":["سوداء","طينية"],"أمراض":["البياض الدقيقي","الذبول"],"زراعة":"نوفمبر","عائلة":"Fabaceae","صعوبة":"سهل","سعر":45000,"تصدير":False,"tempMin":7,"tempMax":22,"rainfallMin":350,"rainfallMax":650,"rotGood":["القمح","الذرة"],"rotBad":["الفول"]},
    "التمر": {"فئة":"فاكهة","إنتاج":8.0,"دورة":365,"مياه":"منخفضة","تربة":["رملية","طينية رملية"],"أمراض":["البياض","الذبول"],"زراعة":"سبتمبر","عائلة":"Arecaceae","صعوبة":"خبير","سعر":300000,"تصدير":True,"tempMin":20,"tempMax":50,"rainfallMin":0,"rainfallMax":200,"rotGood":[],"rotBad":[]},
    "الزيتون": {"فئة":"فاكهة","إنتاج":3.5,"دورة":365,"مياه":"منخفضة","تربة":["سوداء","طينية","رملية"],"أمراض":["الذبول","الصدأ"],"زراعة":"نوفمبر","عائلة":"Oleaceae","صعوبة":"سهل","سعر":120000,"تصدير":True,"tempMin":0,"tempMax":40,"rainfallMin":300,"rainfallMax":800,"rotGood":[],"rotBad":[]},
    "الشمام": {"فئة":"فاكهة","إنتاج":20.0,"دورة":90,"مياه":"عالية","تربة":["سوداء","طينية","رملية"],"أمراض":["البياض","الذبول"],"زراعة":"أبريل","عائلة":"Cucurbitaceae","صعوبة":"سهل","سعر":30000,"تصدير":True,"tempMin":20,"tempMax":38,"rainfallMin":400,"rainfallMax":800,"rotGood":["الفول"],"rotBad":["البطيخ"]},
    "البطيخ": {"فئة":"فاكهة","إنتاج":22.0,"دورة":85,"مياه":"عالية","تربة":["سوداء","طينية","رملية"],"أمراض":["البياض","الذبول"],"زراعة":"أبريل","عائلة":"Cucurbitaceae","صعوبة":"سهل","سعر":20000,"تصدير":True,"tempMin":22,"tempMax":38,"rainfallMin":400,"rainfallMax":800,"rotGood":["الفول"],"rotBad":["الشمام"]},
    "الرمان": {"فئة":"فاكهة","إنتاج":10.0,"دورة":365,"مياه":"منخفضة","تربة":["سوداء","طينية","رملية"],"أمراض":["الذبول","العفن"],"زراعة":"فبراير","عائلة":"Lythraceae","صعوبة":"سهل","سعر":150000,"تصدير":True,"tempMin":15,"tempMax":42,"rainfallMin":200,"rainfallMax":600,"rotGood":[],"rotBad":[]},
    "التين": {"فئة":"فاكهة","إنتاج":8.0,"دورة":365,"مياه":"منخفضة","تربة":["سوداء","طينية","رملية"],"أمراض":["الصدأ","البياض"],"زراعة":"فبراير","عائلة":"Moraceae","صعوبة":"سهل","سعر":100000,"تصدير":True,"tempMin":10,"tempMax":38,"rainfallMin":300,"rainfallMax":700,"rotGood":[],"rotBad":[]},
    "اللوز": {"فئة":"فاكهة","إنتاج":1.5,"دورة":365,"مياه":"منخفضة جداً","تربة":["سوداء","طينية","رملية"],"أمراض":["الصدأ","البياض"],"زراعة":"فبراير","عائلة":"Rosaceae","صعوبة":"سهل","سعر":800000,"تصدير":True,"tempMin":5,"tempMax":38,"rainfallMin":200,"rainfallMax":600,"rotGood":[],"rotBad":[]},
    "عباد الشمس": {"فئة":"محاصيل صناعية","إنتاج":2.2,"دورة":130,"مياه":"متوسطة","تربة":["سوداء","طينية"],"أمراض":["الصدأ","البياض"],"زراعة":"أبريل","عائلة":"Asteraceae","صعوبة":"سهل","سعر":45000,"تصدير":False,"tempMin":18,"tempMax":35,"rainfallMin":350,"rainfallMax":700,"rotGood":["الحبوب"],"rotBad":[]},
    "البرسيم": {"فئة":"أعلاف","إنتاج":10.0,"دورة":180,"مياه":"متوسطة","تربة":["سوداء","طينية"],"أمراض":["الذبول","الصدأ"],"زراعة":"أكتوبر","عائلة":"Fabaceae","صعوبة":"سهل","سعر":8000,"تصدير":False,"tempMin":5,"tempMax":28,"rainfallMin":350,"rainfallMax":700,"rotGood":["القمح"],"rotBad":[]},
    "الكمون": {"فئة":"توابل وعطريات","إنتاج":0.8,"دورة":120,"مياه":"منخفضة","تربة":["رملية","طينية رملية"],"أمراض":["الذبول","البياض"],"زراعة":"فبراير","عائلة":"Apiaceae","صعوبة":"متوسط","سعر":400000,"تصدير":True,"tempMin":15,"tempMax":35,"rainfallMin":200,"rainfallMax":500,"rotGood":["الحبوب"],"rotBad":[]},
    "الزعفران": {"فئة":"توابل وعطريات","إنتاج":0.01,"دورة":90,"مياه":"منخفضة","تربة":["سوداء","طينية"],"أمراض":["الذبول","العفن"],"زراعة":"أغسطس","عائلة":"Iridaceae","صعوبة":"خبير","سعر":50000000,"تصدير":True,"tempMin":10,"tempMax":25,"rainfallMin":300,"rainfallMax":600,"rotGood":[],"rotBad":[]},
    "النعناع": {"فئة":"توابل وعطريات","إنتاج":2.0,"دورة":90,"مياه":"عالية","تربة":["سوداء","طينية"],"أمراض":["الصدأ","البياض"],"زراعة":"مارس","عائلة":"Lamiaceae","صعوبة":"سهل","سعر":80000,"تصدير":False,"tempMin":10,"tempMax":30,"rainfallMin":400,"rainfallMax":800,"rotGood":[],"rotBad":[]},
}

# Pre-compute harvest month + plantIdx for each crop
for name, d in CROPS.items():
    plant_idx = MONTHS_AR.index(d["زراعة"]) if d["زراعة"] in MONTHS_AR else 0
    harvest_days = plant_idx * 30 + d["دورة"]
    harvest_idx = round(harvest_days / 30) % 12
    d["plantIdx"] = plant_idx
    d["harvestIdx"] = harvest_idx
    d["حصاد"] = MONTHS_AR[harvest_idx]

FAMILIES = {c: d["عائلة"] for c, d in CROPS.items()}
INCOMPATIBLE = {"Poaceae":["Poaceae"],"Solanaceae":["Solanaceae"],"Cucurbitaceae":["Cucurbitaceae"],"Brassicaceae":["Brassicaceae"]}
GOOD_ROTATIONS = {"Poaceae":["Fabaceae","Apiaceae"],"Fabaceae":["Solanaceae","Asteraceae"],"Solanaceae":["Apiaceae","Fabaceae"],"Cucurbitaceae":["Fabaceae"]}

# ═══════════════════════════════════════════════════════════════════
# TIME UTILS
# ═══════════════════════════════════════════════════════════════════

def resolve_year(chosen_month_idx: int) -> int:
    t = datetime.now()
    current_month = t.month - 1
    return t.year if chosen_month_idx >= current_month else t.year + 1

def timing_penalty(crop_idx: int, user_idx: int) -> int:
    diff = min(abs(crop_idx - user_idx), 12 - abs(crop_idx - user_idx))
    return [0,5,12,20,28,31,34,37,40,43,46,49,52][min(diff, 12)]

def is_plantable_window(crop_idx: int, user_idx: int) -> bool:
    diff = min(abs(crop_idx - user_idx), 12 - abs(crop_idx - user_idx))
    return diff <= 3

def timing_status(crop_idx: int, user_idx: int) -> dict:
    current = datetime.now().month - 1
    diff = min(abs(crop_idx - user_idx), 12 - abs(crop_idx - user_idx))
    is_past = user_idx < current
    year = resolve_year(user_idx)
    ideal = MONTHS_AR[crop_idx]
    chosen = MONTHS_AR[user_idx]
    
    if diff == 0:
        if user_idx == current:
            return {"type":"optimal","icon":"✅","msg":f"الشهر الحالي ({chosen}) مثالي تماماً"}
        return {"type":"future","icon":"📅","msg":f"الزراعة في {chosen} {year}"}
    if diff <= 1:
        return {"type":"near","icon":"📅","msg":f"المثالي: {ideal} — اخترت {chosen} (مقبول)"}
    if is_past:
        return {"type":"future","icon":"🔄","msg":f"المثالي: {ideal} — {chosen} {year} (الموسم القادم)"}
    return {"type":"warn","icon":"⚠️","msg":f"المثالي: {ideal} — فارق {diff} أشهر"}

# ═══════════════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════════════

def check_rotation(prev: str, crop: str) -> dict:
    if not prev: return {"valid":True,"msg":""}
    if prev == crop: return {"valid":False,"msg":f"لا يُزرع {crop} بعد نفسه"}
    pf, cf = FAMILIES.get(prev), FAMILIES.get(crop)
    if pf and cf and cf in INCOMPATIBLE.get(pf, []):
        return {"valid":False,"msg":f"تعارض عائلي: {crop} لا يُزرع بعد {prev}"}
    if pf and cf and cf in GOOD_ROTATIONS.get(pf, []):
        return {"valid":True,"msg":f"دوران مثالي ✓"}
    return {"valid":True,"msg":"دوران مقبول"}

def rule_score(crop: dict, wd: dict, req, weather_temp) -> int:
    score = 0
    wmap = {"منخفضة جداً":0,"منخفضة":1,"متوسطة":2,"عالية":3}
    wdiff = abs(wmap.get(req.water,1) - wmap.get(crop["مياه"],1))
    score += 25 if wdiff==0 else (15 if wdiff==1 else 4)
    score += 25 if wd["تربة"] in crop["تربة"] else 5
    r = wd.get("avgRainfall",300)
    if crop["rainfallMin"] <= r <= crop["rainfallMax"]: score += 8
    elif r >= crop["rainfallMin"]*0.6: score += 4
    score += max(0, 20 - timing_penalty(crop["plantIdx"], req.plant_month))
    diff_map = {"سهل":0,"متوسط":1,"خبير":2}
    exp_map = {"مبتدئ":0,"متوسط":1,"خبير":2}
    cd, ue = diff_map.get(crop["صعوبة"],0), exp_map.get(req.experience,0)
    score += 12 if ue>=cd else (8 if ue==cd-1 else 1)
    if req.goal=="تصدير" and crop["تصدير"]: score += 10
    elif req.goal=="بيع" and crop["إنتاج"]>=5: score += 10
    elif req.goal in ["اكتفاء","كلاهما"]: score += 10
    else: score += 5
    if "صحراوية" in wd["منطقة"] and crop["مياه"] in ["منخفضة جداً","منخفضة"]: score += 5
    elif "شمالية" in wd["منطقة"] and crop["مياه"]=="عالية": score += 5
    else: score += 2
    return min(max(score,0),100)

def ml_score(crop: dict, wd: dict, req, weather_temp) -> int:
    wmap = {"منخفضة جداً":0,"منخفضة":0.33,"متوسطة":0.66,"عالية":1.0}
    soil = 1.0 if wd["تربة"] in crop["تربة"] else 0.12
    water = 1 - abs(wmap.get(req.water,0.5) - wmap.get(crop["مياه"],0.5))
    yield_n = min(math.log1p(crop["إنتاج"]) / math.log1p(50), 1.0)
    season = max(0, 1 - timing_penalty(crop["plantIdx"], req.plant_month)/30)
    temp_fit = 0.65
    if weather_temp and crop["tempMin"] <= weather_temp <= crop["tempMax"]: temp_fit = 1.0
    elif weather_temp:
        overshoot = max(0, weather_temp-crop["tempMax"], crop["tempMin"]-weather_temp)
        temp_fit = max(0.1, 1 - overshoot/15)
    r = wd.get("avgRainfall",300)
    rain_fit = 1.0 if crop["rainfallMin"]<=r<=crop["rainfallMax"] else max(0.1, 1-abs(r-(crop["rainfallMin"]+crop["rainfallMax"])/2)/400)
    rot = 0.12 if req.prev_crop in crop.get("rotGood",[]) else (-0.15 if req.prev_crop in crop.get("rotBad",[]) else 0)
    region = 1.0 if ("صحراوية" in wd["منطقة"] and crop["مياه"] in ["منخفضة جداً","منخفضة"]) or ("شمالية" in wd["منطقة"] and crop["مياه"]=="عالية") else 0.6
    diff_map = {"سهل":1.0,"متوسط":0.7,"خبير":0.4}
    exp_map2 = {"مبتدئ":0.3,"متوسط":0.7,"خبير":1.0}
    exp_fit = max(0, 1-abs(exp_map2.get(req.experience,0.5)-(1-diff_map.get(crop["صعوبة"],0.5))))
    goal = 1.0 if req.goal=="تصدير" and crop["تصدير"] else (min(math.log1p(crop["إنتاج"])/math.log1p(40),1.0) if req.goal=="بيع" else 0.8)
    raw = soil*0.22 + water*0.17 + season*0.18 + yield_n*0.10 + temp_fit*0.10 + rain_fit*0.08 + region*0.07 + exp_fit*0.05 + goal*0.03 + rot
    return round(min(max(raw,0),1)*100)

def hybrid_score(rs: int, ms: int) -> int:
    return round(rs * 0.58 + ms * 0.42)

def build_explanation(crop_name: str, crop: dict, wd: dict, req, weather_temp) -> list:
    items = []
    wL = {"منخفضة جداً":"شحيحة جداً","منخفضة":"محدودة","متوسطة":"معتدلة","عالية":"وفيرة"}
    if wd["تربة"] in crop["تربة"]:
        items.append({"type":"good","text":f"تربة {wd['تربة']} مثالية — الجذور تتأقلم بامتياز"})
    else:
        items.append({"type":"warn","text":f"تربة {wd['تربة']} غير مثالية — أضف سماداً عضوياً"})
    if crop["مياه"]==req.water or (req.water=="متوسطة" and crop["مياه"]=="منخفضة"):
        items.append({"type":"good","text":f"الري ({wL[req.water]}) يتوافق مع احتياج {crop_name}"})
    elif req.water=="عالية" and crop["مياه"]=="منخفضة":
        items.append({"type":"warn","text":f"ري زائد قد يسبب تعفن الجذور — استخدم ري بالتنقيط"})
    else:
        items.append({"type":"warn","text":f"{crop_name} يحتاج ري {crop['مياه']} — فكّر في الري بالتنقيط"})
    ts = timing_status(crop["plantIdx"], req.plant_month)
    items.append({"type":"good" if ts["type"] in ["optimal","near"] else "warn","text":ts["msg"]})
    year = resolve_year(req.plant_month)
    items.append({"type":"info","text":f"دورة النمو: {crop['دورة']} يوم — زراعة {MONTHS_AR[req.plant_month]} {year} ← حصاد {crop['حصاد']}"})
    dm = {"سهل":"مناسب للجميع","متوسط":"يتطلب خبرة متوسطة","خبير":"يتطلب خبرة عالية"}
    if req.experience=="خبير":
        items.append({"type":"good","text":f"{dm[crop['صعوبة']]} — بخبرتك ستحقق أعلى إنتاجية"})
    elif req.experience=="مبتدئ" and crop["صعوبة"]=="خبير":
        items.append({"type":"warn","text":f"يحتاج خبرة عالية — ابدأ بكميات صغيرة أو استعن بمرشد"})
    else:
        items.append({"type":"info","text":f"{dm[crop['صعوبة']]} — مناسب لمستوى خبرتك"})
    if weather_temp:
        if 15<=weather_temp<=28: items.append({"type":"good","text":f"الحرارة {weather_temp}°م مناسبة لنمو {crop_name}"})
        elif weather_temp>38: items.append({"type":"warn","text":f"حرارة {weather_temp}°م مرتفعة — أضف تغطية ظلية"})
        elif weather_temp<10: items.append({"type":"warn","text":f"حرارة {weather_temp}°م منخفضة — احمِ المحصول من الصقيع"})
        else: items.append({"type":"info","text":f"الحرارة الحالية {weather_temp}°م — مقبولة"})
    if req.goal=="تصدير" and crop["تصدير"]:
        items.append({"type":"good","text":f"محصول تصديري — مطلوب في الأسواق الجزائرية والأوروبية"})
    elif req.goal=="بيع" and crop["إنتاج"]>=10:
        items.append({"type":"good","text":f"إنتاجية عالية ({crop['إنتاج']} طن/هكتار) — مردود تجاري ممتاز"})
    elif req.goal=="اكتفاء":
        items.append({"type":"info","text":f"مناسب للاكتفاء الذاتي وتأمين غذاء الأسرة"})
    return items

# ═══════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════

app = FastAPI(
    title="🌾 نظام التوصيات الزراعية الجزائري",
    description="API ذكي لتقديم أفضل 3 محاصيل للزراعة حسب الولاية، التربة، المياه، والخبرة",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FarmRequest(BaseModel):
    wilaya: str = Field(..., description="اسم الولاية الجزائرية", example="الجزائر")
    area: float = Field(..., gt=0, description="مساحة الأرض بالهكتار", example=2.5)
    plant_month: int = Field(..., ge=0, le=11, description="شهر الزراعة (0=يناير ... 11=ديسمبر)", example=2)
    prev_crop: Optional[str] = Field(default="", description="المحصول السابق", example="القمح الصلب")
    category: Optional[str] = Field(default="", description="فئة المحصول المطلوبة", example="خضروات")
    water: str = Field(..., description="مستوى المياه", example="متوسطة")
    goal: str = Field(..., description="الهدف", example="بيع")
    experience: str = Field(..., description="الخبرة", example="متوسط")

@app.get("/")
def root():
    return {"status":"ok","message":"🌾 نظام التوصيات الزراعية الجزائري v2.0","endpoints":{"GET /wilayas":"قائمة الولايات","GET /crops":"قائمة المحاصيل","POST /recommend":"الحصول على التوصيات"}}

@app.get("/wilayas")
def get_wilayas():
    return sorted([{"name":k,"code":v["رقم"],"region":v["منطقة"],"soil":v["تربة"],"rainfall":v["أمطار"]} for k,v in WILAYAS.items()],key=lambda x:x["code"])

@app.get("/crops")
def get_crops():
    return sorted(list(CROPS.keys()))

@app.post("/recommend")
def recommend(req: FarmRequest):
    if req.wilaya not in WILAYAS:
        raise HTTPException(status_code=400,detail=f"الولاية '{req.wilaya}' غير موجودة")
    
    wd = WILAYAS[req.wilaya]
    
    # جلب الطقس من Open-Meteo (مجاني، لا يحتاج مفتاح)
    weather_temp = None
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={wd['lat']}&longitude={wd['lng']}&current=temperature_2m&timezone=Africa/Algiers"
        r = requests.get(url, timeout=4)
        if r.status_code==200:
            weather_temp = r.json().get("current",{}).get("temperature_2m")
    except: pass
    
    scored = []
    for name, crop in CROPS.items():
        if req.category and crop["فئة"]!=req.category: continue
        rot = check_rotation(req.prev_crop, name)
        if not rot["valid"]: continue
        if not is_plantable_window(crop["plantIdx"], req.plant_month): continue
        
        rs = rule_score(crop, wd, req, weather_temp)
        ms = ml_score(crop, wd, req, weather_temp)
        hs = hybrid_score(rs, ms)
        
        scored.append({
            "name":name,"score":hs,"rule_score":rs,"ml_score":ms,
            "yield_total":round(crop["إنتاج"]*req.area,2),"yield_per_ha":crop["إنتاج"],
            "cycle_days":crop["دورة"],"category":crop["فئة"],"difficulty":crop["صعوبة"],
            "water_need":crop["مياه"],"plant_month":MONTHS_AR[crop["plantIdx"]],
            "harvest_month":crop["حصاد"],"resolve_year":resolve_year(req.plant_month),
            "timing":timing_status(crop["plantIdx"],req.plant_month),"rotation":rot,
            "diseases":crop["أمراض"],"exportable":crop["تصدير"],"price_dzd_per_ton":crop["سعر"],
            "soil_match":wd["تربة"] in crop["تربة"],
            "explanation":build_explanation(name,crop,wd,req,weather_temp),
            "breakdown":{"soil":100 if wd["تربة"] in crop["تربة"] else 22,
                        "water":round((1-abs({"منخفضة جداً":0,"منخفضة":1,"متوسطة":2,"عالية":3}.get(req.water,1)-{"منخفضة جداً":0,"منخفضة":1,"متوسطة":2,"عالية":3}.get(crop["مياه"],1))/3)*100),
                        "season":max(0,round((1-timing_penalty(crop["plantIdx"],req.plant_month)/30)*100)),
                        "experience":max(0,round((1-abs({"مبتدئ":0,"متوسط":1,"خبير":2}.get(req.experience,0)-{"سهل":0,"متوسط":1,"خبير":2}.get(crop["صعوبة"],0))/2)*100))}
        })
    
    if not scored:
        for name, crop in CROPS.items():
            if req.category and crop["فئة"]!=req.category: continue
            rot = check_rotation(req.prev_crop, name)
            if not rot["valid"]: continue
            rs = rule_score(crop, wd, req, weather_temp)
            ms = ml_score(crop, wd, req, weather_temp)
            hs = hybrid_score(rs, ms)
            scored.append({"name":name,"score":hs,"rule_score":rs,"ml_score":ms,
                          "yield_total":round(crop["إنتاج"]*req.area,2),"yield_per_ha":crop["إنتاج"],
                          "cycle_days":crop["دورة"],"category":crop["فئة"],"difficulty":crop["صعوبة"],
                          "water_need":crop["مياه"],"plant_month":MONTHS_AR[crop["plantIdx"]],
                          "harvest_month":crop["حصاد"],"resolve_year":resolve_year(req.plant_month),
                          "timing":timing_status(crop["plantIdx"],req.plant_month),"rotation":rot,
                          "diseases":crop["أمراض"],"exportable":crop["تصدير"],"price_dzd_per_ton":crop["سعر"],
                          "soil_match":wd["تربة"] in crop["تربة"],
                          "explanation":build_explanation(name,crop,wd,req,weather_temp),
                          "breakdown":{"soil":100 if wd["تربة"] in crop["تربة"] else 22,"water":50,"season":50,"experience":50}})
    
    scored.sort(key=lambda x:(x["score"],x["yield_total"]),reverse=True)
    top = []
    used_fam, used_cat = set(), set()
    for item in scored:
        if len(top)>=3: break
        fam, cat = FAMILIES.get(item["name"],""), item["category"]
        if fam not in used_fam and cat not in used_cat:
            top.append(item); used_fam.add(fam); used_cat.add(cat)
    for item in scored:
        if len(top)>=3: break
        fam = FAMILIES.get(item["name"],"")
        if fam not in used_fam: top.append(item); used_fam.add(fam)
    for item in scored:
        if len(top)>=3: break
        if item not in top: top.append(item)
    
    return {
        "wilaya":req.wilaya,"region":wd["منطقة"],"soil":wd["تربة"],"rainfall":wd["أمطار"],
        "weather_temp":weather_temp,"plant_month_name":MONTHS_AR[req.plant_month],
        "area":req.area,"goal":req.goal,"water":req.water,"experience":req.experience,
        "prev_crop":req.prev_crop,"top_crops":top,"total_candidates":len(scored)
    }

@app.get("/health")
def health_check():
    return {"status":"healthy","timestamp":datetime.now().isoformat(),"env":FASTAPI_ENV}

# ═══════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=FASTAPI_ENV=="development")