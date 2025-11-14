"""
HCM VOYAGES - Application Streamlit Optimisée
Améliorations: Performance, UX, Sécurité et Fonctionnalités
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple
import hashlib

# Configuration de la page
st.set_page_config(
    page_title="HCM Voyages - L'évasion sur mesure",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONFIGURATION SUPABASE ======
SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"

# ====== SÉCURITÉ ======
def hash_password(password: str) -> str:
    """Hash un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_CREDENTIALS = {
    "admin": hash_password("admin123")
}

# Initialisation du client Supabase
@st.cache_resource
def init_supabase() -> Optional[Client]:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ Erreur de connexion Supabase: {e}")
        return None

supabase = init_supabase()

# ====== FONCTIONS UTILITAIRES ======
def validate_email(email: str) -> bool:
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Valide le format d'un numéro de téléphone algérien"""
    clean_phone = phone.replace(' ', '').replace('-', '')
    pattern = r'^(\+?213|0)[5-7][0-9]{8}$'
    return bool(re.match(pattern, clean_phone))

def format_currency(amount: float) -> str:
    """Formate un montant en devise"""
    return f"{amount:,.0f}".replace(',', ' ') + " €"

def format_date(date_str: str) -> str:
    """Formate une date au format français"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%d/%m/%Y %H:%M')
    except:
        return date_str

# ====== LOGO ======
def display_logo(size: str = "300px"):
    """Affiche le logo avec fallback"""
    try:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <div style="font-size: {size}; color: #667eea;">✈️</div>
            </div>
        """, unsafe_allow_html=True)

# ====== CSS OPTIMISÉ ======
def load_css():
    """Charge le CSS avec animations optimisées et responsive mobile"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * { 
            font-family: 'Poppins', sans-serif; 
        }
        
        .stApp { 
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        }
        
        /* Responsive - Mobile First */
        @media only screen and (max-width: 768px) {
            /* Ajustement des titres pour mobile */
            h1 { font-size: 1.8em !important; }
            h2 { font-size: 1.5em !important; }
            h3 { font-size: 1.2em !important; }
            
            /* Hero Section responsive */
            .hero-section {
                height: 300px !important;
            }
            
            .hero-title {
                font-size: 2em !important;
            }
            
            .hero-subtitle {
                font-size: 1em !important;
            }
            
            /* Carousel responsive */
            .carousel-container {
                height: 350px !important;
            }
            
            .carousel-title {
                font-size: 0.3em !important;
            }
            
            .carousel-description {
                font-size: 0.15em !important;
            }
            
            /* Cards responsive */
            .card {
                padding: 15px !important;
                margin: 10px 0 !important;
            }
            
            .price-tag {
                font-size: 18px !important;
                padding: 8px 15px !important;
            }
            
            /* Boutons plus grands pour mobile */
            .stButton>button {
                padding: 15px 25px !important;
                font-size: 16px !important;
                min-height: 50px !important;
            }
            
            /* Inputs plus grands */
            .stTextInput input, 
            .stTextArea textarea, 
            .stSelectbox select, 
            .stNumberInput input,
            .stDateInput input {
                font-size: 16px !important;
                padding: 12px !important;
                min-height: 50px !important;
            }
            
            /* Sidebar mobile */
            [data-testid="stSidebar"] {
                min-width: 250px !important;
            }
            
            /* Colonnes en mode mobile - stack vertical */
            [data-testid="column"] {
                width: 100% !important;
                flex: 100% !important;
                max-width: 100% !important;
            }
            
            /* Espacement mobile */
            .element-container {
                margin-bottom: 15px !important;
            }
            
            /* Form labels plus lisibles */
            label {
                font-size: 16px !important;
            }
        }
        
        /* Tablettes */
        @media only screen and (min-width: 769px) and (max-width: 1024px) {
            .hero-title {
                font-size: 2.8em !important;
            }
            
            .hero-subtitle {
                font-size: 1.2em !important;
            }
            
            .carousel-container {
                height: 400px !important;
            }
        }
        
        /* Amélioration du touch sur mobile */
        @media (hover: none) and (pointer: coarse) {
            .stButton>button {
                -webkit-tap-highlight-color: rgba(30, 64, 175, 0.3);
                touch-action: manipulation;
            }
            
            .card {
                touch-action: manipulation;
            }
        }
        
        /* Hero Section */
        .hero-section {
            position: relative;
            width: 100%;
            height: 400px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            background: white;
        }
        
        .hero-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        
        .hero-title {
            color: #1e40af;
            font-size: 3.5em;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: fadeInDown 0.8s ease-out;
            text-align: center;
        }
        
        .hero-subtitle {
            color: #2563eb;
            font-size: 1.5em;
            font-weight: 300;
            margin: 20px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            animation: fadeInUp 0.8s ease-out 0.2s backwards;
            text-align: center;
        }
        
        /* Carousel */
        .carousel-container {
            position: relative;
            width: 100%;
            height: 500px;
            border-radius: 20px;
            overflow: hidden;
            margin: 30px 0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        .carousel-slide {
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8em;
            animation: slideIn 0.5s ease-out;
            background: linear-gradient(135deg, rgba(30, 64, 175, 0.9), rgba(37, 99, 235, 0.9));
        }
        
        .carousel-content {
            text-align: center;
            color: white;
            padding: 40px;
        }
        
        .carousel-title {
            font-size: 0.4em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        
        .carousel-description {
            font-size: 0.2em;
            font-weight: 300;
            margin-top: 15px;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(100px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Cards */
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin: 15px 0;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2, .card h3, .card h4 {
            color: #1e3a8a !important;
        }
        
        .card p, .card span:not(.badge), .card strong {
            color: #1e3a8a !important;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            border-color: #1e3a8a;
        }
        
        .price-tag {
            color: #dc2626;
            font-size: 24px;
            font-weight: 700;
            margin-top: 15px;
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-radius: 12px;
        }
        
        /* Buttons */
        .stButton>button {
            background: white;
            color: #1e40af;
            border-radius: 25px;
            padding: 12px 30px;
            border: 2px solid white;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            background: #f8fafc;
        }
        
        .stButton>button:active {
            transform: translateY(0);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: white;
            border-right: 2px solid #e5e7eb;
        }
        
        [data-testid="stSidebar"] * {
            color: #1e40af !important;
        }
        
        [data-testid="stSidebar"] h2 {
            color: #1e40af !important;
        }
        
        /* Info boxes */
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid white;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        
        .info-box h3, .info-box h4, .info-box p, .info-box strong {
            color: #1e3a8a !important;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left-color: #10b981;
        }
        
        .success-box h3, .success-box h4, .success-box p, .success-box strong {
            color: #065f46 !important;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left-color: #f59e0b;
        }
        
        .warning-box h3, .warning-box h4, .warning-box p, .warning-box strong {
            color: #92400e !important;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 5px;
        }
        
        .badge-success { background: #10b981; color: white; }
        .badge-warning { background: #f59e0b; color: white; }
        .badge-danger { background: #dc2626; color: white; }
        .badge-info { background: #3b82f6; color: white; }
        
        /* Headers - Blanc sur accueil (fond bleu) */
        .accueil-page h1, .accueil-page h2, .accueil-page h3 {
            color: white !important;
        }
        
        .accueil-page p:not(.card p):not(.info-box p), 
        .accueil-page label:not(.card label), 
        .accueil-page span:not(.card span):not(.badge) {
            color: white !important;
        }
        
        /* Headers - Blanc sur autres pages (fond bleu) */
        .other-page h1, .other-page h2, .other-page h3 {
            color: white !important;
        }
        
        .other-page > p:not(.card p):not(.info-box p), 
        .other-page > label:not(.card label), 
        .other-page > span:not(.card span):not(.badge),
        .other-page [data-testid="stMarkdownContainer"] > p {
            color: white !important;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.95);
            color: #1e40af;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stNumberInput input:focus {
            border-color: white;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px 10px 0 0;
            color: white !important;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: white;
            color: #1e3a8a !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            color: white !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] h3,
        .stTabs [data-baseweb="tab-panel"] h4 {
            color: white !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: #1e3a8a !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #1e3a8a;
        }
        
        .streamlit-expanderContent {
            background-color: white;
        }
        
        .streamlit-expanderContent p, 
        .streamlit-expanderContent span,
        .streamlit-expanderContent strong {
            color: #1e3a8a !important;
        }
        
        /* DataFrames */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: white;
        }
        
        /* Date Input */
        .stDateInput input {
            background: rgba(255, 255, 255, 0.95);
            color: #1e40af;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: white;
            color: #065f46;
        }
        
        .stError {
            background: white;
            color: #991b1b;
        }
        
        .stInfo {
            background: white;
            color: #1e40af;
        }
        
        .stWarning {
            background: white;
            color: #92400e;
        }
        
        /* Amélioration de la lisibilité sur petits écrans */
        @media only screen and (max-width: 480px) {
            .hero-title {
                font-size: 1.5em !important;
            }
            
            .hero-subtitle {
                font-size: 0.9em !important;
            }
            
            .carousel-container {
                height: 300px !important;
            }
            
            .card {
                padding: 12px !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
        
        /* Hero Section */
        .hero-section {
            position: relative;
            width: 100%;
            height: 400px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            background: white;
        }
        
        .hero-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        
        .hero-title {
            color: #1e40af;
            font-size: 3.5em;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: fadeInDown 0.8s ease-out;
        }
        
        .hero-subtitle {
            color: #2563eb;
            font-size: 1.5em;
            font-weight: 300;
            margin: 20px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            animation: fadeInUp 0.8s ease-out 0.2s backwards;
        }
        
        /* Carousel */
        .carousel-container {
            position: relative;
            width: 100%;
            height: 500px;
            border-radius: 20px;
            overflow: hidden;
            margin: 30px 0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        .carousel-slide {
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8em;
            animation: slideIn 0.5s ease-out;
            background: linear-gradient(135deg, rgba(30, 64, 175, 0.9), rgba(37, 99, 235, 0.9));
        }
        
        .carousel-content {
            text-align: center;
            color: white;
            padding: 40px;
        }
        
        .carousel-title {
            font-size: 0.4em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        
        .carousel-description {
            font-size: 0.2em;
            font-weight: 300;
            margin-top: 15px;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.3);
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(100px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Cards */
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin: 15px 0;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            border-color: white;
        }
        
        .card h2, .card h3, .card h4 {
            color: #1e40af !important;
        }
        
        .card p, .card span {
            color: #374151 !important;
        }
        
        .price-tag {
            color: #dc2626;
            font-size: 24px;
            font-weight: 700;
            margin-top: 15px;
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-radius: 12px;
        }
        
        /* Buttons */
        .stButton>button {
            background: white;
            color: #1e40af;
            border-radius: 25px;
            padding: 12px 30px;
            border: 2px solid white;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            background: #f8fafc;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: white;
            border-right: 2px solid #e5e7eb;
        }
        
        [data-testid="stSidebar"] * {
            color: #1e40af !important;
        }
        
        [data-testid="stSidebar"] h2 {
            color: #1e40af !important;
        }
        
        /* Info boxes */
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid white;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        
        .info-box h3, .info-box h4, .info-box p {
            color: #1e40af !important;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left-color: #10b981;
        }
        
        .success-box h3, .success-box h4, .success-box p {
            color: #065f46 !important;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left-color: #f59e0b;
        }
        
        .warning-box h3, .warning-box h4, .warning-box p {
            color: #92400e !important;
        }
        
        /* Badge */
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 5px;
        }
        
        .badge-success { background: #10b981; color: white; }
        .badge-warning { background: #f59e0b; color: white; }
        .badge-danger { background: #dc2626; color: white; }
        .badge-info { background: #3b82f6; color: white; }
        
        /* Headers - Blanc sur accueil (fond bleu) */
        .accueil-page h1, .accueil-page h2, .accueil-page h3 {
            color: white !important;
        }
        
        .accueil-page p:not(.card p):not(.info-box p), 
        .accueil-page label:not(.card label), 
        .accueil-page span:not(.card span):not(.badge) {
            color: white !important;
        }
        
        /* Texte dans les cards - toujours noir sur blanc */
        .card h2, .card h3, .card h4 {
            color: #1e3a8a !important;
        }
        
        .card p, .card span:not(.badge) {
            color: #1e3a8a !important;
        }
        
        /* Headers - Blanc sur autres pages (fond bleu) */
        .other-page h1, .other-page h2, .other-page h3 {
            color: white !important;
        }
        
        .other-page > p:not(.card p):not(.info-box p), 
        .other-page > label:not(.card label), 
        .other-page > span:not(.card span):not(.badge),
        .other-page [data-testid="stMarkdownContainer"] > p {
            color: white !important;
        }
        
        /* Info boxes - noir sur blanc */
        .info-box h3, .info-box h4, .info-box p, .info-box strong {
            color: #1e3a8a !important;
        }
        
        .success-box h3, .success-box h4, .success-box p, .success-box strong {
            color: #065f46 !important;
        }
        
        .warning-box h3, .warning-box h4, .warning-box p, .warning-box strong {
            color: #92400e !important;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.95);
            color: #1e40af;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stNumberInput input:focus {
            border-color: white;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px 10px 0 0;
            color: white !important;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: white;
            color: #1e3a8a !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            color: white !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] h3,
        .stTabs [data-baseweb="tab-panel"] h4 {
            color: white !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: #1e3a8a !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #1e3a8a;
        }
        
        .streamlit-expanderContent {
            background-color: white;
        }
        
        .streamlit-expanderContent p, 
        .streamlit-expanderContent span,
        .streamlit-expanderContent strong {
            color: #1e3a8a !important;
        }
        
        /* DataFrames */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: white;
        }
        
        /* Date Input */
        .stDateInput input {
            background: rgba(255, 255, 255, 0.95);
            color: #1e40af;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: white;
            color: #065f46;
        }
        
        .stError {
            background: white;
            color: #991b1b;
        }
        
        .stInfo {
            background: white;
            color: #1e40af;
        }
        
        .stWarning {
            background: white;
            color: #92400e;
        }
        </style>
    """, unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======
@st.cache_data(ttl=300)
def get_destinations() -> List[Dict]:
    """Récupère toutes les destinations actives avec cache"""
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
    return []

def add_reservation(data: Dict) -> Tuple[bool, str]:
    """Ajoute une réservation avec validation renforcée"""
    if not supabase:
        return False, "Base de données non connectée"
    
    try:
        data['statut'] = 'en_attente'
        data['date_creation'] = datetime.now().isoformat()
        response = supabase.table('reservations').insert(data).execute()
        
        # Invalider le cache des statistiques
        get_statistics.clear()
        
        return True, "✅ Réservation enregistrée avec succès"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def get_reservations(limit: Optional[int] = None) -> List[Dict]:
    """Récupère les réservations"""
    if supabase:
        try:
            query = supabase.table('reservations').select("*").order('date_creation', desc=True)
            if limit:
                query = query.limit(limit)
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    return []

def update_reservation_status(reservation_id: int, new_status: str) -> bool:
    """Met à jour le statut d'une réservation"""
    if supabase:
        try:
            supabase.table('reservations').update({"statut": new_status}).eq('id', reservation_id).execute()
            get_statistics.clear()
            return True
        except:
            return False
    return False

def add_contact(data: Dict) -> Tuple[bool, str]:
    """Ajoute un message de contact"""
    if not supabase:
        return False, "Base de données non connectée"
    
    try:
        data['lu'] = False
        data['date_creation'] = datetime.now().isoformat()
        supabase.table('contacts').insert(data).execute()
        get_statistics.clear()
        return True, "✅ Message envoyé avec succès"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def get_contacts(unread_only: bool = False) -> List[Dict]:
    """Récupère les messages de contact"""
    if supabase:
        try:
            query = supabase.table('contacts').select("*").order('date_creation', desc=True)
            if unread_only:
                query = query.eq('lu', False)
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    return []

def mark_contact_as_read(contact_id: int) -> bool:
    """Marque un message comme lu"""
    if supabase:
        try:
            supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            get_statistics.clear()
            return True
        except:
            return False
    return False

# ====== STATISTIQUES ======
@st.cache_data(ttl=60)
def get_statistics() -> Dict:
    """Calcule les statistiques avec cache"""
    stats = {
        'total_reservations': 0,
        'reservations_en_attente': 0,
        'reservations_confirmees': 0,
        'messages_non_lus': 0,
        'destinations_actives': 0
    }
    
    if supabase:
        try:
            reservations = get_reservations()
            stats['total_reservations'] = len(reservations)
            stats['reservations_en_attente'] = len([r for r in reservations if r.get('statut') == 'en_attente'])
            stats['reservations_confirmees'] = len([r for r in reservations if r.get('statut') == 'confirme'])
            
            contacts = get_contacts(unread_only=True)
            stats['messages_non_lus'] = len(contacts)
            
            destinations = get_destinations()
            stats['destinations_actives'] = len(destinations)
        except:
            pass
    
    return stats

# ====== COMPOSANTS RÉUTILISABLES ======
def display_stat_card(icon: str, number: str, label: str):
    """Affiche une carte de statistique"""
    st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
            <h2 style="color: #1e40af; margin: 5px 0;">{number}</h2>
            <p style="margin: 5px 0 0 0; color: #374151;">{label}</p>
        </div>
    """, unsafe_allow_html=True)

# ====== CAROUSEL ======
def display_carousel():
    """Affiche un carrousel de destinations avec émojis"""
    carousel_data = [
        {
            "emoji": "🗼",
            "title": "Paris, France",
            "description": "La Ville Lumière vous attend avec ses monuments emblématiques"
        },
        {
            "emoji": "🕌",
            "title": "Istanbul, Turquie",
            "description": "Entre Orient et Occident, découvrez une ville fascinante"
        },
        {
            "emoji": "🏝️",
            "title": "Maldives",
            "description": "Paradis tropical aux eaux cristallines"
        },
        {
            "emoji": "🏛️",
            "title": "Rome, Italie",
            "description": "L'histoire antique prend vie dans la Ville Éternelle"
        },
        {
            "emoji": "🌴",
            "title": "Dubaï, EAU",
            "description": "Luxe et modernité dans le désert arabique"
        }
    ]
    
    # Initialiser l'index du carousel
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    # Container pour le carousel
    carousel_container = st.empty()
    
    # Afficher la slide actuelle
    current_slide = carousel_data[st.session_state.carousel_index]
    
    carousel_container.markdown(f"""
        <div class="carousel-container">
            <div class="carousel-slide">
                <div class="carousel-content">
                    <div style="font-size: 1.5em; margin-bottom: 20px;">{current_slide['emoji']}</div>
                    <div class="carousel-title">{current_slide['title']}</div>
                    <div class="carousel-description">{current_slide['description']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Précédent", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(carousel_data)
            st.rerun()
    
    with col2:
        # Indicateurs de position
        indicators = ""
        for i in range(len(carousel_data)):
            if i == st.session_state.carousel_index:
                indicators += "⬤ "
            else:
                indicators += "○ "
        st.markdown(f"<div style='text-align: center; color: white; font-size: 1.5em;'>{indicators}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Suivant ▶", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_data)
            st.rerun()

# ====== PAGES ======
def page_accueil():
    """Page d'accueil optimisée avec texte blanc"""
    
    # Wrapper pour la page d'accueil
    st.markdown('<div class="accueil-page">', unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('<div class="hero-section"><div class="hero-overlay">', unsafe_allow_html=True)
    display_logo(size="150px")
    st.markdown("""
            <h1 class="hero-title">HCM VOYAGES</h1>
            <p class="hero-subtitle">L'évasion sur mesure, explorez, rêvez, partez</p>
        </div></div>
    """, unsafe_allow_html=True)
    
    # Carousel de photos
    st.markdown("### 🌍 Découvrez Nos Destinations Phares")
    display_carousel()
    
    # Statistiques
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    
    stats_data = [
        ("🌍", "50+", "Destinations"),
        ("😊", "1000+", "Clients Satisfaits"),
        ("📅", "10+", "Années d'Expérience"),
        ("🤝", "25+", "Partenaires")
    ]
    
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats_data):
        with col:
            display_stat_card(icon, num, label)
    
    # Services
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Nos Services Premium")
    
    services = [
        ("🎫", "Billets d'Avion", "Les meilleurs tarifs pour toutes destinations"),
        ("🏨", "Réservation Hôtels", "Hébergements de qualité sélectionnés"),
        ("🎒", "Circuits Organisés", "Voyages tout compris clés en main"),
        ("📋", "Assistance Visa", "Aide complète pour vos démarches"),
        ("💼", "Voyages Affaires", "Solutions professionnelles sur mesure"),
        ("🎯", "Séjours sur Mesure", "Créez votre voyage personnalisé")
    ]
    
    col1, col2, col3 = st.columns(3)
    for i, (icon, titre, desc) in enumerate(services):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
                <div class="card" style="min-height: 180px;">
                    <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
                    <h3 style="color: #1e40af; margin: 10px 0;">{titre}</h3>
                    <p style="color: #4b5563; font-size: 0.9em;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Section Photos Nature
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🌿 Découvrez des Destinations Sublimes")
    
    col1, col2, col3 = st.columns(3)
    
    nature_images = [
        {
            "emoji": "🏔️",
            "title": "Montagnes Majestueuses",
            "description": "Des sommets enneigés aux panoramas à couper le souffle"
        },
        {
            "emoji": "🏖️",
            "title": "Plages Paradisiaques",
            "description": "Eaux turquoise et sable blanc pour une détente absolue"
        },
        {
            "emoji": "🌲",
            "title": "Forêts Enchantées",
            "description": "Nature verdoyante et sentiers paisibles"
        },
        {
            "emoji": "🌅",
            "title": "Couchers de Soleil",
            "description": "Des moments magiques dans des lieux exceptionnels"
        },
        {
            "emoji": "🏝️",
            "title": "Îles Tropicales",
            "description": "Évasion garantie dans des cadres idylliques"
        },
        {
            "emoji": "🗻",
            "title": "Volcans & Geysers",
            "description": "Découvrez les merveilles géologiques du monde"
        }
    ]
    
    for i, img in enumerate(nature_images):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
                <div class="card" style="min-height: 220px; position: relative; overflow: hidden;">
                    <div style="font-size: 4em; margin-bottom: 15px; text-align: center;">{img['emoji']}</div>
                    <h3 style="color: #1e40af; text-align: center; margin: 10px 0;">{img['title']}</h3>
                    <p style="color: #4b5563; text-align: center; font-size: 0.9em;">{img['description']}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # CTA
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌍 Découvrir nos destinations", use_container_width=True, type="primary"):
            st.session_state.page = "destinations"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_destinations():
    """Page destinations avec recherche optimisée"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 🌍 Nos Voyages Organisés")
    
    # Filtres simplifiés
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", "", placeholder="Istanbul, Antalya, Hammamet...")
    with col2:
        tri = st.selectbox("💰 Trier", ["Nom A-Z", "Nom Z-A"])
    
    # Destinations fixes
    destinations = [
        {
            "nom": "Istanbul",
            "pays": "Turquie",
            "description": "La ville des deux continents, entre Orient et Occident. Mosquées majestueuses, bazars colorés et Bosphore enchanteur.",
            "duree": "5 jours / 4 nuits",
            "categorie": "Asie",
            "actif": True
        },
        {
            "nom": "Antalya",
            "pays": "Turquie",
            "description": "Perle de la Riviera turque. Plages paradisiaques, sites antiques et eaux cristallines de la Méditerranée.",
            "duree": "7 jours / 6 nuits",
            "categorie": "Asie",
            "actif": True
        },
        {
            "nom": "Hammamet",
            "pays": "Tunisie",
            "description": "Station balnéaire méditerranéenne. Plages dorées, médina authentique et art de vivre tunisien.",
            "duree": "6 jours / 5 nuits",
            "categorie": "Afrique",
            "actif": True
        },
        {
            "nom": "Sharm El Sheikh",
            "pays": "Égypte",
            "description": "Paradis de la Mer Rouge. Plongée exceptionnelle, récifs coralliens et luxe en bord de mer.",
            "duree": "7 jours / 6 nuits",
            "categorie": "Afrique",
            "actif": True
        },
        {
            "nom": "Malaisie",
            "pays": "Malaisie",
            "description": "Mélange fascinant de cultures. Kuala Lumpur moderne, plages de Langkawi et jungle tropicale.",
            "duree": "10 jours / 9 nuits",
            "categorie": "Asie",
            "actif": True
        },
        {
            "nom": "Maldives",
            "pays": "Maldives",
            "description": "Le paradis sur terre. Atolls turquoise, bungalows sur pilotis et fonds marins spectaculaires.",
            "duree": "8 jours / 7 nuits",
            "categorie": "Asie",
            "actif": True
        }
    ]
    
    # Filtrage
    filtered = destinations
    
    if search:
        search_lower = search.lower()
        filtered = [d for d in filtered if search_lower in d['nom'].lower() or search_lower in d.get('pays', '').lower()]
    
    # Tri
    if tri == "Nom A-Z":
        filtered = sorted(filtered, key=lambda x: x.get('nom', ''))
    else:
        filtered = sorted(filtered, key=lambda x: x.get('nom', ''), reverse=True)
    
    # Affichage
    st.markdown(f"### ✈️ {len(filtered)} voyage(s) organisé(s)")
    
    if not filtered:
        st.warning("Aucune destination ne correspond à vos critères")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Grille
    cols = st.columns(2)
    for idx, dest in enumerate(filtered):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="card" style="min-height: 280px;">
                    <h2 style="color: #1e40af; margin-bottom: 10px;">📍 {dest['nom']}</h2>
                    <h4 style="color: #4b5563; margin: 5px 0;">{dest['pays']}</h4>
                    <p style="color: #4b5563; margin: 15px 0; min-height: 80px; line-height: 1.6;">{dest['description']}</p>
                    <div style="background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); padding: 12px; border-radius: 10px; margin-top: 15px;">
                        <p style="margin: 0; color: #1e40af; font-weight: 600;">⏱️ {dest.get('duree', '5 jours')}</p>
                        <p style="margin: 5px 0 0 0; color: #2563eb; font-size: 0.9em;">Voyage tout compris</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_reservation():
    """Page de réservation optimisée"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📝 Réserver Votre Voyage")
    
    tab1, tab2 = st.tabs(["✈️ Réservation Voyage", "💰 Demande de Devis"])
    
    with tab1:
        st.markdown("### Formulaire de Réservation")
        
        with st.form("reservation_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom complet *", placeholder="Ex: Ahmed Benali")
                email = st.text_input("Email *", placeholder="exemple@email.com")
                telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            
            with col2:
                destination = st.text_input(
                    "Destination *", 
                    value=st.session_state.get('destination_selectionnee', ''),
                    placeholder="Ex: Paris"
                )
                date_depart = st.date_input(
                    "Date de départ *", 
                    value=datetime.now().date(),
                    min_value=datetime.now().date()
                )
                date_retour = st.date_input(
                    "Date de retour *", 
                    value=datetime.now().date() + timedelta(days=7),
                    min_value=datetime.now().date() + timedelta(days=1)
                )
                nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
            
            message = st.text_area("Message / Demandes spéciales", height=120)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✈️ Envoyer la demande", use_container_width=True)
            
            if submitted:
                errors = []
                
                if not nom or len(nom) < 3:
                    errors.append("Le nom doit contenir au moins 3 caractères")
                if not email or not validate_email(email):
                    errors.append("Email invalide")
                if not telephone or not validate_phone(telephone):
                    errors.append("Téléphone invalide (format: +213XXXXXXXXX)")
                if not destination:
                    errors.append("Destination requise")
                if date_retour <= date_depart:
                    errors.append("La date de retour doit être après la date de départ")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    duree_sejour = (date_retour - date_depart).days
                    
                    data = {
                        "nom": nom,
                        "email": email,
                        "telephone": telephone,
                        "destination": destination,
                        "date_depart": str(date_depart),
                        "date_retour": str(date_retour),
                        "nb_personnes": nb_personnes,
                        "duree_sejour": duree_sejour,
                        "message": message
                    }
                    
                    success, msg = add_reservation(data)
                    
                    if success:
                        st.success(msg)
                        st.markdown(f"""
                            <div class="info-box success-box">
                                <h4>🎉 Réservation enregistrée !</h4>
                                <p>Destination: <strong>{destination}</strong></p>
                                <p>📅 Départ: <strong>{date_depart.strftime('%d/%m/%Y')}</strong></p>
                                <p>📅 Retour: <strong>{date_retour.strftime('%d/%m/%Y')}</strong></p>
                                <p>⏱️ Durée: <strong>{duree_sejour} jour(s)</strong></p>
                                <p>👥 Personnes: <strong>{nb_personnes}</strong></p>
                                <hr>
                                <p>📧 Confirmation envoyée à <strong>{email}</strong></p>
                                <p>Notre équipe vous contactera sous 24h pour finaliser votre réservation</p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.error(msg)
    
    with tab2:
        st.markdown("### 💰 Demande de Devis Personnalisé")
        st.markdown("""
            <div class="info-box">
                <p style="font-size: 1.05em;">
                Recevez un devis détaillé et personnalisé pour votre voyage. 
                Indiquez vos dates, destination et préférences.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("devis_form", clear_on_submit=True):
            st.markdown("#### 👤 Vos Coordonnées")
            col1, col2 = st.columns(2)
            
            with col1:
                devis_nom = st.text_input("Nom complet *", placeholder="Votre nom")
                devis_email = st.text_input("Email *", placeholder="votre@email.com")
                devis_telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            
            with col2:
                devis_destination = st.selectbox("Destination *", [
                    "-- Sélectionnez --", "Paris", "Istanbul", "Dubaï", "Londres", 
                    "Rome", "Barcelone", "Marrakech", "Le Caire", "New York", "Tokyo"
                ])
                devis_date_depart = st.date_input(
                    "Date de départ *", 
                    value=datetime.now().date(),
                    min_value=datetime.now().date()
                )
                devis_date_retour = st.date_input(
                    "Date de retour *", 
                    value=datetime.now().date() + timedelta(days=7),
                    min_value=datetime.now().date() + timedelta(days=1)
                )
            
            col1, col2 = st.columns(2)
            with col1:
                devis_nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
            with col2:
                devis_budget = st.select_slider("Budget approximatif", [
                    "Moins de 500€", "500€ - 1000€", "1000€ - 2000€", "Plus de 2000€"
                ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            devis_message = st.text_area("Commentaires / Demandes spéciales", height=100)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted_devis = st.form_submit_button("📨 Recevoir mon devis gratuit", use_container_width=True)
            
            if submitted_devis:
                errors_devis = []
                
                if not devis_nom or len(devis_nom) < 3:
                    errors_devis.append("Nom invalide")
                if not devis_email or not validate_email(devis_email):
                    errors_devis.append("Email invalide")
                if not devis_telephone or not validate_phone(devis_telephone):
                    errors_devis.append("Téléphone invalide")
                if devis_destination == "-- Sélectionnez --":
                    errors_devis.append("Veuillez sélectionner une destination")
                if devis_date_retour <= devis_date_depart:
                    errors_devis.append("La date de retour doit être après la date de départ")
                
                if errors_devis:
                    for error in errors_devis:
                        st.error(f"❌ {error}")
                else:
                    duree_devis = (devis_date_retour - devis_date_depart).days
                    st.success("✅ Demande de devis envoyée avec succès!")
                    st.markdown(f"""
                        <div class="info-box success-box">
                            <h4>🎉 Demande de devis enregistrée !</h4>
                            <p>Destination: <strong>{devis_destination}</strong></p>
                            <p>📅 Du {devis_date_depart.strftime('%d/%m/%Y')} au {devis_date_retour.strftime('%d/%m/%Y')}</p>
                            <p>⏱️ Durée: <strong>{duree_devis} jour(s)</strong></p>
                            <p>👥 {devis_nb_personnes} personne(s)</p>
                            <p>💰 Budget: {devis_budget}</p>
                            <hr>
                            <p>Vous recevrez votre devis personnalisé sous 48h à <strong>{devis_email}</strong></p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_contact():
    """Page de contact"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📞 Contactez-Nous")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h3 style="color: #1e40af;">📍 Notre Agence</h3>
                <p style="color: #374151;"><strong>🏢 Adresse:</strong><br>Cité 632 logements BT 28<br>El Mohammadia, Alger, Algérie</p>
                <p style="color: #374151;"><strong>📞 Téléphone:</strong><br>+213 783 80 27 12</p>
                <p style="color: #374151;"><strong>📧 Email:</strong><br>hcmvoyage1@gmail.com</p>
                <p style="color: #374151;"><strong>🕐 Horaires:</strong><br>Dim-Jeu: 9h-18h<br>Sam: 9h-13h</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            sujet = st.selectbox("Sujet *", ["Information", "Réservation", "Réclamation", "Autre"])
            message = st.text_area("Message *", height=150)
            
            if st.form_submit_button("📨 Envoyer", use_container_width=True):
                if not all([nom, email, message]) or not validate_email(email):
                    st.error("❌ Veuillez remplir correctement tous les champs")
                else:
                    success, msg = add_contact({"nom": nom, "email": email, "sujet": sujet, "message": message})
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_admin():
    """Dashboard administrateur sécurisé"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown("""
            <div class="hero-section" style="height: 300px;">
                <div class="hero-overlay">
                    <h1>🔐 Administration</h1>
                    <p>Accès sécurisé</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("👤 Utilisateur")
                password = st.text_input("🔒 Mot de passe", type="password")
                
                if st.form_submit_button("🔓 Connexion", use_container_width=True):
                    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hash_password(password):
                        st.session_state.admin_logged = True
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    st.markdown("# ⚙️ Dashboard Administrateur")
    
    stats = get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_stat_card("📋", str(stats['total_reservations']), "Réservations")
    with col2:
        display_stat_card("⏳", str(stats['reservations_en_attente']), "En attente")
    with col3:
        display_stat_card("✅", str(stats['reservations_confirmees']), "Confirmées")
    with col4:
        display_stat_card("📧", str(stats['messages_non_lus']), "Messages non lus")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Réservations", "💬 Messages", "🌍 Destinations"])
    
    with tab1:
        st.markdown("### Gestion des Réservations")
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            
            for _, res in df.iterrows():
                status_badge = ""
                if res.get('statut') == 'en_attente':
                    status_badge = '<span class="badge badge-warning">En attente</span>'
                elif res.get('statut') == 'confirme':
                    status_badge = '<span class="badge badge-success">Confirmé</span>'
                elif res.get('statut') == 'annule':
                    status_badge = '<span class="badge badge-danger">Annulé</span>'
                
                with st.expander(f"#{res.get('id')} - {res.get('nom')} → {res.get('destination')} {status_badge}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**👤 Client:** {res.get('nom')}")
                        st.markdown(f"**📧 Email:** {res.get('email')}")
                        st.markdown(f"**📞 Tél:** {res.get('telephone')}")
                    
                    with col2:
                        st.markdown(f"**📍 Destination:** {res.get('destination')}")
                        st.markdown(f"**📅 Départ:** {res.get('date_depart')}")
                        st.markdown(f"**📅 Retour:** {res.get('date_retour', 'Non spécifié')}")
                        st.markdown(f"**⏱️ Durée:** {res.get('duree_sejour', 'N/A')} jour(s)")
                        st.markdown(f"**👥 Personnes:** {res.get('nb_personnes')}")
                    
                    with col3:
                        st.markdown("**📝 Message:**")
                        st.info(res.get('message', 'Aucun message'))
                    
                    st.markdown("---")
                    col_act1, col_act2, col_act3 = st.columns(3)
                    
                    with col_act1:
                        if st.button("✅ Confirmer", key=f"conf_{res.get('id')}", use_container_width=True):
                            if update_reservation_status(res.get('id'), 'confirme'):
                                st.success("Réservation confirmée")
                                st.rerun()
                    
                    with col_act2:
                        if st.button("⏳ En attente", key=f"pend_{res.get('id')}", use_container_width=True):
                            if update_reservation_status(res.get('id'), 'en_attente'):
                                st.success("Statut mis à jour")
                                st.rerun()
                    
                    with col_act3:
                        if st.button("❌ Annuler", key=f"canc_{res.get('id')}", use_container_width=True):
                            if update_reservation_status(res.get('id'), 'annule'):
                                st.success("Réservation annulée")
                                st.rerun()
        else:
            st.info("📭 Aucune réservation")
    
    with tab2:
        st.markdown("### Messages de Contact")
        contacts = get_contacts()
        
        if contacts:
            for contact in contacts:
                is_read = contact.get('lu', False)
                icon = "📧" if is_read else "✉️"
                
                with st.expander(f"{icon} {contact.get('sujet', 'Sans sujet')} - {contact.get('nom', 'Anonyme')}", expanded=not is_read):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📧 Email:** {contact.get('email')}")
                        st.markdown(f"**📅 Date:** {format_date(contact.get('date_creation', ''))}")
                        st.markdown("**💬 Message:**")
                        st.info(contact.get('message', 'Pas de message'))
                    
                    with col2:
                        if not is_read:
                            if st.button("✅ Marquer comme lu", key=f"read_{contact.get('id')}", use_container_width=True):
                                if mark_contact_as_read(contact.get('id')):
                                    st.success("Marqué comme lu")
                                    st.rerun()
        else:
            st.info("📭 Aucun message")
    
    with tab3:
        st.markdown("### Destinations Actives")
        destinations = get_destinations()
        
        if destinations:
            df_dest = pd.DataFrame(destinations)
            columns_to_show = ['nom', 'pays', 'prix', 'categorie', 'duree']
            available_cols = [col for col in columns_to_show if col in df_dest.columns]
            
            if available_cols:
                st.dataframe(df_dest[available_cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_dest, use_container_width=True, hide_index=True)
            
            st.success(f"✅ {len(destinations)} destination(s) active(s)")
        else:
            st.info("🌍 Aucune destination configurée")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.admin_logged = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_visas():
    """Page d'informations sur les visas"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📋 Services Visa & Rendez-vous")
    
    st.markdown("""
        <div class="info-box">
            <h3>🌍 Obtenez votre visa facilement</h3>
            <p style="font-size: 1.1em;">
            HCM Voyages vous accompagne dans toutes vos démarches de visa. 
            Prenez rendez-vous selon votre besoin : Normal, Express ou à Domicile.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🌍 Nos Services Visa par Pays")
    
    visas_info = [
        {
            "flag": "🇺🇸",
            "pays": "USA",
            "types": ["📅 Normal", "⚡ Express"],
            "description": "B1/B2, ESTA - Délai Normal: 4-8 semaines / Express: 1-2 semaines"
        },
        {
            "flag": "🇫🇷",
            "pays": "France",
            "types": ["📅 Normal", "🏠 À Domicile"],
            "description": "Court séjour Schengen - Délai: 15-45 jours / Service à domicile disponible"
        },
        {
            "flag": "🇪🇸",
            "pays": "Espagne",
            "types": ["📅 Normal", "🏠 À Domicile"],
            "description": "Schengen touristique - Délai: 15-30 jours / Prise RDV à votre domicile"
        }
    ]
    
    for visa in visas_info:
        st.markdown(f"""
            <div class="card" style="margin: 20px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="font-size: 3em; margin-right: 20px;">{visa['flag']}</div>
                    <div>
                        <h2 style="color: #1e40af; margin: 0;">Visa {visa['pays']}</h2>
                        <p style="color: #4b5563; margin: 5px 0 0 0;">{visa['description']}</p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    {"".join([f'<span class="badge badge-info">{t}</span>' for t in visa['types']])}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 Prendre un rendez-vous", use_container_width=True, type="primary"):
            st.session_state.page = "demande-visa"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_demande_visa():
    """Page de demande de rendez-vous visa"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📅 Demande de Rendez-vous Visa")
    
    st.markdown("""
        <div class="hero-section" style="height: 250px;">
            <div class="hero-overlay">
                <div style="font-size: 3em; margin-bottom: 10px;">📅</div>
                <h1 class="hero-title" style="font-size: 2.5em;">Prenez Rendez-vous</h1>
                <p class="hero-subtitle">Choisissez le service adapté à vos besoins</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("rdv_visa_form", clear_on_submit=True):
        st.markdown("### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            numero_passeport = st.text_input("Numéro de passeport *", placeholder="Ex: 123456789")
            date_naissance = st.date_input("Date de naissance *", min_value=datetime(1920, 1, 1).date(), max_value=datetime.now().date())
            profession = st.text_input("Profession", placeholder="Votre profession")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Détails du Rendez-vous")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pays_destination = st.selectbox("Pays de destination *", [
                "-- Sélectionnez --", 
                "🇺🇸 États-Unis (USA)", 
                "🇫🇷 France", 
                "🇪🇸 Espagne"
            ])
            
            type_visa = st.selectbox("Type de visa *", [
                "Tourisme", "Affaires", "Visite familiale", "Études", "Travail"
            ])
        
        with col2:
            if "USA" in pays_destination:
                type_service = st.selectbox("Type de service *", [
                    "📅 Normal (4-8 semaines)",
                    "⚡ Express (1-2 semaines)"
                ])
            elif "France" in pays_destination or "Espagne" in pays_destination:
                type_service = st.selectbox("Type de service *", [
                    "📅 Normal (15-45 jours)",
                    "🏠 À Domicile (rendez-vous chez vous)"
                ])
            else:
                type_service = st.selectbox("Type de service *", [
                    "📅 Normal"
                ])
            
            date_rdv_souhaitee = st.date_input(
                "Date de rendez-vous souhaitée *",
                value=datetime.now().date() + timedelta(days=7),
                min_value=datetime.now().date() + timedelta(days=3)
            )
        
        if "🏠" in type_service:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🏠 Adresse pour rendez-vous à domicile")
            adresse = st.text_area("Adresse complète *", height=100, placeholder="Rue, ville, code postal...")
        else:
            adresse = ""
        
        st.markdown("<br>", unsafe_allow_html=True)
        message = st.text_area("Informations complémentaires", height=100, placeholder="Précisez vos besoins particuliers...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📅 Confirmer mon rendez-vous", use_container_width=True)
        
        if submitted:
            errors = []
            
            if not all([nom, email, telephone, numero_passeport]):
                errors.append("Veuillez remplir tous les champs obligatoires")
            elif not validate_email(email):
                errors.append("Email invalide")
            elif not validate_phone(telephone):
                errors.append("Téléphone invalide")
            elif pays_destination == "-- Sélectionnez --":
                errors.append("Veuillez sélectionner un pays")
            elif "🏠" in type_service and not adresse:
                errors.append("L'adresse est obligatoire pour le service à domicile")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                service_type = "Express" if "⚡" in type_service else ("À Domicile" if "🏠" in type_service else "Normal")
                pays_clean = pays_destination.split(" ")[1] if " " in pays_destination else pays_destination
                
                st.success("✅ Demande de rendez-vous envoyée avec succès!")
                st.markdown(f"""
                    <div class="info-box success-box">
                        <h4>🎉 Rendez-vous enregistré !</h4>
                        <p><strong>Pays:</strong> {pays_clean}</p>
                        <p><strong>Type de visa:</strong> {type_visa}</p>
                        <p><strong>Service:</strong> {service_type}</p>
                        <p><strong>Date souhaitée:</strong> {date_rdv_souhaitee.strftime('%d/%m/%Y')}</p>
                        {"<p><strong>Adresse:</strong> " + adresse + "</p>" if adresse else ""}
                        <hr>
                        <p>📧 Une confirmation vous sera envoyée à <strong>{email}</strong></p>
                        <p>📞 Notre équipe vous contactera sous 48h pour confirmer votre rendez-vous</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_discover_algeria():
    """Page Discover Algeria"""
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("""
        <div class="hero-section" style="height: 300px;">
            <div class="hero-overlay">
                <div style="font-size: 3em; margin-bottom: 10px;">🇩🇿</div>
                <h1 class="hero-title">Discover Algeria</h1>
                <p class="hero-subtitle">Explorez la beauté du Maghreb</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏠 Présentation", "🗺️ Destinations"])
    
    with tab1:
        st.markdown("""
            <div class="info-box">
                <h3>🇩🇿 Bienvenue en Algérie</h3>
                <p style="font-size: 1.1em; line-height: 1.8;">
                L'Algérie, perle du Maghreb, vous invite à découvrir ses trésors. 
                Du Sahara majestueux aux plages méditerranéennes, en passant par les villes historiques,
                l'Algérie offre une diversité exceptionnelle.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✨ Pourquoi visiter l'Algérie ?")
        
        col1, col2 = st.columns(2)
        
        highlights = [
            ("🏜️", "Le Sahara", "Le plus grand désert du monde"),
            ("🏛️", "Patrimoine UNESCO", "Sites historiques exceptionnels"),
            ("🏖️", "Côtes méditerranéennes", "Plages magnifiques"),
            ("🍲", "Gastronomie riche", "Saveurs authentiques"),
            ("🎭", "Culture vivante", "Traditions millénaires"),
            ("🤝", "Hospitalité", "Accueil chaleureux"),
        ]
        
        for i, (icon, titre, desc) in enumerate(highlights):
            col = col1 if i < 3 else col2
            with col:
                st.markdown(f"""
                    <div class="card" style="margin: 10px 0;">
                        <div style="font-size: 2em; float: left; margin-right: 15px;">{icon}</div>
                        <div>
                            <strong style="color: #1e40af;">{titre}</strong><br>
                            <span style="color: #4b5563; font-size: 0.9em;">{desc}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🗺️ Destinations Phares")
        
        destinations_dz = [
            {"nom": "Alger", "description": "La capitale avec sa Casbah UNESCO", "prix": 450},
            {"nom": "Sahara", "description": "Le plus grand désert du monde", "prix": 890},
            {"nom": "Constantine", "description": "Ville des ponts suspendus", "prix": 520},
            {"nom": "Oran", "description": "Perle de la Méditerranée", "prix": 480},
            {"nom": "Tlemcen", "description": "Ville d'art et d'histoire", "prix": 510},
            {"nom": "Annaba", "description": "Hippone l'antique", "prix": 470},
        ]
        
        col1, col2, col3 = st.columns(3)
        for idx, dest in enumerate(destinations_dz):
            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                    <div class="card">
                        <h3>🇩🇿 {dest['nom']}</h3>
                        <p style="min-height: 50px; color: #4b5563;">{dest['description']}</p>
                        <div class="price-tag">{format_currency(dest['prix'])}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✈️ Réserver {dest['nom']}", key=f"dz_{idx}", use_container_width=True):
                    st.session_state.destination_selectionnee = dest['nom']
                    st.session_state.page = "reservation"
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ====== NAVIGATION PRINCIPALE ======
def main():
    """Fonction principale avec navigation optimisée"""
    
    load_css()
    
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(size="120px")
        st.markdown('<div style="text-align: center;"><h2>HCM VOYAGES</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Voyages Organisés", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📋", "Visa & RDV", "visas"),
            ("📅", "Prendre RDV", "demande-visa"),
            ("🇩🇿", "Discover Algeria", "discover-algeria"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Admin", "admin"),
        ]
        
        for icon, label, page_id in pages:
            button_type = "primary" if st.session_state.page == page_id else "secondary"
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.get('admin_logged', False):
            stats = get_statistics()
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <p style="margin: 5px 0; font-size: 0.9em;">📋 Réservations: <strong>{stats['total_reservations']}</strong></p>
                    <p style="margin: 5px 0; font-size: 0.9em;">⏳ En attente: <strong>{stats['reservations_en_attente']}</strong></p>
                    <p style="margin: 5px 0; font-size: 0.9em;">📧 Messages: <strong>{stats['messages_non_lus']}</strong></p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; font-size: 0.8em; color: #1e40af;">
                © 2024 HCM Voyages<br>
                Tous droits réservés
            </div>
        """, unsafe_allow_html=True)
    
    routes = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "visas": page_visas,
        "demande-visa": page_demande_visa,
        "discover-algeria": page_discover_algeria,
        "contact": page_contact,
        "admin": page_admin,
    }
    
    current_page = st.session_state.page
    if current_page in routes:
        routes[current_page]()
    else:
        st.error("❌ Page introuvable")
        st.session_state.page = "accueil"
        st.rerun()

if __name__ == "__main__":
    main()
