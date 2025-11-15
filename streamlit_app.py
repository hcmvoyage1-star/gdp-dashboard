"""
HCM VOYAGES - Application Streamlit avec Contraste Optimisé
Amélioration de l'accessibilité et de la lisibilité
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple
import hashlib

# Configuration de la page (DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT)
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
                <div style="font-size: {size}; color: #ffffff;">✈️</div>
            </div>
        """, unsafe_allow_html=True)

# ====== CSS OPTIMISÉ AVEC MEILLEUR CONTRASTE ======
def load_css():
    """Charge le CSS avec contraste amélioré pour une meilleure accessibilité"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * { 
            font-family: 'Poppins', sans-serif; 
        }
        
        /* Fond plus sombre pour meilleur contraste avec texte blanc */
        .stApp { 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* Responsive - Mobile First */
        @media only screen and (max-width: 768px) {
            h1 { font-size: 1.8em !important; }
            h2 { font-size: 1.5em !important; }
            h3 { font-size: 1.2em !important; }
            
            .hero-section { height: 300px !important; }
            .hero-title { font-size: 2em !important; }
            .hero-subtitle { font-size: 1em !important; }
            
            .carousel-container { height: 350px !important; }
            .carousel-title { font-size: 0.3em !important; }
            .carousel-description { font-size: 0.15em !important; }
            
            .card {
                padding: 15px !important;
                margin: 10px 0 !important;
            }
            
            .price-tag {
                font-size: 18px !important;
                padding: 8px 15px !important;
            }
            
            .stButton>button {
                padding: 15px 25px !important;
                font-size: 16px !important;
                min-height: 50px !important;
            }
            
            .stTextInput input, 
            .stTextArea textarea, 
            .stSelectbox select, 
            .stNumberInput input,
            .stDateInput input {
                font-size: 16px !important;
                padding: 12px !important;
                min-height: 50px !important;
            }
            
            [data-testid="stSidebar"] {
                min-width: 250px !important;
            }
            
            [data-testid="column"] {
                width: 100% !important;
                flex: 100% !important;
                max-width: 100% !important;
            }
            
            .element-container {
                margin-bottom: 15px !important;
            }
            
            label {
                font-size: 16px !important;
            }
        }
        
        /* Tablettes */
        @media only screen and (min-width: 769px) and (max-width: 1024px) {
            .hero-title { font-size: 2.8em !important; }
            .hero-subtitle { font-size: 1.2em !important; }
            .carousel-container { height: 400px !important; }
        }
        
        /* Amélioration du touch sur mobile */
        @media (hover: none) and (pointer: coarse) {
            .stButton>button {
                -webkit-tap-highlight-color: rgba(59, 130, 246, 0.3);
                touch-action: manipulation;
            }
            .card { touch-action: manipulation; }
        }
        
        /* Hero Section */
        .hero-section {
            position: relative;
            width: 100%;
            height: 400px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
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
            color: #0f172a;
            font-size: 3.5em;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            animation: fadeInDown 0.8s ease-out;
            text-align: center;
        }
        
        .hero-subtitle {
            color: #1e293b;
            font-size: 1.5em;
            font-weight: 400;
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
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
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
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
        }
        
        .carousel-content {
            text-align: center;
            color: #ffffff;
            padding: 40px;
        }
        
        .carousel-title {
            font-size: 0.4em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
            color: #ffffff;
        }
        
        .carousel-description {
            font-size: 0.2em;
            font-weight: 300;
            margin-top: 15px;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
            color: #e2e8f0;
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
        
        /* Cards avec meilleur contraste */
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin: 15px 0;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.1);
        }
        
        .card h2, .card h3, .card h4 {
            color: #0f172a !important;
        }
        
        .card p, .card span:not(.badge), .card strong {
            color: #1e293b !important;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            border-color: #3b82f6;
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
        
        /* Buttons avec meilleur contraste */
        .stButton>button {
            background: #3b82f6;
            color: #ffffff;
            border-radius: 25px;
            padding: 12px 30px;
            border: 2px solid #3b82f6;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
            background: #2563eb;
            border-color: #2563eb;
        }
        
        .stButton>button:active {
            transform: translateY(0);
        }
        
        /* Sidebar avec meilleur contraste */
        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 2px solid #e5e7eb;
        }
        
        [data-testid="stSidebar"] * {
            color: #0f172a !important;
        }
        
        [data-testid="stSidebar"] h2 {
            color: #0f172a !important;
            font-weight: 700;
        }
        
        /* Info boxes avec contraste optimisé */
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        }
        
        .info-box h3, .info-box h4, .info-box p, .info-box strong {
            color: #0f172a !important;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left-color: #10b981;
        }
        
        .success-box h3, .success-box h4, .success-box p, .success-box strong {
            color: #064e3b !important;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left-color: #f59e0b;
        }
        
        .warning-box h3, .warning-box h4, .warning-box p, .warning-box strong {
            color: #78350f !important;
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
        
        /* Headers avec contraste blanc fort */
        .accueil-page h1, .accueil-page h2, .accueil-page h3 {
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .accueil-page p:not(.card p):not(.info-box p), 
        .accueil-page label:not(.card label), 
        .accueil-page span:not(.card span):not(.badge) {
            color: #f1f5f9 !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        .other-page h1, .other-page h2, .other-page h3 {
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .other-page > p:not(.card p):not(.info-box p), 
        .other-page > label:not(.card label), 
        .other-page > span:not(.card span):not(.badge),
        .other-page [data-testid="stMarkdownContainer"] > p {
            color: #f1f5f9 !important;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        /* Inputs avec meilleur contraste */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: #ffffff;
            color: #0f172a;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus, .stNumberInput input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }
        
        /* Tabs avec meilleur contraste */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px 10px 0 0;
            color: #ffffff !important;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: white;
            color: #0f172a !important;
            text-shadow: none;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            color: #f1f5f9 !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] h3,
        .stTabs [data-baseweb="tab-panel"] h4 {
            color: #ffffff !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #ffffff;
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: #0f172a !important;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #3b82f6;
        }
        
        .streamlit-expanderContent {
            background-color: white;
        }
        
        .streamlit-expanderContent p, 
        .streamlit-expanderContent span,
        .streamlit-expanderContent strong {
            color: #0f172a !important;
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
            background: #ffffff;
            color: #0f172a;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Messages avec meilleur contraste */
        .stSuccess {
            background: #d1fae5;
            color: #064e3b;
            border: 1px solid #10b981;
        }
        
        .stError {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #dc2626;
        }
        
        .stInfo {
            background: #dbeafe;
            color: #1e3a8a;
            border: 1px solid #3b82f6;
        }
        
        .stWarning {
            background: #fef3c7;
            color: #78350f;
            border: 1px solid #f59e0b;
        }
        
        /* Labels avec meilleur contraste */
        label {
            color: #f1f5f9 !important;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        /* Petits écrans */
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
            <h2 style="color: #0f172a; margin: 5px 0;">{number}</h2>
            <p style="margin: 5px 0 0 0; color: #1e293b;">{label}</p>
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
    
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    carousel_container = st.empty()
    
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Précédent", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(carousel_data)
            st.rerun()
    
    with col2:
        indicators = ""
        for i in range(len(carousel_data)):
            if i == st.session_state.carousel_index:
                indicators += "⬤ "
            else:
                indicators += "○ "
        st.markdown(f"<div style='text-align: center; color: #ffffff; font-size: 1.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>{indicators}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Suivant ▶", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_data)
            st.rerun()

# ====== PAGES ======
def page_accueil():
    """Page d'accueil optimisée"""
    st.markdown('<div class="accueil-page">', unsafe_allow_html=True)
    
    st.markdown('<div class="hero-section"><div class="hero-overlay">', unsafe_allow_html=True)
    display_logo(size="150px")
    st.markdown("""
            <h1 class="hero-title">HCM VOYAGES</h1>
            <p class="hero-subtitle">L'évasion sur mesure, explorez, rêvez, partez</p>
        </div></div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🌍 Découvrez Nos Destinations Phares")
    display_carousel()
    
    st.markdown
