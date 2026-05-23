import json
import os
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # السماح بـ CORS للاتصال من Flutter

# ============================================================
# مفتاح API لخدمة الطقس - سيتم قراءته من متغيرات البيئة
# ============================================================
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
OPENMETEO_API_URL = "https://api.open-meteo.com/v1/forecast"

# ============================================================
# BASE DE DONNÉES COMPLÈTE
# ============================================================

# 58 Wilayas - التصحيح: إضافة الأسماء العربية مباشرة
WILAYA_COORDINATES = {
    "أدرار": {"lat": 27.8667, "lon": -0.2833, "code": 1, "region": "Sud-Ouest"},
    "الشلف": {"lat": 36.1650, "lon": 1.3317, "code": 2, "region": "Nord-Ouest"},
    "الأغواط": {"lat": 33.8000, "lon": 2.8650, "code": 3, "region": "Sud"},
    "أم البواقي": {"lat": 35.8775, "lon": 7.1136, "code": 4, "region": "Est"},
    "باتنة": {"lat": 35.5667, "lon": 6.1667, "code": 5, "region": "Est"},
    "بجاية": {"lat": 36.7500, "lon": 5.0833, "code": 6, "region": "Nord-Est"},
    "بسكرة": {"lat": 34.8500, "lon": 5.7300, "code": 7, "region": "Sud-Est"},
    "بشار": {"lat": 31.6167, "lon": -2.2167, "code": 8, "region": "Sud-Ouest"},
    "البليدة": {"lat": 36.4700, "lon": 2.8300, "code": 9, "region": "Nord-Centre"},
    "البويرة": {"lat": 36.3800, "lon": 3.9000, "code": 10, "region": "Nord-Centre"},
    "تمنراست": {"lat": 22.7850, "lon": 5.5228, "code": 11, "region": "Extrême-Sud"},
    "تبسة": {"lat": 35.4000, "lon": 8.1167, "code": 12, "region": "Est"},
    "تلمسان": {"lat": 34.8828, "lon": -1.3167, "code": 13, "region": "Nord-Ouest"},
    "تيارت": {"lat": 35.3667, "lon": 1.3167, "code": 14, "region": "Ouest"},
    "تيزي وزو": {"lat": 36.7200, "lon": 4.0500, "code": 15, "region": "Nord-Centre"},
    "الجزائر": {"lat": 36.7764, "lon": 3.0586, "code": 16, "region": "Nord-Centre"},
    "الجلفة": {"lat": 34.6700, "lon": 3.2500, "code": 17, "region": "Sud"},
    "جيجل": {"lat": 36.8167, "lon": 5.7667, "code": 18, "region": "Nord-Est"},
    "سطيف": {"lat": 36.1900, "lon": 5.4100, "code": 19, "region": "Est"},
    "سعيدة": {"lat": 34.8300, "lon": 0.1500, "code": 20, "region": "Ouest"},
    "سكيكدة": {"lat": 36.8667, "lon": 6.9000, "code": 21, "region": "Nord-Est"},
    "سيدي بلعباس": {"lat": 35.1900, "lon": -0.6400, "code": 22, "region": "Nord-Ouest"},
    "عنابة": {"lat": 36.9000, "lon": 7.7667, "code": 23, "region": "Nord-Est"},
    "قالمة": {"lat": 36.4667, "lon": 7.4333, "code": 24, "region": "Est"},
    "قسنطينة": {"lat": 36.3650, "lon": 6.6147, "code": 25, "region": "Est"},
    "المدية": {"lat": 36.2675, "lon": 2.7500, "code": 26, "region": "Nord-Centre"},
    "مستغانم": {"lat": 35.9300, "lon": 0.0900, "code": 27, "region": "Nord-Ouest"},
    "المسيلة": {"lat": 35.7058, "lon": 4.5419, "code": 28, "region": "Est"},
    "معسكر": {"lat": 35.4000, "lon": 0.1333, "code": 29, "region": "Nord-Ouest"},
    "ورقلة": {"lat": 31.9500, "lon": 5.3167, "code": 30, "region": "Sud-Est"},
    "وهران": {"lat": 35.6969, "lon": -0.6331, "code": 31, "region": "Nord-Ouest"},
    "البيض": {"lat": 33.6833, "lon": 1.0167, "code": 32, "region": "Ouest"},
    "إليزي": {"lat": 26.5000, "lon": 8.4167, "code": 33, "region": "Sud-Est"},
    "برج بوعريريج": {"lat": 36.0700, "lon": 4.7600, "code": 34, "region": "Est"},
    "بومرداس": {"lat": 36.7600, "lon": 3.4800, "code": 35, "region": "Nord-Centre"},
    "الطارف": {"lat": 36.7667, "lon": 8.3167, "code": 36, "region": "Nord-Est"},
    "تندوف": {"lat": 27.6667, "lon": -8.1333, "code": 37, "region": "Extrême-Sud"},
    "تيسمسيلت": {"lat": 35.6000, "lon": 1.8167, "code": 38, "region": "Ouest"},
    "الوادي": {"lat": 33.3667, "lon": 6.8667, "code": 39, "region": "Sud-Est"},
    "خنشلة": {"lat": 35.4333, "lon": 7.1333, "code": 40, "region": "Est"},
    "سوق أهراس": {"lat": 36.2833, "lon": 7.9500, "code": 41, "region": "Est"},
    "تيبازة": {"lat": 36.5900, "lon": 2.4400, "code": 42, "region": "Nord-Centre"},
    "ميلة": {"lat": 36.4500, "lon": 6.2667, "code": 43, "region": "Est"},
    "عين الدفلى": {"lat": 36.2600, "lon": 1.9700, "code": 44, "region": "Nord-Centre"},
    "النعامة": {"lat": 33.2667, "lon": -0.3167, "code": 45, "region": "Ouest"},
    "عين تموشنت": {"lat": 35.3000, "lon": -1.1333, "code": 46, "region": "Nord-Ouest"},
    "غرداية": {"lat": 32.4833, "lon": 3.6667, "code": 47, "region": "Sud"},
    "غليزان": {"lat": 35.7400, "lon": 0.5500, "code": 48, "region": "Nord-Ouest"},
    "تيميمون": {"lat": 29.2667, "lon": 0.2333, "code": 49, "region": "Sud-Ouest"},
    "برج باجي مختار": {"lat": 21.3833, "lon": 0.9500, "code": 50, "region": "Extrême-Sud"},
    "أولاد جلال": {"lat": 34.4333, "lon": 5.0667, "code": 51, "region": "Sud-Est"},
    "بني عباس": {"lat": 30.1167, "lon": -2.1667, "code": 52, "region": "Sud-Ouest"},
    "عين صالح": {"lat": 27.2000, "lon": 2.4833, "code": 53, "region": "Extrême-Sud"},
    "عين قزام": {"lat": 19.5667, "lon": 5.7667, "code": 54, "region": "Extrême-Sud"},
    "تقرت": {"lat": 33.1000, "lon": 6.0667, "code": 55, "region": "Sud-Est"},
    "جانت": {"lat": 24.5500, "lon": 9.4833, "code": 56, "region": "Extrême-Sud"},
    "المغير": {"lat": 33.9500, "lon": 5.9167, "code": 57, "region": "Sud-Est"},
    "المنيعة": {"lat": 30.5833, "lon": 2.8833, "code": 58, "region": "Sud"}
}

# Type de sol par wilaya
WILAYA_SOIL_MAPPING = {
    "أدرار": "Sols sableux (Erg)", "الشلف": "Sols alluviaux", "الأغواط": "Sols sableux (Erg)",
    "أم البواقي": "Vertisols", "باتنة": "Sols peu évolués d'érosion",
    "بجاية": "Sols bruns calcaires", "بسكرة": "Sols sableux (Erg)",
    "بشار": "Sols sableux (Erg)", "البليدة": "Sols alluviaux", "البويرة": "Sols bruns calcaires",
    "تمنراست": "Sols minéraux bruts (Reg)", "تبسة": "Sols bruns calcaires",
    "تلمسان": "Sols bruns calcaires", "تيارت": "Sols bruns calcaires",
    "تيزي وزو": "Sols peu évolués d'érosion", "الجزائر": "Sols alluviaux",
    "الجلفة": "Sols bruns calcaires", "جيجل": "Sols bruns calcaires",
    "سطيف": "Sols bruns calcaires", "سعيدة": "Sols bruns calcaires",
    "سكيكدة": "Sols bruns calcaires", "سيدي بلعباس": "Sols bruns calcaires",
    "عنابة": "Sols alluviaux", "قالمة": "Vertisols", "قسنطينة": "Vertisols",
    "المدية": "Sols bruns calcaires", "مستغانم": "Sols bruns calcaires",
    "المسيلة": "Sols bruns calcaires", "معسكر": "Sols bruns calcaires",
    "ورقلة": "Sols sableux (Erg)", "وهران": "Sols bruns calcaires",
    "البيض": "Sols bruns calcaires", "إليزي": "Sols minéraux bruts (Reg)",
    "برج بوعريريج": "Sols bruns calcaires", "بومرداس": "Sols bruns calcaires",
    "الطارف": "Sols hydromorphes (Oasis)", "تندوف": "Sols minéraux bruts (Reg)",
    "تيسمسيلت": "Sols bruns calcaires", "الوادي": "Sols sableux (Erg)",
    "خنشلة": "Sols bruns calcaires", "سوق أهراس": "Sols bruns calcaires",
    "تيبازة": "Sols alluviaux", "ميلة": "Vertisols", "عين الدفلى": "Sols alluviaux",
    "النعامة": "Sols bruns calcaires", "عين تموشنت": "Sols bruns calcaires",
    "غرداية": "Sols hydromorphes (Oasis)", "غليزان": "Sols bruns calcaires",
    "تيميمون": "Sols sableux (Erg)", "برج باجي مختار": "Sols minéraux bruts (Reg)",
    "أولاد جلال": "Sols sableux (Erg)", "بني عباس": "Sols sableux (Erg)",
    "عين صالح": "Sols minéraux bruts (Reg)", "عين قزام": "Sols minéraux bruts (Reg)",
    "تقرت": "Sols hydromorphes (Oasis)", "جانت": "Sols minéraux bruts (Reg)",
    "المغير": "Sols hydromorphes (Oasis)", "المنيعة": "Sols sableux (Erg)"
}

# تحليل العناصر الغذائية للتربة
SOL_NUTRIENTS_COMPLET = {
    "Sols alluviaux": {
        "N": 85, "P": 45, "K": 180, "Ca": 2500, "Mg": 350, "S": 25,
        "Fe": 15, "Zn": 3.5, "B": 1.2, "Mn": 8,
        "ph": 7.0, "mo_pct": 3.5, "cec": 22, "efficacite": 0.80,
        "description": "Sols fertiles de vallée - Équilibrés"
    },
    "Sols bruns calcaires": {
        "N": 55, "P": 25, "K": 150, "Ca": 3500, "Mg": 250, "S": 18,
        "Fe": 8, "Zn": 1.8, "B": 0.8, "Mn": 5,
        "ph": 7.6, "mo_pct": 2.0, "cec": 18, "efficacite": 0.75,
        "description": "Sols calcaires - Carence fréquente en P et Zn"
    },
    "Vertisols": {
        "N": 70, "P": 35, "K": 200, "Ca": 2800, "Mg": 400, "S": 30,
        "Fe": 20, "Zn": 4.0, "B": 1.5, "Mn": 10,
        "ph": 7.5, "mo_pct": 3.0, "cec": 28, "efficacite": 0.85,
        "description": "Sols argileux - Excellente rétention"
    },
    "Sols peu évolués d'érosion": {
        "N": 25, "P": 10, "K": 80, "Ca": 1500, "Mg": 120, "S": 8,
        "Fe": 5, "Zn": 0.8, "B": 0.3, "Mn": 3,
        "ph": 7.0, "mo_pct": 1.0, "cec": 10, "efficacite": 0.55,
        "description": "Sols érodés - Carences multiples"
    },
    "Sols sableux (Erg)": {
        "N": 12, "P": 6, "K": 45, "Ca": 800, "Mg": 60, "S": 5,
        "Fe": 3, "Zn": 0.4, "B": 0.2, "Mn": 1.5,
        "ph": 8.0, "mo_pct": 0.3, "cec": 5, "efficacite": 0.50,
        "description": "Sols sableux - Très pauvres, lessivage intense"
    },
    "Sols minéraux bruts (Reg)": {
        "N": 5, "P": 2, "K": 25, "Ca": 500, "Mg": 30, "S": 2,
        "Fe": 2, "Zn": 0.2, "B": 0.1, "Mn": 1,
        "ph": 8.2, "mo_pct": 0.1, "cec": 3, "efficacite": 0.40,
        "description": "Sols squelettiques - Extrêmement pauvres"
    },
    "Sols hydromorphes (Oasis)": {
        "N": 40, "P": 20, "K": 110, "Ca": 1800, "Mg": 200, "S": 15,
        "Fe": 10, "Zn": 2.0, "B": 0.8, "Mn": 4,
        "ph": 7.5, "mo_pct": 1.5, "cec": 15, "efficacite": 0.65,
        "description": "Sols d'oasis - Fertilité modérée"
    }
}

# قاعدة بيانات المحاصيل
# قاعدة بيانات المحاصيل - جميع المحاصيل مدعومة ✅
CROPS_DATABASE = {
    # ============================================================
    # 🌾 الحبوب (Céréales)
    # ============================================================
    "قمح صلب": {
        "categorie": "Céréale", "cycle_jours": 180,
        "stades": {
            "الإنبات": {"duree": 15, "N": 25, "P": 40, "K": 30, "Ca": 10, "Mg": 5, "S": 3},
            "الخضري": {"duree": 55, "N": 70, "P": 35, "K": 55, "Ca": 15, "Mg": 8, "S": 5},
            "الاستطالة": {"duree": 30, "N": 60, "P": 25, "K": 45, "Ca": 10, "Mg": 7, "S": 4},
            "التسنبل": {"duree": 40, "N": 45, "P": 20, "K": 50, "Ca": 8, "Mg": 5, "S": 3},
            "النضج": {"duree": 40, "N": 10, "P": 15, "K": 20, "Ca": 5, "Mg": 3, "S": 2},
        },
        "temperature_optimale": [12, 25], "temperature_critique": [0, 35],
        "irrigation": {"الإنبات": 3, "الخضري": 5, "الاستطالة": 6, "التسنبل": 7, "النضج": 2},
        "carences_sensibles": ["N", "P"], "excès_sensibles": ["N"],
    },
    "قمح لين": {
        "categorie": "Céréale", "cycle_jours": 170,
        "stades": {
            "الإنبات": {"duree": 14, "N": 24, "P": 38, "K": 28, "Ca": 9, "Mg": 5, "S": 3},
            "الخضري": {"duree": 52, "N": 68, "P": 34, "K": 53, "Ca": 14, "Mg": 7, "S": 5},
            "الاستطالة": {"duree": 28, "N": 58, "P": 24, "K": 43, "Ca": 9, "Mg": 6, "S": 4},
            "التسنبل": {"duree": 38, "N": 43, "P": 19, "K": 48, "Ca": 7, "Mg": 4, "S": 3},
            "النضج": {"duree": 38, "N": 9, "P": 14, "K": 19, "Ca": 4, "Mg": 3, "S": 2},
        },
        "temperature_optimale": [11, 24], "temperature_critique": [-1, 34],
        "irrigation": {"الإنبات": 2.8, "الخضري": 4.8, "الاستطالة": 5.8, "التسنبل": 6.8, "النضج": 1.8},
        "carences_sensibles": ["N", "P"], "excès_sensibles": ["N"],
    },
    "شعير": {
        "categorie": "Céréale", "cycle_jours": 150,
        "stades": {
            "الإنبات": {"duree": 12, "N": 20, "P": 35, "K": 25, "Ca": 8, "Mg": 4, "S": 2},
            "الخضري": {"duree": 45, "N": 60, "P": 30, "K": 45, "Ca": 12, "Mg": 7, "S": 4},
            "الاستطالة": {"duree": 25, "N": 50, "P": 20, "K": 40, "Ca": 10, "Mg": 6, "S": 3},
            "التسنبل": {"duree": 35, "N": 40, "P": 18, "K": 45, "Ca": 7, "Mg": 4, "S": 2},
            "النضج": {"duree": 33, "N": 8, "P": 12, "K": 18, "Ca": 4, "Mg": 2, "S": 1},
        },
        "temperature_optimale": [10, 28], "temperature_critique": [-2, 38],
        "irrigation": {"الإنبات": 2.5, "الخضري": 4.5, "الاستطالة": 5.5, "التسنبل": 6.5, "النضج": 1.5},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["K"],
    },
    "ذرة": {
        "categorie": "Céréale", "cycle_jours": 110,
        "stades": {
            "الإنبات": {"duree": 10, "N": 22, "P": 38, "K": 32, "Ca": 10, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 40, "N": 75, "P": 40, "K": 65, "Ca": 18, "Mg": 12, "S": 8},
            "الازهار": {"duree": 20, "N": 55, "P": 35, "K": 70, "Ca": 20, "Mg": 14, "S": 9},
            "امتلاء الحبوب": {"duree": 40, "N": 30, "P": 25, "K": 45, "Ca": 12, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [20, 35], "temperature_critique": [8, 42],
        "irrigation": {"الإنبات": 3.5, "النمو الخضري": 6.5, "الازهار": 8, "امتلاء الحبوب": 5},
        "carences_sensibles": ["N", "K"], "excès_sensibles": ["N"],
    },
    "سرغو": {
        "categorie": "Céréale", "cycle_jours": 100,
        "stades": {
            "الإنبات": {"duree": 9, "N": 18, "P": 32, "K": 28, "Ca": 8, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 38, "N": 65, "P": 35, "K": 58, "Ca": 15, "Mg": 10, "S": 7},
            "الازهار": {"duree": 18, "N": 48, "P": 30, "K": 62, "Ca": 17, "Mg": 12, "S": 8},
            "النضج": {"duree": 35, "N": 25, "P": 22, "K": 40, "Ca": 10, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [22, 38], "temperature_critique": [10, 45],
        "irrigation": {"الإنبات": 3, "النمو الخضري": 6, "الازهار": 7.5, "النضج": 4.5},
        "carences_sensibles": ["N", "P"], "excès_sensibles": ["K"],
    },
    "شوفان": {
        "categorie": "Céréale", "cycle_jours": 140,
        "stades": {
            "الإنبات": {"duree": 13, "N": 21, "P": 36, "K": 26, "Ca": 9, "Mg": 5, "S": 3},
            "الخضري": {"duree": 48, "N": 62, "P": 32, "K": 47, "Ca": 13, "Mg": 8, "S": 5},
            "الاستطالة": {"duree": 26, "N": 52, "P": 22, "K": 42, "Ca": 11, "Mg": 7, "S": 4},
            "التسنبل": {"duree": 32, "N": 41, "P": 19, "K": 46, "Ca": 8, "Mg": 5, "S": 3},
            "النضج": {"duree": 21, "N": 9, "P": 13, "K": 19, "Ca": 5, "Mg": 3, "S": 2},
        },
        "temperature_optimale": [10, 26], "temperature_critique": [-3, 36],
        "irrigation": {"الإنبات": 2.6, "الخضري": 4.6, "الاستطالة": 5.6, "التسنبل": 6.6, "النضج": 1.6},
        "carences_sensibles": ["N", "K"], "excès_sensibles": ["N"],
    },

    # ============================================================
    # 🥦 الخضروات (Légumes)
    # ============================================================
    "طماطم": {
        "categorie": "Légume", "cycle_jours": 120,
        "stades": {
            "الشتلات": {"duree": 25, "N": 30, "P": 50, "K": 40, "Ca": 15, "Mg": 8, "S": 5},
            "النمو الخضري": {"duree": 35, "N": 65, "P": 35, "K": 55, "Ca": 20, "Mg": 10, "S": 7},
            "الازهار": {"duree": 20, "N": 45, "P": 45, "K": 60, "Ca": 25, "Mg": 12, "S": 8},
            "الاثمار": {"duree": 40, "N": 40, "P": 35, "K": 75, "Ca": 30, "Mg": 15, "S": 10},
        },
        "temperature_optimale": [18, 30], "temperature_critique": [8, 40],
        "irrigation": {"الشتلات": 4, "النمو الخضري": 6, "الازهار": 7, "الاثمار": 8},
        "carences_sensibles": ["Ca", "K"], "excès_sensibles": ["N"],
    },
    "بطاطس": {
        "categorie": "Légume", "cycle_jours": 100,
        "stades": {
            "الإنبات": {"duree": 20, "N": 25, "P": 45, "K": 40, "Ca": 12, "Mg": 7, "S": 4},
            "النمو الخضري": {"duree": 30, "N": 55, "P": 30, "K": 50, "Ca": 18, "Mg": 10, "S": 6},
            "تكوين الدرنات": {"duree": 30, "N": 35, "P": 35, "K": 70, "Ca": 20, "Mg": 12, "S": 8},
            "النضج": {"duree": 20, "N": 10, "P": 15, "K": 25, "Ca": 8, "Mg": 5, "S": 3},
        },
        "temperature_optimale": [15, 25], "temperature_critique": [5, 35],
        "irrigation": {"الإنبات": 3.5, "النمو الخضري": 5.5, "تكوين الدرنات": 7, "النضج": 2.5},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["N"],
    },
    "بصل": {
        "categorie": "Légume", "cycle_jours": 130,
        "stades": {
            "الإنبات": {"duree": 18, "N": 22, "P": 42, "K": 35, "Ca": 11, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 45, "N": 58, "P": 38, "K": 52, "Ca": 16, "Mg": 9, "S": 6},
            "تكوين البصلة": {"duree": 35, "N": 42, "P": 35, "K": 65, "Ca": 19, "Mg": 11, "S": 7},
            "النضج": {"duree": 32, "N": 12, "P": 18, "K": 28, "Ca": 9, "Mg": 5, "S": 3},
        },
        "temperature_optimale": [13, 28], "temperature_critique": [2, 38],
        "irrigation": {"الإنبات": 3.2, "النمو الخضري": 5.2, "تكوين البصلة": 6.5, "النضج": 2},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },
    "ثوم": {
        "categorie": "Légume", "cycle_jours": 150,
        "stades": {
            "الإنبات": {"duree": 20, "N": 18, "P": 38, "K": 32, "Ca": 10, "Mg": 5, "S": 6},
            "النمو الخضري": {"duree": 50, "N": 52, "P": 35, "K": 48, "Ca": 14, "Mg": 8, "S": 8},
            "تكوين الرؤوس": {"duree": 45, "N": 38, "P": 32, "K": 58, "Ca": 17, "Mg": 10, "S": 10},
            "النضج": {"duree": 35, "N": 10, "P": 15, "K": 25, "Ca": 8, "Mg": 4, "S": 5},
        },
        "temperature_optimale": [12, 26], "temperature_critique": [0, 35],
        "irrigation": {"الإنبات": 3, "النمو الخضري": 5, "تكوين الرؤوس": 6, "النضج": 1.5},
        "carences_sensibles": ["S", "K"], "excès_sensibles": ["N"],
    },
    "فلفل": {
        "categorie": "Légume", "cycle_jours": 100,
        "stades": {
            "الشتلات": {"duree": 25, "N": 28, "P": 42, "K": 38, "Ca": 14, "Mg": 7, "S": 4},
            "النمو الخضري": {"duree": 30, "N": 58, "P": 38, "K": 52, "Ca": 19, "Mg": 10, "S": 6},
            "الازهار": {"duree": 18, "N": 48, "P": 42, "K": 58, "Ca": 23, "Mg": 12, "S": 7},
            "الاثمار": {"duree": 27, "N": 42, "P": 38, "K": 68, "Ca": 26, "Mg": 14, "S": 9},
        },
        "temperature_optimale": [20, 33], "temperature_critique": [10, 40],
        "irrigation": {"الشتلات": 3.5, "النمو الخضري": 5.5, "الازهار": 6.5, "الاثمار": 7.5},
        "carences_sensibles": ["Ca", "K"], "excès_sensibles": ["N"],
    },
    "كوسة": {
        "categorie": "Légume", "cycle_jours": 90,
        "stades": {
            "الإنبات": {"duree": 10, "N": 20, "P": 35, "K": 30, "Ca": 10, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 30, "N": 50, "P": 30, "K": 45, "Ca": 15, "Mg": 8, "S": 5},
            "الازهار": {"duree": 15, "N": 40, "P": 35, "K": 50, "Ca": 18, "Mg": 10, "S": 6},
            "الاثمار": {"duree": 35, "N": 35, "P": 30, "K": 60, "Ca": 20, "Mg": 12, "S": 8},
        },
        "temperature_optimale": [20, 32], "temperature_critique": [10, 40],
        "irrigation": {"الإنبات": 3, "النمو الخضري": 5, "الازهار": 6, "الاثمار": 7},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },
    "باذنجان": {
        "categorie": "Légume", "cycle_jours": 110,
        "stades": {
            "الشتلات": {"duree": 25, "N": 25, "P": 40, "K": 35, "Ca": 12, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 35, "N": 55, "P": 35, "K": 50, "Ca": 18, "Mg": 9, "S": 6},
            "الازهار": {"duree": 20, "N": 45, "P": 40, "K": 55, "Ca": 22, "Mg": 11, "S": 7},
            "الاثمار": {"duree": 30, "N": 40, "P": 35, "K": 65, "Ca": 25, "Mg": 13, "S": 9},
        },
        "temperature_optimale": [22, 35], "temperature_critique": [12, 42],
        "irrigation": {"الشتلات": 4, "النمو الخضري": 6, "الازهار": 7, "الاثمار": 8},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["N"],
    },
    "جزر": {
        "categorie": "Légume", "cycle_jours": 100,
        "stades": {
            "الإنبات": {"duree": 15, "N": 18, "P": 40, "K": 35, "Ca": 10, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 35, "N": 48, "P": 35, "K": 48, "Ca": 14, "Mg": 8, "S": 5},
            "تكوين الجذور": {"duree": 35, "N": 32, "P": 30, "K": 62, "Ca": 16, "Mg": 10, "S": 6},
            "النضج": {"duree": 15, "N": 8, "P": 12, "K": 22, "Ca": 7, "Mg": 4, "S": 2},
        },
        "temperature_optimale": [15, 24], "temperature_critique": [4, 32],
        "irrigation": {"الإنبات": 3, "النمو الخضري": 5, "تكوين الجذور": 6.5, "النضج": 2.5},
        "carences_sensibles": ["K", "B"], "excès_sensibles": ["N"],
    },
    "خس": {
        "categorie": "Légume", "cycle_jours": 60,
        "stades": {
            "الإنبات": {"duree": 8, "N": 15, "P": 28, "K": 25, "Ca": 8, "Mg": 4, "S": 2},
            "النمو الخضري": {"duree": 35, "N": 45, "P": 30, "K": 42, "Ca": 12, "Mg": 7, "S": 4},
            "تكوين الرأس": {"duree": 17, "N": 28, "P": 22, "K": 38, "Ca": 10, "Mg": 6, "S": 3},
        },
        "temperature_optimale": [12, 22], "temperature_critique": [2, 30],
        "irrigation": {"الإنبات": 2.5, "النمو الخضري": 4.5, "تكوين الرأس": 5.5},
        "carences_sensibles": ["N", "Ca"], "excès_sensibles": ["N"],
    },
    "بطيخ": {
        "categorie": "Légume", "cycle_jours": 90,
        "stades": {
            "الإنبات": {"duree": 10, "N": 20, "P": 35, "K": 32, "Ca": 10, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 30, "N": 52, "P": 35, "K": 55, "Ca": 16, "Mg": 9, "S": 6},
            "الازهار": {"duree": 15, "N": 42, "P": 38, "K": 62, "Ca": 19, "Mg": 11, "S": 7},
            "نمو الثمار": {"duree": 35, "N": 38, "P": 32, "K": 72, "Ca": 22, "Mg": 13, "S": 9},
        },
        "temperature_optimale": [22, 35], "temperature_critique": [12, 42],
        "irrigation": {"الإنبات": 3.5, "النمو الخضري": 6, "الازهار": 7.5, "نمو الثمار": 8.5},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["N"],
    },
    "قرع": {
        "categorie": "Légume", "cycle_jours": 95,
        "stades": {
            "الإنبات": {"duree": 10, "N": 19, "P": 34, "K": 31, "Ca": 10, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 32, "N": 50, "P": 34, "K": 53, "Ca": 15, "Mg": 9, "S": 6},
            "الازهار": {"duree": 16, "N": 41, "P": 37, "K": 60, "Ca": 18, "Mg": 11, "S": 7},
            "نمو الثمار": {"duree": 37, "N": 37, "P": 31, "K": 70, "Ca": 21, "Mg": 13, "S": 9},
        },
        "temperature_optimale": [20, 34], "temperature_critique": [10, 41],
        "irrigation": {"الإنبات": 3.3, "النمو الخضري": 5.8, "الازهار": 7.2, "نمو الثمار": 8.2},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },
    "فلفل حار": {
        "categorie": "Légume", "cycle_jours": 105,
        "stades": {
            "الشتلات": {"duree": 26, "N": 27, "P": 41, "K": 37, "Ca": 13, "Mg": 7, "S": 4},
            "النمو الخضري": {"duree": 32, "N": 57, "P": 37, "K": 51, "Ca": 18, "Mg": 10, "S": 6},
            "الازهار": {"duree": 19, "N": 47, "P": 41, "K": 57, "Ca": 22, "Mg": 12, "S": 7},
            "الاثمار": {"duree": 28, "N": 41, "P": 37, "K": 67, "Ca": 25, "Mg": 14, "S": 9},
        },
        "temperature_optimale": [21, 34], "temperature_critique": [11, 41],
        "irrigation": {"الشتلات": 3.6, "النمو الخضري": 5.6, "الازهار": 6.6, "الاثمار": 7.6},
        "carences_sensibles": ["Ca", "K"], "excès_sensibles": ["N"],
    },
    "لفت": {
        "categorie": "Légume", "cycle_jours": 70,
        "stades": {
            "الإنبات": {"duree": 7, "N": 16, "P": 30, "K": 27, "Ca": 9, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 32, "N": 44, "P": 32, "K": 44, "Ca": 13, "Mg": 7, "S": 5},
            "تكوين الجذر": {"duree": 31, "N": 30, "P": 28, "K": 56, "Ca": 15, "Mg": 9, "S": 6},
        },
        "temperature_optimale": [10, 22], "temperature_critique": [0, 32],
        "irrigation": {"الإنبات": 2.4, "النمو الخضري": 4.4, "تكوين الجذر": 5.8},
        "carences_sensibles": ["K", "B"], "excès_sensibles": ["N"],
    },
    "خرشوف": {
        "categorie": "Légume", "cycle_jours": 180,
        "stades": {
            "النمو الخضري": {"duree": 60, "N": 35, "P": 45, "K": 48, "Ca": 16, "Mg": 9, "S": 6},
            "تكوين البراعم": {"duree": 50, "N": 52, "P": 42, "K": 62, "Ca": 22, "Mg": 13, "S": 8},
            "النضج": {"duree": 40, "N": 38, "P": 35, "K": 55, "Ca": 19, "Mg": 11, "S": 7},
            "الحصاد": {"duree": 30, "N": 15, "P": 20, "K": 32, "Ca": 11, "Mg": 6, "S": 4},
        },
        "temperature_optimale": [14, 26], "temperature_critique": [2, 35],
        "irrigation": {"النمو الخضري": 4.5, "تكوين البراعم": 6.5, "النضج": 5.5, "الحصاد": 3.5},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },

    # ============================================================
    # 🫘 البقوليات (Légumineuses)
    # ============================================================
    "حمص": {
        "categorie": "Légumineuse", "cycle_jours": 110,
        "stades": {
            "الإنبات": {"duree": 12, "N": 15, "P": 35, "K": 28, "Ca": 10, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 40, "N": 38, "P": 42, "K": 45, "Ca": 15, "Mg": 8, "S": 5},
            "الازهار": {"duree": 25, "N": 32, "P": 48, "K": 52, "Ca": 18, "Mg": 10, "S": 6},
            "امتلاء القرون": {"duree": 33, "N": 22, "P": 35, "K": 42, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [18, 30], "temperature_critique": [5, 38],
        "irrigation": {"الإنبات": 2.8, "النمو الخضري": 4.2, "الازهار": 5.5, "امتلاء القرون": 4},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },
    "عدس": {
        "categorie": "Légumineuse", "cycle_jours": 100,
        "stades": {
            "الإنبات": {"duree": 10, "N": 14, "P": 32, "K": 26, "Ca": 9, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 38, "N": 36, "P": 40, "K": 43, "Ca": 14, "Mg": 8, "S": 5},
            "الازهار": {"duree": 22, "N": 30, "P": 46, "K": 50, "Ca": 17, "Mg": 10, "S": 6},
            "امتلاء القرون": {"duree": 30, "N": 20, "P": 33, "K": 40, "Ca": 13, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [16, 28], "temperature_critique": [3, 36],
        "irrigation": {"الإنبات": 2.6, "النمو الخضري": 4, "الازهار": 5.2, "امتلاء القرون": 3.8},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },
    "فول": {
        "categorie": "Légumineuse", "cycle_jours": 120,
        "stades": {
            "الإنبات": {"duree": 14, "N": 16, "P": 36, "K": 30, "Ca": 11, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 42, "N": 40, "P": 44, "K": 47, "Ca": 16, "Mg": 9, "S": 6},
            "الازهار": {"duree": 28, "N": 34, "P": 50, "K": 54, "Ca": 19, "Mg": 11, "S": 7},
            "امتلاء القرون": {"duree": 36, "N": 24, "P": 37, "K": 44, "Ca": 15, "Mg": 9, "S": 5},
        },
        "temperature_optimale": [15, 26], "temperature_critique": [2, 35],
        "irrigation": {"الإنبات": 3, "النمو الخضري": 4.5, "الازهار": 5.8, "امتلاء القرون": 4.2},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },
    "فاصوليا خضراء": {
        "categorie": "Légumineuse", "cycle_jours": 75,
        "stades": {
            "الإنبات": {"duree": 9, "N": 13, "P": 30, "K": 25, "Ca": 9, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 28, "N": 34, "P": 38, "K": 41, "Ca": 13, "Mg": 7, "S": 5},
            "الازهار": {"duree": 15, "N": 28, "P": 42, "K": 46, "Ca": 16, "Mg": 9, "S": 6},
            "تكوين القرون": {"duree": 23, "N": 20, "P": 32, "K": 38, "Ca": 12, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [18, 30], "temperature_critique": [8, 38],
        "irrigation": {"الإنبات": 2.5, "النمو الخضري": 4, "الازهار": 5, "تكوين القرون": 4.5},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },
    "بازلاء": {
        "categorie": "Légumineuse", "cycle_jours": 90,
        "stades": {
            "الإنبات": {"duree": 11, "N": 14, "P": 33, "K": 27, "Ca": 10, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 35, "N": 37, "P": 41, "K": 44, "Ca": 14, "Mg": 8, "S": 5},
            "الازهار": {"duree": 20, "N": 31, "P": 45, "K": 49, "Ca": 17, "Mg": 10, "S": 6},
            "امتلاء القرون": {"duree": 24, "N": 21, "P": 34, "K": 41, "Ca": 13, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [14, 24], "temperature_critique": [1, 32],
        "irrigation": {"الإنبات": 2.7, "النمو الخضري": 4.3, "الازهار": 5.4, "امتلاء القرون": 4},
        "carences_sensibles": ["P", "K"], "excès_sensibles": ["N"],
    },

    # ============================================================
    # 🌳 الأشجار المثمرة (Arbres fruitiers)
    # ============================================================
    "زيتون": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 90, "N": 20, "P": 30, "K": 35, "Ca": 10, "Mg": 5, "S": 3},
            "إزهار": {"duree": 45, "N": 35, "P": 45, "K": 50, "Ca": 15, "Mg": 8, "S": 5},
            "نمو الثمار": {"duree": 120, "N": 40, "P": 35, "K": 60, "Ca": 20, "Mg": 10, "S": 7},
            "نضج": {"duree": 110, "N": 15, "P": 20, "K": 25, "Ca": 10, "Mg": 5, "S": 3},
        },
        "temperature_optimale": [10, 35], "temperature_critique": [-5, 45],
        "irrigation": {"سكون شتوي": 1, "إزهار": 3, "نمو الثمار": 5, "نضج": 2},
        "carences_sensibles": ["B", "K"], "excès_sensibles": ["Na"],
    },
    "نخيل التمر": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 60, "N": 18, "P": 28, "K": 42, "Ca": 12, "Mg": 6, "S": 4},
            "طلع": {"duree": 45, "N": 32, "P": 42, "K": 55, "Ca": 16, "Mg": 9, "S": 6},
            "حبابوك": {"duree": 50, "N": 38, "P": 38, "K": 62, "Ca": 19, "Mg": 11, "S": 7},
            "بسر": {"duree": 60, "N": 35, "P": 35, "K": 68, "Ca": 21, "Mg": 12, "S": 8},
            "رطب/تمر": {"duree": 150, "N": 22, "P": 28, "K": 52, "Ca": 17, "Mg": 10, "S": 6},
        },
        "temperature_optimale": [25, 40], "temperature_critique": [5, 50],
        "irrigation": {"سكون شتوي": 2, "طلع": 4, "حبابوك": 6, "بسر": 7, "رطب/تمر": 5},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["Cl"],
    },
    "تين": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 70, "N": 16, "P": 26, "K": 32, "Ca": 11, "Mg": 6, "S": 3},
            "إزهار": {"duree": 40, "N": 30, "P": 38, "K": 45, "Ca": 14, "Mg": 8, "S": 5},
            "نمو الثمار": {"duree": 90, "N": 35, "P": 32, "K": 52, "Ca": 17, "Mg": 10, "S": 6},
            "النضج": {"duree": 165, "N": 18, "P": 24, "K": 38, "Ca": 13, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [18, 35], "temperature_critique": [-8, 42],
        "irrigation": {"سكون شتوي": 1.5, "إزهار": 3.5, "نمو الثمار": 5.5, "النضج": 3},
        "carences_sensibles": ["K", "B"], "excès_sensibles": ["N"],
    },
    "رمان": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 75, "N": 19, "P": 29, "K": 36, "Ca": 12, "Mg": 6, "S": 4},
            "إزهار": {"duree": 45, "N": 34, "P": 42, "K": 48, "Ca": 15, "Mg": 9, "S": 5},
            "نمو الثمار": {"duree": 110, "N": 38, "P": 36, "K": 58, "Ca": 19, "Mg": 11, "S": 7},
            "النضج": {"duree": 135, "N": 20, "P": 26, "K": 42, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [20, 38], "temperature_critique": [-5, 45],
        "irrigation": {"سكون شتوي": 1.8, "إزهار": 3.8, "نمو الثمار": 6, "النضج": 3.5},
        "carences_sensibles": ["K", "Zn"], "excès_sensibles": ["N"],
    },
    "كرمة": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 80, "N": 17, "P": 27, "K": 38, "Ca": 11, "Mg": 6, "S": 4},
            "إزهار": {"duree": 40, "N": 32, "P": 40, "K": 50, "Ca": 14, "Mg": 8, "S": 5},
            "عقد الثمار": {"duree": 50, "N": 36, "P": 36, "K": 56, "Ca": 17, "Mg": 10, "S": 6},
            "نمو الثمار": {"duree": 70, "N": 33, "P": 33, "K": 62, "Ca": 19, "Mg": 11, "S": 7},
            "النضج": {"duree": 125, "N": 19, "P": 25, "K": 44, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [18, 32], "temperature_critique": [-10, 40],
        "irrigation": {"سكون شتوي": 1.2, "إزهار": 3.2, "عقد الثمار": 4.8, "نمو الثمار": 5.5, "النضج": 2.5},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["N"],
    },
    "لوز": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 85, "N": 18, "P": 28, "K": 34, "Ca": 11, "Mg": 6, "S": 4},
            "إزهار": {"duree": 35, "N": 33, "P": 41, "K": 46, "Ca": 14, "Mg": 8, "S": 5},
            "نمو الثمار": {"duree": 100, "N": 37, "P": 34, "K": 54, "Ca": 18, "Mg": 10, "S": 6},
            "النضج": {"duree": 145, "N": 19, "P": 25, "K": 40, "Ca": 13, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [15, 32], "temperature_critique": [-8, 42],
        "irrigation": {"سكون شتوي": 1.5, "إزهار": 3.5, "نمو الثمار": 5.5, "النضج": 3},
        "carences_sensibles": ["Zn", "B"], "excès_sensibles": ["N"],
    },
    "مشمش": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 90, "N": 19, "P": 30, "K": 35, "Ca": 12, "Mg": 6, "S": 4},
            "إزهار": {"duree": 30, "N": 34, "P": 43, "K": 47, "Ca": 15, "Mg": 9, "S": 5},
            "نمو الثمار": {"duree": 70, "N": 38, "P": 36, "K": 55, "Ca": 18, "Mg": 11, "S": 7},
            "النضج": {"duree": 175, "N": 20, "P": 26, "K": 41, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [16, 30], "temperature_critique": [-12, 40],
        "irrigation": {"سكون شتوي": 1.6, "إزهار": 3.6, "نمو الثمار": 5.6, "النضج": 3.2},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },
    "خوخ": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 85, "N": 20, "P": 31, "K": 36, "Ca": 12, "Mg": 7, "S": 4},
            "إزهار": {"duree": 32, "N": 35, "P": 44, "K": 48, "Ca": 15, "Mg": 9, "S": 5},
            "نمو الثمار": {"duree": 75, "N": 39, "P": 37, "K": 56, "Ca": 19, "Mg": 11, "S": 7},
            "النضج": {"duree": 173, "N": 21, "P": 27, "K": 42, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [17, 31], "temperature_critique": [-10, 41],
        "irrigation": {"سكون شتوي": 1.7, "إزهار": 3.7, "نمو الثمار": 5.7, "النضج": 3.3},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },
    "برقوق": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 88, "N": 19, "P": 30, "K": 35, "Ca": 12, "Mg": 6, "S": 4},
            "إزهار": {"duree": 31, "N": 34, "P": 43, "K": 47, "Ca": 15, "Mg": 9, "S": 5},
            "نمو الثمار": {"duree": 72, "N": 38, "P": 36, "K": 55, "Ca": 18, "Mg": 11, "S": 7},
            "النضج": {"duree": 174, "N": 20, "P": 26, "K": 41, "Ca": 14, "Mg": 8, "S": 5},
        },
        "temperature_optimale": [16, 30], "temperature_critique": [-11, 40],
        "irrigation": {"سكون شتوي": 1.6, "إزهار": 3.6, "نمو الثمار": 5.6, "النضج": 3.2},
        "carences_sensibles": ["K", "Ca"], "excès_sensibles": ["N"],
    },
    "كرز": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 92, "N": 18, "P": 29, "K": 34, "Ca": 11, "Mg": 6, "S": 4},
            "إزهار": {"duree": 28, "N": 33, "P": 42, "K": 46, "Ca": 14, "Mg": 8, "S": 5},
            "نمو الثمار": {"duree": 65, "N": 37, "P": 35, "K": 54, "Ca": 18, "Mg": 10, "S": 6},
            "النضج": {"duree": 180, "N": 19, "P": 25, "K": 40, "Ca": 13, "Mg": 7, "S": 4},
        },
        "temperature_optimale": [14, 28], "temperature_critique": [-15, 38],
        "irrigation": {"سكون شتوي": 1.4, "إزهار": 3.4, "نمو الثمار": 5.4, "النضج": 3},
        "carences_sensibles": ["Ca", "B"], "excès_sensibles": ["N"],
    },
    "حمضيات (برتقال)": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 60, "N": 22, "P": 32, "K": 40, "Ca": 13, "Mg": 7, "S": 5},
            "إزهار": {"duree": 40, "N": 38, "P": 46, "K": 52, "Ca": 17, "Mg": 10, "S": 6},
            "عقد الثمار": {"duree": 50, "N": 42, "P": 40, "K": 58, "Ca": 20, "Mg": 12, "S": 7},
            "نمو الثمار": {"duree": 120, "N": 40, "P": 38, "K": 65, "Ca": 22, "Mg": 13, "S": 8},
            "النضج": {"duree": 95, "N": 24, "P": 30, "K": 48, "Ca": 16, "Mg": 9, "S": 6},
        },
        "temperature_optimale": [18, 32], "temperature_critique": [-2, 42],
        "irrigation": {"سكون شتوي": 2, "إزهار": 4, "عقد الثمار": 5.5, "نمو الثمار": 6.5, "النضج": 4},
        "carences_sensibles": ["Zn", "Fe", "Mg"], "excès_sensibles": ["Cl"],
    },
    "ليمون": {
        "categorie": "Arbre fruitier", "cycle_jours": 365,
        "stades": {
            "سكون شتوي": {"duree": 55, "N": 21, "P": 31, "K": 39, "Ca": 13, "Mg": 7, "S": 5},
            "إزهار": {"duree": 42, "N": 37, "P": 45, "K": 51, "Ca": 17, "Mg": 10, "S": 6},
            "عقد الثمار": {"duree": 48, "N": 41, "P": 39, "K": 57, "Ca": 19, "Mg": 11, "S": 7},
            "نمو الثمار": {"duree": 115, "N": 39, "P": 37, "K": 64, "Ca": 21, "Mg": 12, "S": 8},
            "النضج": {"duree": 105, "N": 23, "P": 29, "K": 47, "Ca": 15, "Mg": 9, "S": 6},
        },
        "temperature_optimale": [19, 33], "temperature_critique": [-1, 43],
        "irrigation": {"سكون شتوي": 2.1, "إزهار": 4.1, "عقد الثمار": 5.6, "نمو الثمار": 6.6, "النضج": 4.1},
        "carences_sensibles": ["Zn", "Fe", "Mg"], "excès_sensibles": ["Cl"],
    },

    # ============================================================
    # 🏭 الصناعية (Cultures industrielles)
    # ============================================================
    "عباد الشمس": {
        "categorie": "Industrielle", "cycle_jours": 110,
        "stades": {
            "الإنبات": {"duree": 12, "N": 20, "P": 38, "K": 35, "Ca": 11, "Mg": 6, "S": 4},
            "النمو الخضري": {"duree": 42, "N": 55, "P": 40, "K": 52, "Ca": 16, "Mg": 10, "S": 7},
            "الازهار": {"duree": 22, "N": 45, "P": 42, "K": 58, "Ca": 19, "Mg": 12, "S": 8},
            "امتلاء البذور": {"duree": 34, "N": 30, "P": 32, "K": 48, "Ca": 14, "Mg": 9, "S": 6},
        },
        "temperature_optimale": [20, 32], "temperature_critique": [6, 40],
        "irrigation": {"الإنبات": 3.2, "النمو الخضري": 5.5, "الازهار": 7, "امتلاء البذور": 5},
        "carences_sensibles": ["B", "K"], "excès_sensibles": ["N"],
    },
    "شمندر السكر": {
        "categorie": "Industrielle", "cycle_jours": 160,
        "stades": {
            "الإنبات": {"duree": 18, "N": 22, "P": 42, "K": 45, "Ca": 14, "Mg": 8, "S": 5},
            "النمو الخضري": {"duree": 55, "N": 58, "P": 45, "K": 62, "Ca": 20, "Mg": 12, "S": 8},
            "تكوين الجذور": {"duree": 50, "N": 42, "P": 40, "K": 72, "Ca": 24, "Mg": 15, "S": 10},
            "تراكم السكر": {"duree": 37, "N": 25, "P": 32, "K": 55, "Ca": 18, "Mg": 11, "S": 7},
        },
        "temperature_optimale": [15, 25], "temperature_critique": [2, 35],
        "irrigation": {"الإنبات": 3.5, "النمو الخضري": 5.8, "تكوين الجذور": 7.2, "تراكم السكر": 4.5},
        "carences_sensibles": ["B", "K"], "excès_sensibles": ["N"],
    },
    "قطن": {
        "categorie": "Industrielle", "cycle_jours": 140,
        "stades": {
            "الإنبات": {"duree": 14, "N": 24, "P": 40, "K": 38, "Ca": 12, "Mg": 7, "S": 5},
            "النمو الخضري": {"duree": 48, "N": 62, "P": 42, "K": 58, "Ca": 18, "Mg": 11, "S": 8},
            "الازهار": {"duree": 30, "N": 52, "P": 45, "K": 68, "Ca": 22, "Mg": 14, "S": 9},
            "تكوين اللوز": {"duree": 48, "N": 38, "P": 38, "K": 62, "Ca": 19, "Mg": 12, "S": 8},
        },
        "temperature_optimale": [22, 36], "temperature_critique": [12, 44],
        "irrigation": {"الإنبات": 3.4, "النمو الخضري": 6, "الازهار": 7.5, "تكوين اللوز": 6.5},
        "carences_sensibles": ["K", "Zn"], "excès_sensibles": ["N"],
    },
    "تبغ": {
        "categorie": "Industrielle", "cycle_jours": 100,
        "stades": {
            "الشتلات": {"duree": 25, "N": 18, "P": 32, "K": 28, "Ca": 10, "Mg": 5, "S": 3},
            "النمو الخضري": {"duree": 35, "N": 48, "P": 38, "K": 45, "Ca": 15, "Mg": 9, "S": 6},
            "النضج": {"duree": 40, "N": 35, "P": 32, "K": 52, "Ca": 18, "Mg": 11, "S": 7},
        },
        "temperature_optimale": [20, 30], "temperature_critique": [10, 38],
        "irrigation": {"الشتلات": 3, "النمو الخضري": 5.5, "النضج": 4.5},
        "carences_sensibles": ["K", "Mg"], "excès_sensibles": ["Cl"],
    },
}
# قاعدة بيانات الأسمدة
FERTILIZER_DATABASE = {
    "Urea": {"name": "اليوريا", "icon": "🍚", "composition": {"N": 46, "P": 0, "K": 0}, "how": "نثر أو حقن", "when": "مراحل النمو الخضري"},
    "TSP": {"name": "سوبر فوسفات ثلاثي", "icon": "🦴", "composition": {"N": 0, "P": 46, "K": 0}, "how": "خلط مع التربة", "when": "قبل الزراعة أو عند الإنبات"},
    "Sulfate Potasse": {"name": "كبريتات البوتاسيوم", "icon": "🧂", "composition": {"N": 0, "P": 0, "K": 50}, "how": "نثر أو ري", "when": "مراحل الإزهار والإثمار"},
    "Nitrate Calcium": {"name": "نترات الكالسيوم", "icon": "🥛", "composition": {"N": 15.5, "Ca": 26}, "how": "ري أو رش ورقي", "when": "مراحل النمو الحرجة"},
    "Sulfate Magnésium": {"name": "كبريتات المغنيسيوم", "icon": "🧪", "composition": {"Mg": 16, "S": 13}, "how": "ري أو رش ورقي", "when": "عند ظهور أعراض النقص"},
    "DAP": {"name": "فوسفات ثنائي الأمونيوم", "icon": "🍚🦴", "composition": {"N": 18, "P": 46, "K": 0}, "how": "خلط مع التربة", "when": "قبل الزراعة"},
    "NPK_20_20_20": {"name": "سماد مركب NPK (20-20-20)", "icon": "🌱", "composition": {"N": 20, "P": 20, "K": 20}, "how": "ري أو رش ورقي", "when": "مراحل النمو العامة"},
}

# حدود النقص والزيادة
SEUILS_EXCES = {
    "N": {"max": 300, "message": "Excès d'azote → Risque verse, nitrates, pollution nappe"},
    "P": {"max": 100, "message": "Excès de phosphore → Blocage Zn/Fe, eutrophisation"},
    "K": {"max": 300, "message": "Excès de potassium → Blocage Ca/Mg, déséquilibre cations"},
    "ratio_NK": {"min": 0.5, "max": 2.0, "message": "Ratio N/K déséquilibré → Ajuster fertilisation"},
    "ratio_PK": {"min": 0.2, "max": 1.0, "message": "Ratio P/K anormal → Vérifier disponibilité"},
    "ratio_CaMg": {"min": 3.0, "max": 8.0, "message": "Ratio Ca/Mg déséquilibré → Problème structure sol"},
    "Ca": {"max": 5000, "message": "Excès de calcium → Blocage P, Mg, K"},
    "Mg": {"max": 800, "message": "Excès de magnésium → Blocage Ca, K"},
    "S": {"max": 50, "message": "Excès de soufre → Acidification sol, toxicité"},
    "Fe": {"max": 50, "message": "Excès de fer → Toxicité, blocage Mn, Zn"},
    "Zn": {"max": 10, "message": "Excès de zinc → Toxicité, blocage Fe"},
    "B": {"max": 5, "message": "Excès de bore → Toxicité"},
    "Mn": {"max": 30, "message": "Excès de manganèse → Toxicité, blocage Fe"},
    "ph_acide": {"max": 6.0, "message": "pH acide → Fixation P, toxicité Al/Mn"},
    "ph_basique": {"min": 8.0, "message": "pH basique → Blocage P, Fe, Zn, Mn"},
    "mo_faible": {"max": 1.0, "message": "Matière organique faible → Faible rétention eau/nutriments"},
    "cec_faible": {"max": 10, "message": "CEC faible → Faible capacité échange cationique"},
}

# ============================================================
# دوال جلب بيانات الطقس الحقيقية
# ============================================================

def get_weather_data_openmeteo(lat, lon):
    """جلب بيانات الطقس من Open-Meteo API (مجاني، لا يحتاج مفتاح)"""
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,weathercode",
            "timezone": "auto",
            "forecast_days": 7
        }
        response = requests.get(OPENMETEO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        
        # حساب متوسط درجة الحرارة للأيام القادمة
        daily_temps = daily.get("temperature_2m_max", [])
        avg_temp = sum(daily_temps[:5]) / len(daily_temps[:5]) if daily_temps else current.get("temperature", 20)
        
        # حساب إجمالي الأمطار المتوقعة
        total_rain = sum(daily.get("precipitation_sum", [])[:7])
        
        return {
            "temperature": current.get("temperature", 20),
            "temperature_min": daily.get("temperature_2m_min", [20])[0] if daily.get("temperature_2m_min") else 15,
            "temperature_max": daily.get("temperature_2m_max", [25])[0] if daily.get("temperature_2m_max") else 25,
            "avg_temp_7days": round(avg_temp, 1),
            "precipitation": total_rain,
            "humidity": 65,  # Open-Meteo current doesn't provide humidity directly
            "wind_speed": current.get("windspeed", 10),
            "weather_code": current.get("weathercode", 0),
            "forecast_days": daily_temps,
            "source": "Open-Meteo"
        }
    except Exception as e:
        print(f"Error fetching OpenMeteo weather: {e}")
        return None


def get_weather_data_openweather(lat, lon):
    """جلب بيانات الطقس من OpenWeather API (يتطلب مفتاح API)"""
    if not OPENWEATHER_API_KEY:
        return None
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # جلب التوقعات للأيام القادمة
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_data = forecast_response.json() if forecast_response.status_code == 200 else None
        
        # حساب متوسط درجة الحرارة من التوقعات
        avg_temp = 20
        total_rain = 0
        if forecast_data and "list" in forecast_data:
            temps = [item["main"]["temp"] for item in forecast_data["list"][:8]]
            avg_temp = sum(temps) / len(temps) if temps else data["main"]["temp"]
            total_rain = sum(item.get("rain", {}).get("3h", 0) for item in forecast_data["list"][:8])
        
        return {
            "temperature": data["main"]["temp"],
            "temperature_min": data["main"]["temp_min"],
            "temperature_max": data["main"]["temp_max"],
            "avg_temp_7days": round(avg_temp, 1),
            "precipitation": total_rain,
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather_code": data["weather"][0]["id"] if data.get("weather") else 0,
            "source": "OpenWeather"
        }
    except Exception as e:
        print(f"Error fetching OpenWeather weather: {e}")
        return None


def get_weather_data(lat, lon):
    """الحصول على بيانات الطقس من المصدر المتاح"""
    # محاولة Open-Meteo أولاً (مجاني)
    weather = get_weather_data_openmeteo(lat, lon)
    
    # إذا فشل، جرب OpenWeather إذا كان المفتاح موجوداً
    if weather is None and OPENWEATHER_API_KEY:
        weather = get_weather_data_openweather(lat, lon)
    
    # إذا فشل كلاهما، أرجع بيانات افتراضية
    if weather is None:
        weather = {
            "temperature": 22,
            "temperature_min": 15,
            "temperature_max": 30,
            "avg_temp_7days": 22,
            "precipitation": 5,
            "humidity": 60,
            "wind_speed": 10,
            "source": "Default"
        }
    
    return weather


# ============================================================
# دوال التحليل والتوصية
# ============================================================

def detecter_exces_et_desequilibres(soil_data, stade_data, engrais_apportes):
    alertes_critiques = []
    avertissements = []
    conseils_correctifs = []
    niveau_risque = "Faible"

    # تحليل النسب
    n_val = soil_data.get("N", 0) + engrais_apportes.get("N", 0)
    p_val = soil_data.get("P", 0) + engrais_apportes.get("P", 0)
    k_val = soil_data.get("K", 0) + engrais_apportes.get("K", 0)
    ca_val = soil_data.get("Ca", 0) + engrais_apportes.get("Ca", 0)
    mg_val = soil_data.get("Mg", 0) + engrais_apportes.get("Mg", 0)

    if k_val > 0 and n_val > 0:
        ratio_nk = n_val / k_val
        if ratio_nk < SEUILS_EXCES["ratio_NK"]["min"] or ratio_nk > SEUILS_EXCES["ratio_NK"]["max"]:
            avertissements.append(SEUILS_EXCES["ratio_NK"]["message"])
            conseils_correctifs.append(f"Ajuster le ratio N/K. Valeur actuelle: {ratio_nk:.2f}.")
            niveau_risque = "Modéré"

    if k_val > 0 and p_val > 0:
        ratio_pk = p_val / k_val
        if ratio_pk < SEUILS_EXCES["ratio_PK"]["min"] or ratio_pk > SEUILS_EXCES["ratio_PK"]["max"]:
            avertissements.append(SEUILS_EXCES["ratio_PK"]["message"])
            conseils_correctifs.append(f"Ajuster le ratio P/K. Valeur actuelle: {ratio_pk:.2f}.")

    if mg_val > 0 and ca_val > 0:
        ratio_camg = ca_val / mg_val
        if ratio_camg < SEUILS_EXCES["ratio_CaMg"]["min"] or ratio_camg > SEUILS_EXCES["ratio_CaMg"]["max"]:
            avertissements.append(SEUILS_EXCES["ratio_CaMg"]["message"])

    # تحليل pH
    ph_sol = soil_data.get("ph", 7.0)
    if ph_sol < SEUILS_EXCES["ph_acide"]["max"]:
        alertes_critiques.append(SEUILS_EXCES["ph_acide"]["message"])
        conseils_correctifs.append("زيادة pH التربة (إضافة الجير).")
        niveau_risque = "Élevé"
    elif ph_sol > SEUILS_EXCES["ph_basique"]["min"]:
        alertes_critiques.append(SEUILS_EXCES["ph_basique"]["message"])
        conseils_correctifs.append("خفض pH التربة (إضافة الكبريت).")
        niveau_risque = "Élevé"

    # تحليل المادة العضوية
    mo_pct = soil_data.get("mo_pct", 0)
    if mo_pct < SEUILS_EXCES["mo_faible"]["max"]:
        avertissements.append(SEUILS_EXCES["mo_faible"]["message"])
        conseils_correctifs.append("زيادة المادة العضوية (سماد عضوي، كمبوست).")

    return {
        "alertes_critiques": alertes_critiques,
        "avertissements": avertissements,
        "conseils_correctifs": conseils_correctifs,
        "niveau_risque": niveau_risque
    }


def calculer_stade(date_plantation_str, culture_data):
    try:
        date_plantation = datetime.strptime(date_plantation_str, '%Y-%m-%d').date()
    except ValueError:
        return None
    
    today = date.today()
    jours_ecoules = (today - date_plantation).days

    if jours_ecoules < 0:
        return None

    stades = culture_data["stades"]
    cycle_jours = culture_data["cycle_jours"]

    jours_cumules = 0
    stade_actuel = None
    for nom_stade, info_stade in stades.items():
        jours_cumules += info_stade["duree"]
        if jours_ecoules <= jours_cumules:
            stade_actuel = nom_stade
            break
    
    if stade_actuel is None and jours_ecoules > cycle_jours:
        stade_actuel = list(stades.keys())[-1]

    if stade_actuel is None:
        return None

    progression = min(100, round((jours_ecoules / cycle_jours) * 100, 1))
    days_remaining = max(0, cycle_jours - jours_ecoules)

    return {
        "stade": stade_actuel,
        "jours_ecoules": jours_ecoules,
        "progression": progression,
        "days_remaining": days_remaining
    }


def get_fertilizer_recommendations(manques, area):
    recommended_fertilizers = []
    
    nutrient_deficits = {
        "N": manques["N"]["manque"],
        "P": manques["P"]["manque"],
        "K": manques["K"]["manque"],
    }
    
    sorted_deficits = sorted(nutrient_deficits.items(), key=lambda item: item[1], reverse=True)

    for nutrient, deficit_amount in sorted_deficits:
        if deficit_amount > 0:
            for fert_key, fert_data in FERTILIZER_DATABASE.items():
                if fert_data["composition"].get(nutrient, 0) > 0:
                    nutrient_percentage = fert_data["composition"][nutrient]
                    required_fert_kg_ha = (deficit_amount / nutrient_percentage) * 100 if nutrient_percentage > 0 else 0
                    
                    if required_fert_kg_ha > 0.1:
                        recommended_fertilizers.append({
                            "name": fert_data["name"],
                            "icon": fert_data["icon"],
                            "kgHa": round(required_fert_kg_ha, 1),
                            "how": fert_data["how"],
                            "when": fert_data["when"],
                            "composition": fert_data["composition"],
                        })
                        manques[nutrient]["manque"] = 0
                        break

    for nutrient in ["Ca", "Mg", "S"]:
        if manques.get(nutrient, {}).get("manque", 0) > 0:
            for fert_key, fert_data in FERTILIZER_DATABASE.items():
                if fert_data["composition"].get(nutrient, 0) > 0:
                    nutrient_percentage = fert_data["composition"][nutrient]
                    required_fert_kg_ha = (manques[nutrient]["manque"] / nutrient_percentage) * 100
                    if required_fert_kg_ha > 0.1:
                        found = False
                        for rec_fert in recommended_fertilizers:
                            if rec_fert["name"] == fert_data["name"]:
                                rec_fert["kgHa"] += round(required_fert_kg_ha, 1)
                                found = True
                                break
                        if not found:
                            recommended_fertilizers.append({
                                "name": fert_data["name"],
                                "icon": fert_data["icon"],
                                "kgHa": round(required_fert_kg_ha, 1),
                                "how": fert_data["how"],
                                "when": fert_data["when"],
                                "composition": fert_data["composition"],
                            })
                        break

    return recommended_fertilizers


def calculer_engrais_intelligent(wilaya_name, crop_name, planting_date_str, area, weather_data):
    # الحصول على نوع التربة
    soil_type_fr = WILAYA_SOIL_MAPPING.get(wilaya_name, "Sols bruns calcaires")
    soil_data_complexe = SOL_NUTRIENTS_COMPLET.get(soil_type_fr, SOL_NUTRIENTS_COMPLET["Sols bruns calcaires"])

    # ✅ التحقق من وجود المحصول - تصحيح
    culture_data = CROPS_DATABASE.get(crop_name)
    if not culture_data:
        return {
            "success": False,
            "error": f"Crop data not found for {crop_name}. Available crops: {', '.join(CROPS_DATABASE.keys())}"
        }

    # حساب المرحلة الحالية
    stage_info = calculer_stade(planting_date_str, culture_data)
    if not stage_info:
        return {
            "success": False,
            "error": "Invalid planting date or future date. Please use a date in the past."
        }

    current_stade_name = stage_info["stade"]
    stade_data = culture_data["stades"].get(current_stade_name)
    if not stade_data:
        return {
            "success": False,
            "error": f"Stage data not found for {current_stade_name}"
        }

    # حساب الاحتياجات
    nutriments_list = ["N", "P", "K", "Ca", "Mg", "S"]
    resultats_nutriments = {}
    total_engrais_needed = 0

    for nut in nutriments_list:
        besoin = stade_data.get(nut, 0)
        disponible = soil_data_complexe.get(nut, 0)
        manque = max(0, besoin - disponible)
        efficacite = soil_data_complexe["efficacite"]
        engrais_a_apporter = manque / efficacite if manque > 0 else 0

        resultats_nutriments[nut] = {
            "need": besoin,
            "available": disponible,
            "deficit": round(manque, 1),
            "required": round(engrais_a_apporter, 1),
            "ok": disponible >= besoin
        }
        total_engrais_needed += engrais_a_apporter

    # تعديل الطقس
    if weather_data:
        temp = weather_data.get('avg_temp_7days', weather_data.get('temperature', 22))
        pluie = weather_data.get('precipitation', 0)
        
        if temp > 35:
            total_engrais_needed *= 1.12
        elif temp > 30:
            total_engrais_needed *= 1.06

        if pluie > 25:
            total_engrais_needed *= 1.15
        elif pluie > 10:
            total_engrais_needed *= 1.08

    # حساب الأسمدة الموصى بها
    engrais_apportes_for_exces = {nut: resultats_nutriments[nut]["required"] for nut in nutriments_list}
    analyse_exces = detecter_exces_et_desequilibres(soil_data_complexe, stade_data, engrais_apportes_for_exces)
    
    recommended_fertilizers = get_fertilizer_recommendations(resultats_nutriments, area)

    # حساب الري
    irrigation_base = culture_data.get("irrigation", {}).get(current_stade_name, 4)
    if weather_data and weather_data.get("avg_temp_7days", 20) > 30:
        irrigation_base *= 1.3
    irrigation_amount = round(irrigation_base, 1)

    # إعداد التنبيهات
    alerts = analyse_exces["alertes_critiques"]
    warnings = analyse_exces["avertissements"]
    tips = [{"title": "نصيحة تصحيحية", "description": c} for c in analyse_exces["conseils_correctifs"]]

    # إضافة تنبيهات الطقس
    if weather_data:
        if weather_data.get("temperature_max", 25) > 35:
            alerts.append(f"⚠️ تحذير: درجة حرارة عالية جداً ({weather_data['temperature_max']}°C)")
            tips.append({"title": "موجة حر", "description": "زيادة الري وتوفير الظل للمحاصيل"})
        if weather_data.get("precipitation", 0) > 30:
            warnings.append(f"⚠️ أمطار غزيرة متوقعة ({weather_data['precipitation']}mm)")
            tips.append({"title": "أمطار غزيرة", "description": "تجنب التسميد قبل هطول الأمطار"})

    # إعداد المرحلة التالية
    stades_list = list(culture_data["stades"].keys())
    next_stage_info = {}
    try:
        current_index = stades_list.index(current_stade_name)
        if current_index + 1 < len(stades_list):
            next_name = stades_list[current_index + 1]
            next_stage_info = {
                "name": next_name,
                "days_estimes": culture_data["stades"][next_name]["duree"]
            }
    except ValueError:
        pass

    # المخرجات النهائية
    return {
        "success": True,
        "wilaya": wilaya_name,
        "area": area,
        "crop": crop_name,
        "plantDate": planting_date_str,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "totalKgHa": round(total_engrais_needed, 1),
        "totalKg": round(total_engrais_needed * area, 1),  # الكمية الإجمالية للمساحة
        "stageProgress": stage_info["progression"],
        "stageName": current_stade_name,
        "daysElapsed": stage_info["jours_ecoules"],
        "totalDays": culture_data["cycle_jours"],
        "daysRemaining": stage_info["days_remaining"],
        "nextStage": next_stage_info,
        "soilType": soil_type_fr,
        "soilData": {
            "texture": soil_type_fr,
            "phMin": soil_data_complexe["ph"],
            "phMax": soil_data_complexe["ph"],
            "fertilisation": soil_data_complexe["description"],
        },
        "soilNutrients": {
            "efficacite": soil_data_complexe["efficacite"],
            "moPct": soil_data_complexe["mo_pct"],
            "cec": f"{soil_data_complexe['cec']} meq/100g",
            "available": {nut: soil_data_complexe.get(nut, 0) for nut in nutriments_list},
        },
        "nutrients": resultats_nutriments,
        "fertilizers": recommended_fertilizers,
        "alerts": alerts,
        "warnings": warnings,
        "tips": tips,
        "irrigation": {"amount": irrigation_amount, "unit": "mm/jour"},
        "weatherData": weather_data
    }


# ============================================================
# نقاط نهاية API
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():
    """نقطة نهاية للتحقق من صحة الخادم"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/wilayas', methods=['GET'])
def get_wilayas():
    """إرجاع قائمة الولايات مع إحداثياتها"""
    wilayas_list = []
    for name, data in WILAYA_COORDINATES.items():
        wilayas_list.append({
            "name": name,
            "code": data["code"],
            "region": data["region"],
            "lat": data["lat"],
            "lon": data["lon"]
        })
    return jsonify(wilayas_list)

@app.route('/api/crops', methods=['GET'])
def get_crops():
    """إرجاع قائمة المحاصيل المتاحة"""
    crops_list = []
    for name, data in CROPS_DATABASE.items():
        crops_list.append({
            "name": name,
            "categorie": data["categorie"],
            "cycle_jours": data["cycle_jours"]
        })
    return jsonify(crops_list)

@app.route('/api/fertilizer/calculate', methods=['POST'])
def calculate_fertilizer():
    """نقطة النهاية الرئيسية لحساب التسميد"""
    try:
        data = request.get_json()
        
        wilaya = data.get('wilaya')
        area = float(data.get('area', 1.0))
        crop = data.get('crop')
        plant_date = data.get('plantDate')
        
        # التحقق من صحة المدخلات
        if not wilaya or not crop or not plant_date:
            return jsonify({"success": False, "error": "Missing required fields: wilaya, crop, plantDate"}), 400
        
        # الحصول على إحداثيات الولاية
        wilaya_coords = WILAYA_COORDINATES.get(wilaya)
        if not wilaya_coords:
            return jsonify({"success": False, "error": f"Wilaya '{wilaya}' not found"}), 400
        
        # جلب بيانات الطقس
        weather_data = get_weather_data(wilaya_coords["lat"], wilaya_coords["lon"])
        
        # حساب التوصية
        result = calculer_engrais_intelligent(wilaya, crop, plant_date, area, weather_data)
        
        # ✅ إذا كانت النتيجة تحتوي على success: False، نرجعها مع status code مناسب
        if not result.get('success', True):
            return jsonify(result), 400
        
        return jsonify(result)
    
    except ValueError as e:
        # خطأ في تحويل البيانات (مثلاً area مش رقم)
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        # أي خطأ آخر
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """نقطة نهاية لجلب بيانات الطقس لولاية محددة"""
    wilaya = request.args.get('wilaya')
    if not wilaya:
        return jsonify({"success": False, "error": "Wilaya parameter required"}), 400
    
    wilaya_coords = WILAYA_COORDINATES.get(wilaya)
    if not wilaya_coords:
        return jsonify({"success": False, "error": f"Wilaya '{wilaya}' not found"}), 400
    
    weather = get_weather_data(wilaya_coords["lat"], wilaya_coords["lon"])
    return jsonify({"success": True, "weather": weather, "wilaya": wilaya})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)