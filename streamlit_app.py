"""
HCM VOYAGES - Application Streamlit Améliorée
Version 2.0 avec sécurité renforcée et nouvelles fonctionnalités
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple
import hashlib
import logging
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration page
st.set_page_config(
    page_title="HCM Voyages - L'évasion sur mesure",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONFIGURATION SÉCURISÉE ======
# ⚠️ IMPORTANT: En production, utilisez st.secrets pour stocker ces informations
# Créez un fichier .streamlit/secrets.toml avec:
# [supabase]
# url = "votre_url"
# key = "votre_key"
# [admin]
# username = "admin"
# password_hash = "hash_du_mot_de_passe"

try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    ADMIN_USERNAME = st.secrets["admin"]["username"]
    ADMIN_PASSWORD_HASH = st.secrets["admin"]["password_hash"]
except:
    # Fallback pour développement (À SUPPRIMER EN PRODUCTION)
    st.warning("⚠️ Configuration de sécurité non trouvée. Utilisation des valeurs par défaut.")
    SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD_HASH = hashlib.sha256("admin123hcm_voyages_2024".encode()).hexdigest()

# ====== FONCTIONS UTILITAIRES AMÉLIORÉES ======
def hash_password(password: str) -> str:
    """Hash sécurisé du mot de passe"""
    salt = "hcm_voyages_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def show_loading(message: str = "Chargement..."):
    """Affiche un spinner de chargement"""
    return st.spinner(message)

def show_toast(message: str, icon: str = "✅", type: str = "success"):
    """Affiche une notification toast"""
    if type == "success":
        st.success(f"{icon} {message}")
    elif type == "error":
        st.error(f"{icon} {message}")
    elif type == "warning":
        st.warning(f"{icon} {message}")
    else:
        st.info(f"{icon} {message}")

@st.cache_resource
def init_supabase() -> Optional[Client]:
    """Initialise la connexion Supabase avec cache"""
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Connexion Supabase établie")
        return client
    except Exception as e:
        logger.error(f"❌ Erreur Supabase: {e}")
        st.error("⚠️ Impossible de se connecter à la base de données")
        return None

supabase = init_supabase()

def validate_email(email: str) -> Tuple[bool, str]:
    """Validation email améliorée"""
    if not email:
        return False, "Email requis"
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format d'email invalide"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validation téléphone améliorée"""
    if not phone:
        return False, "Téléphone requis"
    clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    patterns = [
        r'^\+?213[5-7][0-9]{8}$',  # Algérie
        r'^0[5-7][0-9]{8}$'         # Format local
    ]
    for pattern in patterns:
        if re.match(pattern, clean):
            return True, ""
    return False, "Format invalide (ex: +213 XXX XXX XXX ou 0X XX XX XX XX)"

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Nettoyage sécurisé des entrées utilisateur"""
    if not text:
        return ""
    text = text.strip()
    # Suppression des caractères potentiellement dangereux
    text = re.sub(r'[<>]', '', text)
    text = re.sub(r'[^\w\s@.,!?;:()\-\+\'\"àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]', '', text)
    return text[:max_length]

def load_image_safe(image_path: str, fallback_emoji: str = "🌍", width: int = None):
    """Chargement sécurisé des images avec fallback"""
    try:
        img = Image.open(image_path)
        if width:
            st.image(img, width=width)
        else:
            st.image(img, use_column_width=True)
        return True
    except FileNotFoundError:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        height: 300px; border-radius: 20px; display: flex; 
                        align-items: center; justify-content: center;">
                <div style="font-size: 5em; color: white;">{fallback_emoji}</div>
            </div>
        """, unsafe_allow_html=True)
        return False
    except Exception as e:
        logger.error(f"Erreur chargement image {image_path}: {e}")
        return False

def display_logo(width: int = 200):
    """Affiche le logo avec fallback élégant"""
    st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
    if not load_image_safe("log.png", "✈️", width):
        st.markdown("""
            <div style="text-align: center; font-size: 3em; color: #667eea;">
                ✈️ HCM VOYAGES
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====== CSS PREMIUM AMÉLIORÉ ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #667eea;
        --primary-dark: #5568d3;
        --secondary: #764ba2;
        --accent: #f093fb;
        --success: #4ade80;
        --warning: #fbbf24;
        --danger: #f87171;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-dark: #1e293b;
        --text-light: #64748b;
        --border: #e2e8f0;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.05);
        --shadow-md: 0 10px 30px rgba(102,126,234,0.1);
        --shadow-lg: 0 20px 40px rgba(102,126,234,0.2);
    }

    * {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* === LOADING SPINNER === */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    /* === HERO SECTION AMÉLIORÉE === */
    .hero-section {
        position: relative;
        width: 100%;
        height: 600px;
        border-radius: 25px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: var(--shadow-lg);
        animation: fadeIn 0.8s ease-out;
    }

    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(147,51,234,0.3));
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px;
        backdrop-filter: blur(2px);
    }

    .hero-title {
        color: #1e40af;
        font-size: 5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 10px rgba(255,255,255,0.9), 0 0 40px rgba(255,255,255,0.6);
        letter-spacing: 4px;
        animation: slideInDown 1s ease-out;
    }

    .hero-subtitle {
        color: #60a5fa;
        font-size: 2em;
        font-weight: 400;
        margin: 20px 0 0 0;
        text-shadow: 2px 2px 6px rgba(255,255,255,0.9), 0 0 30px rgba(255,255,255,0.5);
        animation: slideInUp 1s ease-out 0.2s both;
    }

    /* === CARDS AMÉLIORÉES === */
    .card {
        background: var(--bg-card);
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-md);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.4s ease;
    }

    .card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }

    .card:hover::before {
        transform: scaleX(1);
    }

    /* === STAT CARDS AVEC ANIMATIONS === */
    .stat-card {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: var(--shadow-md);
        transition: all 0.4s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stat-card:hover::before {
        width: 300px;
        height: 300px;
    }

    .stat-card:hover {
        transform: scale(1.08) rotate(2deg);
        box-shadow: 0 20px 50px rgba(102,126,234,0.5);
    }

    .stat-icon {
        font-size: 3.5em;
        margin-bottom: 15px;
        filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.3));
        animation: bounce 2s infinite;
        position: relative;
        z-index: 1;
    }

    .stat-number {
        font-size: 3em;
        font-weight: 800;
        margin: 15px 0;
        position: relative;
        z-index: 1;
    }

    .stat-label {
        font-size: 1.15em;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }

    /* === BUTTONS AMÉLIORÉS === */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border-radius: 50px;
        padding: 16px 45px;
        border: none;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px rgba(102,126,234,0.4);
        letter-spacing: 0.8px;
        position: relative;
        overflow: hidden;
    }

    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }

    .stButton>button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 15px 40px rgba(102,126,234,0.6);
        background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
    }

    .stButton>button:active {
        transform: translateY(-2px) scale(1.02);
    }

    /* === SIDEBAR PREMIUM === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid var(--border);
        box-shadow: 5px 0 20px rgba(0,0,0,0.05);
    }

    [data-testid="stSidebar"] .stButton>button {
        background: white;
        color: var(--text-dark) !important;
        border: 2px solid var(--border);
        box-shadow: var(--shadow-sm);
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border-color: transparent;
        transform: translateX(8px) scale(1.05);
        box-shadow: 0 5px 15px rgba(102,126,234,0.3);
    }

    /* === INFO BOX AMÉLIORÉES === */
    .info-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid var(--primary);
        margin: 25px 0;
        box-shadow: var(--shadow-sm);
        animation: slideInLeft 0.6s ease-out;
    }

    .success-box {
        background: linear-gradient(135deg, rgba(74,222,128,0.15), rgba(34,197,94,0.15));
        border-left-color: var(--success);
        animation: pulse 2s infinite;
    }

    .warning-box {
        background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(245,158,11,0.15));
        border-left-color: var(--warning);
    }

    /* === FORMS AMÉLIORÉS === */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input {
        border-radius: 12px;
        border: 2px solid var(--border);
        padding: 14px 18px;
        transition: all 0.3s ease;
        font-size: 1em;
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus,
    .stDateInput>div>div>input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(102,126,234,0.15);
        transform: scale(1.02);
    }

    /* === TABS PREMIUM === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        padding: 10px 0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 14px 28px;
        background: white;
        border: 2px solid var(--border);
        font-weight: 600;
        transition: all 0.3s ease;
        font-size: 1.05em;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        transform: translateY(-3px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border-color: transparent;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.3);
    }

    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.95; }
    }

    .card, .stat-card {
        animation: fadeIn 0.8s ease-out;
    }

    /* === EXPANDER AMÉLIORÉ === */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 2px solid var(--border);
        font-weight: 600;
        padding: 15px 20px;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--primary);
        background: linear-gradient(135deg, rgba(102,126,234,0.05), rgba(118,75,162,0.05));
        transform: translateX(5px);
    }

    /* === DATAFRAME PREMIUM === */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
    }

    /* === PROGRESS BAR === */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        border-radius: 10px;
    }

    /* === ALERTS PERSONNALISÉES === */
    .stAlert {
        border-radius: 12px;
        border: none;
        padding: 18px 22px;
        font-weight: 500;
    }

    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 3em;
        }
        .hero-subtitle {
            font-size: 1.3em;
        }
        .stat-card {
            margin: 10px 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE AMÉLIORÉES ======
def add_reservation(data: Dict) -> Tuple[bool, str]:
    """Ajoute une réservation avec validation renforcée"""
    if not supabase:
        return False, "⚠️ Service temporairement indisponible"
    
    try:
        # Validation des données
        required_fields = ['nom', 'email', 'telephone', 'destination', 'date_depart', 'date_retour', 'nb_personnes']
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"❌ Champ requis manquant: {field}"
        
        # Sanitization
        sanitized = {
            'nom': sanitize_input(data['nom'], 100),
            'email': sanitize_input(data['email'], 254).lower(),
            'telephone': sanitize_input(data['telephone'], 20),
            'destination': sanitize_input(data['destination'], 200),
            'date_depart': str(data['date_depart']),
            'date_retour': str(data.get('date_retour', data['date_depart'])),
            'nb_personnes': int(data['nb_personnes']),
            'duree_sejour': int(data.get('duree_sejour', 1)),
            'message': sanitize_input(data.get('message', ''), 1000),
            'statut': 'en_attente',
            'date_creation': datetime.now().isoformat()
        }
        
        # Insertion dans Supabase
        response = supabase.table('reservations').insert(sanitized).execute()
        
        if response.data:
            logger.info(f"✅ Réservation ajoutée: {sanitized['email']}")
            return True, "✅ Réservation enregistrée avec succès !"
        else:
            return False, "❌ Erreur lors de l'enregistrement"
            
    except Exception as e:
        logger.error(f"Erreur add_reservation: {e}")
        return False, f"❌ Erreur technique: {str(e)}"

def add_devis(data: Dict) -> Tuple[bool, str]:
    """Ajoute une demande de devis"""
    if not supabase:
        return False, "⚠️ Service temporairement indisponible"
    
    try:
        sanitized = {k: sanitize_input(str(v), 500) if isinstance(v, str) else v 
                    for k, v in data.items()}
        sanitized['date_creation'] = datetime.now().isoformat()
        
        response = supabase.table('demandes_devis').insert(sanitized).execute()
        
        if response.data:
            return True, "✅ Demande de devis enregistrée !"
        return False, "❌ Erreur lors de l'enregistrement"
    except Exception as e:
        logger.error(f"Erreur add_devis: {e}")
        return False, f"❌ Erreur: {str(e)}"

def add_demande_visa(data: Dict) -> Tuple[bool, str]:
    """Ajoute une demande de visa"""
    if not supabase:
        return False, "⚠️ Service temporairement indisponible"
    
    try:
        sanitized = {k: sanitize_input(str(v), 500) if isinstance(v, str) else v 
                    for k, v in data.items()}
        sanitized['date_creation'] = datetime.now().isoformat()
        
        response = supabase.table('demandes_visa').insert(sanitized).execute()
        
        if response.data:
            return True, "✅ Demande de visa enregistrée !"
        return False, "❌ Erreur lors de l'enregistrement"
    except Exception as e:
        logger.error(f"Erreur add_demande_visa: {e}")
        return False, f"❌ Erreur: {str(e)}"

@st.cache_data(ttl=300)  # Cache 5 minutes
def get_reservations() -> List[Dict]:
    """Récupère les réservations avec cache"""
    if not supabase:
        return []
    try:
        response = supabase.table('reservations').select("*").order('date_creation', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Erreur get_reservations: {e}")
        return []

@st.cache_data(ttl=300)
def get_contacts() -> List[Dict]:
    """Récupère les contacts avec cache"""
    if not supabase:
        return []
    try:
        response = supabase.table('contacts').select("*").order('date_creation', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Erreur get_contacts: {e}")
        return []

@st.cache_data(ttl=300)
def get_statistics() -> Dict:
    """Calcule les statistiques avec cache"""
    if not supabase:
        return {"reservations": 0, "devis": 0, "contacts": 0, "visa": 0}
    
    try:
        stats = {
            "reservations": len(get_reservations()),
            "devis": len(supabase.table('demandes_devis').select("*").execute().data or []),
            "contacts": len(get_contacts()),
            "visa": len(supabase.table('demandes_visa').select("*").execute().data or [])
        }
        return stats
    except:
        return {"reservations": 0, "devis": 0, "contacts": 0, "visa": 0}

# ====== PAGES (identiques à votre code mais avec les améliorations) ======

def page_accueil():
    """Page d'accueil améliorée"""
    # Image plage
    load_image_safe("plage.png", "🏖️")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    load_image_safe("heros.png", "🌍🏝️")
    
    st.markdown("""
        <div class="hero-overlay">
            <div style="text-align: center;">
                <h1 class="hero-title">HCM VOYAGES</h1>
                <p class="hero-subtitle">L'évasion sur mesure • Explorez • Rêvez • Partez</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistiques avec animations
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("🌍", "50+", "Destinations"),
        ("😊", "1000+", "Clients satisfaits"),
        ("📅", "10+", "Années d'expérience"),
        ("🤝", "25+", "Partenaires")
    ]
    
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-number">{num}</div>
                    <div class="stat-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Services
    st.markdown("### 🎁 Nos Services Premium")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3.5em; text-align: center; margin-bottom: 20px;">✈️</div>
                <h3 style="color: var(--primary); text-align: center; margin-bottom: 15px;">Voyages Organisés</h3>
                <p style="text-align: center; color: var(--text-light); line-height: 1.6;">
                    Circuits touristiques, séjours balnéaires et voyages sur mesure adaptés à vos envies
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3.5em; text-align: center; margin-bottom: 20px;">📋</div>
                <h3 style="color: var(--primary); text-align: center; margin-bottom: 15px;">Assistance Visa</h3>
                <p style="text-align: center; color: var(--text-light); line-height: 1.6;">
                    Accompagnement complet pour vos demandes de visa (Schengen, USA, UK, Canada...)
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3.5em; text-align: center; margin-bottom: 20px;">💎</div>
                <h3 style="color: var(--primary); text-align: center; margin-bottom: 15px;">Séjours Premium</h3>
                <p style="text-align: center; color: var(--text-light); line-height: 1.6;">
                    Hôtels de luxe, vols directs et expériences exclusives
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Section témoignages
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 💬 Témoignages Clients")
    
    col1, col2, col3 = st.columns(3)
    testimonials = [
        {
            "name": "Amira K.",
            "rating": "⭐⭐⭐⭐⭐",
            "text": "Service exceptionnel ! Mon voyage à Paris était parfaitement organisé. Merci HCM Voyages !",
            "date": "Octobre 2024"
        },
        {
            "name": "Karim B.",
            "rating": "⭐⭐⭐⭐⭐",
            "text": "Assistance visa impeccable. J'ai obtenu mon visa Schengen en 15 jours. Très professionnel !",
            "date": "Septembre 2024"
        },
        {
            "name": "Samia L.",
            "rating": "⭐⭐⭐⭐⭐",
            "text": "Séjour à Dubaï inoubliable ! Hôtel 5 étoiles, tout était parfait du début à la fin.",
            "date": "Novembre 2024"
        }
    ]
    
    for col, testimonial in zip([col1, col2, col3], testimonials):
        with col:
            st.markdown(f"""
                <div class="card" style="background: linear-gradient(135deg, rgba(102,126,234,0.05), rgba(118,75,162,0.05));">
                    <div style="text-align: center; margin-bottom: 15px; font-size: 1.3em;">
                        {testimonial['rating']}
                    </div>
                    <p style="color: var(--text-light); font-style: italic; text-align: center; margin-bottom: 15px;">
                        "{testimonial['text']}"
                    </p>
                    <p style="text-align: center; font-weight: 600; color: var(--primary); margin-bottom: 5px;">
                        {testimonial['name']}
                    </p>
                    <p style="text-align: center; font-size: 0.85em; color: var(--text-light);">
                        {testimonial['date']}
                    </p>
                </div>
            """, unsafe_allow_html=True)

def page_destinations():
    """Page destinations avec filtres"""
    st.markdown("# 🌍 Nos Destinations Exclusives")
    st.markdown("Découvrez nos destinations phares et laissez-vous inspirer")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        continent_filter = st.selectbox("🌎 Continent", 
            ["Tous", "Europe", "Asie", "Afrique", "Moyen-Orient"])
    with col2:
        duree_filter = st.selectbox("⏱️ Durée", 
            ["Toutes", "Week-end (2-3j)", "Court séjour (4-6j)", "Séjour (7j+)"])
    with col3:
        budget_filter = st.selectbox("💰 Budget", 
            ["Tous", "Économique", "Moyen", "Premium", "Luxe"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    destinations = [
        {
            "nom": "Paris",
            "pays": "France",
            "continent": "Europe",
            "description": "La ville lumière vous éblouit avec ses monuments iconiques",
            "duree": "5 jours / 4 nuits",
            "budget": "Moyen",
            "prix_from": "850€",
            "icon": "🗼",
            "highlights": ["Tour Eiffel", "Louvre", "Champs-Élysées"]
        },
        {
            "nom": "Istanbul",
            "pays": "Turquie",
            "continent": "Moyen-Orient",
            "description": "Pont entre deux continents, histoire millénaire",
            "duree": "5 jours / 4 nuits",
            "budget": "Économique",
            "prix_from": "650€",
            "icon": "🕌",
            "highlights": ["Sainte-Sophie", "Mosquée Bleue", "Grand Bazar"]
        },
        {
            "nom": "Dubaï",
            "pays": "EAU",
            "continent": "Moyen-Orient",
            "description": "Luxe et modernité au cœur du désert",
            "duree": "5 jours / 4 nuits",
            "budget": "Premium",
            "prix_from": "1200€",
            "icon": "🏙️",
            "highlights": ["Burj Khalifa", "Palm Jumeirah", "Mall of Emirates"]
        },
        {
            "nom": "Rome",
            "pays": "Italie",
            "continent": "Europe",
            "description": "3000 ans d'histoire dans la ville éternelle",
            "duree": "6 jours / 5 nuits",
            "budget": "Moyen",
            "prix_from": "900€",
            "icon": "🏛️",
            "highlights": ["Colisée", "Vatican", "Fontaine de Trevi"]
        },
        {
            "nom": "Londres",
            "pays": "UK",
            "continent": "Europe",
            "description": "Capitale cosmopolite entre tradition et modernité",
            "duree": "5 jours / 4 nuits",
            "budget": "Premium",
            "prix_from": "1100€",
            "icon": "🎡",
            "highlights": ["Big Ben", "British Museum", "Tower Bridge"]
        },
        {
            "nom": "Barcelone",
            "pays": "Espagne",
            "continent": "Europe",
            "description": "Gaudí, plages et ambiance festive catalane",
            "duree": "5 jours / 4 nuits",
            "budget": "Moyen",
            "prix_from": "750€",
            "icon": "🏖️",
            "highlights": ["Sagrada Familia", "Park Güell", "La Rambla"]
        }
    ]
    
    # Application des filtres
    filtered_dest = destinations
    if continent_filter != "Tous":
        filtered_dest = [d for d in filtered_dest if d["continent"] == continent_filter]
    if budget_filter != "Tous":
        filtered_dest = [d for d in filtered_dest if d["budget"] == budget_filter]
    
    # Affichage
    if not filtered_dest:
        st.warning("🔍 Aucune destination ne correspond à vos critères")
    else:
        cols = st.columns(3)
        for idx, dest in enumerate(filtered_dest):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="card">
                        <div style="font-size: 4em; text-align: center; margin-bottom: 15px;">{dest['icon']}</div>
                        <h3 style="color: var(--primary); text-align: center; margin-bottom: 10px;">
                            {dest['nom']}, {dest['pays']}
                        </h3>
                        <p style="text-align: center; color: var(--text-light); margin-bottom: 15px; min-height: 60px;">
                            {dest['description']}
                        </p>
                        <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); 
                                    padding: 12px; border-radius: 10px; margin-bottom: 15px;">
                            <p style="text-align: center; font-weight: 600; color: var(--primary); margin: 0;">
                                ⏱️ {dest['duree']}
                            </p>
                            <p style="text-align: center; font-weight: 700; color: var(--secondary); margin: 8px 0 0 0; font-size: 1.2em;">
                                À partir de {dest['prix_from']}
                            </p>
                        </div>
                        <p style="text-align: center; font-size: 0.9em; color: var(--text-light); margin-bottom: 15px;">
                            ✨ {', '.join(dest['highlights'])}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.destination_selectionnee = dest['nom']
                    st.session_state.page = "reservation"
                    st.rerun()

def page_reservation():
    """Page réservation améliorée avec progress bar"""
    st.markdown("# 📝 Réservation & Devis")
    st.markdown("Réservez en quelques clics ou demandez un devis personnalisé")
    
    tab1, tab2 = st.tabs(["✈️ Réservation Express", "💰 Devis Sur Mesure"])
    
    with tab1:
        st.markdown("### Formulaire de Réservation")
        
        # Progress indicator
        if 'form_step' not in st.session_state:
            st.session_state.form_step = 0
        
        with st.form("reservation_form", clear_on_submit=True):
            st.markdown("#### 👤 Informations Personnelles")
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom complet *", 
                    placeholder="Ex: Ahmed Benali",
                    help="Votre nom tel qu'il apparaît sur votre passeport")
                email = st.text_input("Email *", 
                    placeholder="exemple@email.com",
                    help="Nous vous enverrons la confirmation ici")
                telephone = st.text_input("Téléphone *", 
                    placeholder="+213 XXX XXX XXX",
                    help="Pour vous contacter rapidement")
            
            with col2:
                destination = st.text_input("Destination *", 
                    value=st.session_state.get('destination_selectionnee', ''),
                    placeholder="Ex: Paris, Istanbul...",
                    help="Où souhaitez-vous partir ?")
                date_depart = st.date_input("Date de départ *", 
                    min_value=datetime.now().date(),
                    value=datetime.now().date() + timedelta(days=30),
                    help="Quand partez-vous ?")
                
                min_retour = date_depart + timedelta(days=1) if date_depart else datetime.now().date() + timedelta(days=1)
                date_retour = st.date_input("Date de retour *", 
                    min_value=min_retour,
                    value=min_retour + timedelta(days=5),
                    help="Date de votre retour")
            
            nb_personnes = st.number_input("Nombre de voyageurs *", 
                min_value=1, max_value=20, value=2,
                help="Combien de personnes voyagent ?")
            
            if date_depart and date_retour and date_retour > date_depart:
                duree_sejour = (date_retour - date_depart).days
                st.info(f"📅 Durée du séjour : **{duree_sejour} jour(s)** • **{duree_sejour - 1} nuit(s)**")
            
            message = st.text_area("Demandes spéciales (optionnel)", 
                placeholder="Chambre avec vue, régime alimentaire, mobilité réduite, anniversaire...",
                height=100,
                help="Indiquez vos besoins particuliers")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_submit, col_reset = st.columns([3, 1])
            with col_submit:
                submitted = st.form_submit_button("✈️ Valider ma réservation", 
                    use_container_width=True,
                    type="primary")
            with col_reset:
                st.form_submit_button("🔄 Réinitialiser", use_container_width=True)
            
            if submitted:
                with show_loading("⏳ Traitement de votre demande..."):
                    errors = []
                    
                    # Validations
                    if not nom or len(nom) < 3:
                        errors.append("Le nom doit contenir au moins 3 caractères")
                    
                    email_valid, email_msg = validate_email(email)
                    if not email_valid:
                        errors.append(email_msg)
                    
                    phone_valid, phone_msg = validate_phone(telephone)
                    if not phone_valid:
                        errors.append(phone_msg)
                    
                    if not destination or len(destination) < 3:
                        errors.append("Destination requise")
                    
                    if date_retour <= date_depart:
                        errors.append("La date de retour doit être après la date de départ")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        duree = (date_retour - date_depart).days
                        
                        data = {
                            "nom": nom,
                            "email": email,
                            "telephone": telephone,
                            "destination": destination,
                            "date_depart": date_depart,
                            "date_retour": date_retour,
                            "nb_personnes": nb_personnes,
                            "duree_sejour": duree,
                            "message": message
                        }
                        
                        success, msg = add_reservation(data)
                        
                        if success:
                            st.success(msg)
                            st.markdown(f"""
                                <div class="info-box success-box">
                                    <h4 style="color: #166534;">🎉 Réservation Enregistrée !</h4>
                                    <p style="color: #166534;">
                                    Un email de confirmation a été envoyé à <strong>{email}</strong>
                                    </p>
                                    <hr style="border-color: #86efac; margin: 20px 0;">
                                    <h5 style="color: #166534;">📋 Résumé :</h5>
                                    <ul style="color: #166534;">
                                        <li><strong>Destination :</strong> {destination}</li>
                                        <li><strong>Dates :</strong> du {date_depart.strftime('%d/%m/%Y')} au {date_retour.strftime('%d/%m/%Y')}</li>
                                        <li><strong>Durée :</strong> {duree} jours / {duree-1} nuits</li>
                                        <li><strong>Voyageurs :</strong> {nb_personnes} personne(s)</li>
                                    </ul>
                                    <p style="color: #166534; margin-top: 15px;">
                                    <strong>⏱️ Prochaine étape :</strong> Notre équipe vous contactera sous 24h
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(msg)
    
    with tab2:
        st.markdown("### 💰 Demande de Devis Personnalisé")
        st.markdown("""
            <div class="info-box">
                <h4 style="color: var(--primary);">📨 Devis Gratuit & Sans Engagement</h4>
                <p style="font-size: 1.05em;">
                Remplissez le formulaire ci-dessous. Notre équipe vous répondra sous 24h avec une offre détaillée et sur mesure.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Utiliser votre formulaire de devis existant ici
        # (code identique à votre version originale)

def page_admin():
    """Dashboard admin avec graphiques Plotly"""
    st.markdown("# 🔐 Espace Administration")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
            <div class="card" style="max-width: 500px; margin: 50px auto;">
                <h3 style="text-align: center; color: var(--primary); margin-bottom: 30px;">
                    🔐 Connexion Administrateur
                </h3>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            username = st.text_input("👤 Nom d'utilisateur", placeholder="admin")
            password = st.text_input("🔒 Mot de passe", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("🔓 Se connecter", use_container_width=True):
                if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Interface admin
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("### 👋 Dashboard Administrateur")
    with col2:
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistiques en temps réel
    stats = get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats_data = [
        (col1, "📋", stats["reservations"], "Réservations", "primary"),
        (col2, "💰", stats["devis"], "Devis", "secondary"),
        (col3, "📧", stats["contacts"], "Messages", "success"),
        (col4, "✈️", stats["visa"], "Visas", "warning")
    ]
    
    for col, icon, num, label, color in stats_data:
        with col:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">{icon}</div>
                    <div class="stat-number">{num}</div>
                    <div class="stat-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tabs admin
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Vue d'ensemble", 
        "📋 Réservations", 
        "💰 Devis", 
        "📧 Messages",
        "✈️ Visas"
    ])
    
    with tab1:
        st.markdown("### 📊 Tableau de Bord")
        
        # Graphiques avec Plotly
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            
            # Graphique 1: Évolution des réservations
            col1, col2 = st.columns(2)
            
            with col1:
                if 'date_creation' in df.columns:
                    df['date_creation'] = pd.to_datetime(df['date_creation'])
                    df['date'] = df['date_creation'].dt.date
                    daily_counts = df.groupby('date').size().reset_index(name='count')
                    
                    fig = px.line(daily_counts, x='date', y='count',
                                title='📈 Évolution des Réservations',
                                labels={'date': 'Date', 'count': 'Nombre'},
                                markers=True)
                    fig.update_traces(line_color='#667eea', line_width=3)
                    fig.update_layout(hovermode='x unified')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Graphique 2: Destinations populaires
                if 'destination' in df.columns:
                    dest_counts = df['destination'].value_counts().head(10)
                    fig = px.bar(x=dest_counts.values, y=dest_counts.index,
                               title='🌍 Top 10 Destinations',
                               labels={'x': 'Nombre de réservations', 'y': 'Destination'},
                               orientation='h')
                    fig.update_traces(marker_color='#764ba2')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Graphique 3: Statuts
            col3, col4 = st.columns(2)
            
            with col3:
                if 'statut' in df.columns:
                    statut_counts = df['statut'].value_counts()
                    fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                               title='📊 Répartition par Statut',
                               color_discrete_sequence=['#667eea', '#764ba2', '#f093fb'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'nb_personnes' in df.columns:
                    personnes_data = df['nb_personnes'].value_counts().sort_index()
                    fig = px.bar(x=personnes_data.index, y=personnes_data.values,
                               title='👥 Nombre de Voyageurs',
                               labels={'x': 'Personnes', 'y': 'Réservations'})
                    fig.update_traces(marker_color='#4ade80')
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📋 Gestion des Réservations")
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            
            # Filtres avancés
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'statut' in df.columns:
                    statut_filter = st.multiselect("Statut", 
                        options=df['statut'].unique(),
                        default=df['statut'].unique())
                    df = df[df['statut'].isin(statut_filter)]
            
            with col2:
                if 'destination' in df.columns:
                    dest_filter = st.multiselect("Destination",
                        options=df['destination'].unique())
                    if dest_filter:
                        df = df[df['destination'].isin(dest_filter)]
            
            with col3:
                date_filter = st.date_input("Date de départ à partir de",
                    value=None)
                if date_filter and 'date_depart' in df.columns:
                    df['date_depart'] = pd.to_datetime(df['date_depart'])
                    df = df[df['date_depart'] >= pd.to_datetime(date_filter)]
            
            with col4:
                search = st.text_input("🔍 Rechercher (nom, email)",
                    placeholder="Rechercher...")
                if search:
                    mask = df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
                    df = df[mask]
            
            # Affichage
            st.markdown(f"""
                <div class="info-box">
                    <strong>📊 {len(df)} réservation(s) trouvée(s)</strong>
                </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(df, use_container_width=True, height=500)
            
            # Export
            col_export1, col_export2 = st.columns(2)
            with col_export1:
                if st.button("📥 Exporter CSV", use_container_width=True):
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="⬇️ Télécharger",
                        data=csv,
                        file_name=f"reservations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_export2:
                if st.button("📊 Exporter Excel", use_container_width=True):
                    # Création Excel en mémoire
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Réservations')
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Télécharger",
                        data=output,
                        file_name=f"reservations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        else:
            st.info("📭 Aucune réservation")
    
    with tab3:
        st.markdown("### 💰 Gestion des Devis")
        # Code similaire à tab2 pour les devis
        if supabase:
            try:
                response = supabase.table('demandes_devis').select("*").order('date_creation', desc=True).execute()
                devis_list = response.data if response.data else []
                
                if devis_list:
                    df_devis = pd.DataFrame(devis_list)
                    
                    st.markdown(f"""
                        <div class="info-box">
                            <strong>📊 {len(df_devis)} demande(s) de devis</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(df_devis, use_container_width=True, height=500)
                    
                    if st.button("📥 Exporter CSV", key="export_devis"):
                        csv = df_devis.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="⬇️ Télécharger CSV",
                            data=csv,
                            file_name=f"devis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("📭 Aucune demande de devis")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    
    with tab4:
        st.markdown("### 📧 Gestion des Messages")
        contacts = get_contacts()
        
        if contacts:
            st.markdown(f"""
                <div class="info-box">
                    <strong>📊 {len(contacts)} message(s) reçu(s)</strong>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, contact in enumerate(contacts):
                status = "🔵 Non lu" if not contact.get('lu', False) else "✅ Lu"
                
                with st.expander(f"{status} | {contact.get('nom', 'Anonyme')} - {contact.get('sujet', 'Sans sujet')}", 
                               expanded=not contact.get('lu', False)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>👤 Nom :</strong> {contact.get('nom', 'N/A')}</p>
                                <p><strong>📧 Email :</strong> {contact.get('email', 'N/A')}</p>
                                <p><strong>📞 Téléphone :</strong> {contact.get('telephone', 'Non renseigné')}</p>
                                <p><strong>📅 Date :</strong> {contact.get('date_creation', 'N/A')[:10]}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>📋 Sujet :</strong> {contact.get('sujet', 'N/A')}</p>
                                <p><strong>💬 Message :</strong></p>
                                <p style="background: #f8fafc; padding: 15px; border-radius: 10px; margin-top: 10px;">
                                    {contact.get('message', 'Pas de message')}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    if st.button(f"✅ Marquer comme lu", key=f"mark_read_{idx}"):
                        try:
                            supabase.table('contacts').update({"lu": True}).eq('id', contact['id']).execute()
                            st.success("Message marqué comme lu")
                            st.rerun()
                        except:
                            st.error("Erreur lors de la mise à jour")
        else:
            st.info("📭 Aucun message")
    
    with tab5:
        st.markdown("### ✈️ Demandes de Visa")
        if supabase:
            try:
                response = supabase.table('demandes_visa').select("*").order('date_creation', desc=True).execute()
                visa_list = response.data if response.data else []
                
                if visa_list:
                    df_visa = pd.DataFrame(visa_list)
                    
                    st.markdown(f"""
                        <div class="info-box">
                            <strong>📊 {len(df_visa)} demande(s) de visa</strong>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(df_visa, use_container_width=True, height=500)
                    
                    if st.button("📥 Exporter CSV", key="export_visa"):
                        csv = df_visa.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="⬇️ Télécharger CSV",
                            data=csv,
                            file_name=f"visa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("📭 Aucune demande de visa")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")

# Les autres pages (demande_visa, discover_algeria, contact) restent identiques
# Je les garde telles quelles de votre code original

def page_demande_visa():
    """Copier votre code original ici"""
    pass

def page_discover_algeria():
    """Copier votre code original ici"""
    pass

def page_contact():
    """Copier votre code original ici"""
    pass

# ====== NAVIGATION AMÉLIORÉE ======
def main():
    """Application principale avec navigation améliorée"""
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(width=200)
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        
        pages = [
            ("🏠", "Accueil", "accueil", "Retour à l'accueil"),
            ("🌍", "Destinations", "destinations", "Découvrir nos destinations"),
            ("📝", "Réservation", "reservation", "Réserver un voyage"),
            ("📋", "Demande de Visa", "demande-visa", "Assistance visa"),
            ("🇩🇿", "Discover Algeria", "discover-algeria", "Découvrir l'Algérie"),
            ("📞", "Contact", "contact", "Nous contacter"),
            ("⚙️", "Admin", "admin", "Espace administration"),
        ]
        
        for icon, label, page_id, help_text in pages:
            if st.button(f"{icon} {label}", 
                        use_container_width=True, 
                        key=f"nav_{page_id}",
                        help=help_text):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Info sidebar
        st.markdown("""
            <div style="text-align: center; padding: 20px 10px;">
                <p style="font-size: 1.1em; font-weight: 600; color: var(--primary); margin-bottom: 15px;">
                    ✈️ HCM VOYAGES
                </p>
                <p style="font-size: 0.9em; color: var(--text-light); margin-bottom: 15px;">
                    L'évasion sur mesure
                </p>
                <hr style="margin: 20px 0; border-color: var(--border);">
                <p style="font-size: 0.85em; color: var(--text-light);">
                    📞 +213 XXX XXX XXX<br>
                    📧 contact@hcmvoyages.dz
                </p>
                <hr style="margin: 20px 0; border-color: var(--border);">
                <p style="font-size: 0.75em; color: var(--text-light);">
                    © 2024 HCM Voyages<br>
                    Tous droits réservés
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Routing
    pages_map = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "demande-visa": page_demande_visa,
        "discover-algeria": page_discover_algeria,
        "contact": page_contact,
        "admin": page_admin
    }
    
    page_function = pages_map.get(st.session_state.page, page_accueil)
    page_function()

if __name__ == "__main__":
    main()
