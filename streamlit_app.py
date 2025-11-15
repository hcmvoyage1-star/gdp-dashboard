"""
HCM VOYAGES - Application Streamlit Complète avec Design Premium
Version améliorée avec interface moderne et intuitive
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

# ====== CONFIGURATION SUPABASE ======
SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"

# Credentials admin
def hash_password(password: str) -> str:
    salt = "hcm_voyages_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

ADMIN_CREDENTIALS = {"admin": hash_password("admin123")}

# Initialisation Supabase
@st.cache_resource
def init_supabase() -> Optional[Client]:
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Connexion Supabase établie")
        return client
    except Exception as e:
        logger.error(f"❌ Erreur Supabase: {e}")
        return None

supabase = init_supabase()

# ====== FONCTIONS UTILITAIRES ======
def validate_email(email: str) -> Tuple[bool, str]:
    if not email:
        return False, "Email requis"
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip().lower()):
        return False, "Format d'email invalide"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone:
        return False, "Téléphone requis"
    clean = phone.replace(' ', '').replace('-', '')
    patterns = [r'^\+?213[5-7][0-9]{8}$', r'^0[5-7][0-9]{8}$']
    for pattern in patterns:
        if re.match(pattern, clean):
            return True, ""
    return False, "Format invalide (ex: +213 XXX XXX XXX)"

def sanitize_input(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'[<>]', '', text)
    return text[:max_length]

def display_logo(width: int = None, size: str = None):
    """Affiche le logo centré"""
    try:
        final_width = width
        if size:
            if isinstance(size, str):
                final_width = int(re.sub(r'\D', '', size))
            elif isinstance(size, int):
                final_width = size
        st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=final_width)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<div style="text-align: center; font-size: 4em;">✈️</div>', unsafe_allow_html=True)

def display_home_image(width: int = None):
    """Affiche l'image d'accueil"""
    try:
        img = Image.open("heros.png")
        st.image(img, width=width, use_container_width=(width is None))
    except Exception as e:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        height: 400px; border-radius: 20px; display: flex; 
                        align-items: center; justify-content: center;">
                <div style="font-size: 5em; color: white;">🌍✈️🏝️</div>
            </div>
        """, unsafe_allow_html=True)

# ====== CSS PREMIUM ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
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
    }

    * {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* === HERO SECTION === */
    .hero-section {
        position: relative;
        width: 100%;
        height: 600px;
        border-radius: 25px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
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
    }

    .hero-title {
        color: #1e40af;
        font-size: 5em;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(255,255,255,0.8), 0 0 30px rgba(255,255,255,0.5);
        letter-spacing: 3px;
    }

    .hero-subtitle {
        color: #60a5fa;
        font-size: 2em;
        font-weight: 400;
        margin: 20px 0 0 0;
        text-shadow: 1px 1px 4px rgba(255,255,255,0.8), 0 0 20px rgba(255,255,255,0.4);
    }

    /* === CARDS === */
    .card {
        background: var(--bg-card);
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        border: 1px solid var(--border);
        box-shadow: 0 10px 30px rgba(102,126,234,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102,126,234,0.2);
        border-color: var(--primary);
    }

    .stat-card {
        text-align: center;
        padding: 25px 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 25px rgba(102,126,234,0.3);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 35px rgba(102,126,234,0.4);
    }

    .stat-icon {
        font-size: 3em;
        margin-bottom: 10px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
    }

    .stat-number {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }

    .stat-label {
        font-size: 1.1em;
        font-weight: 300;
        opacity: 0.95;
    }

    /* === BUTTONS === */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border-radius: 50px;
        padding: 14px 40px;
        border: none;
        font-weight: 600;
        font-size: 1.05em;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102,126,234,0.3);
        letter-spacing: 0.5px;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102,126,234,0.5);
        background: linear-gradient(135deg, var(--primary-dark), var(--secondary));
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid var(--border);
    }

    [data-testid="stSidebar"] .stButton>button {
        background: white;
        color: var(--text-dark) !important;
        border: 2px solid var(--border);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin: 8px 0;
    }

    [data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border-color: transparent;
        transform: translateX(5px);
    }

    /* === INFO BOX === */
    .info-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid var(--primary);
        margin: 25px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }

    .success-box {
        background: linear-gradient(135deg, rgba(74,222,128,0.1), rgba(34,197,94,0.1));
        border-left-color: var(--success);
    }

    /* === FORMS === */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border-radius: 12px;
        border: 2px solid var(--border);
        padding: 12px 16px;
        transition: all 0.3s ease;
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        background: white;
        border: 2px solid var(--border);
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
        border-color: transparent;
    }

    /* === ANIMATIONS === */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .card, .stat-card {
        animation: fadeInUp 0.6s ease-out;
    }

    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 2px solid var(--border);
        font-weight: 600;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--primary);
    }

    /* === DATAFRAME === */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======
def add_reservation(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    try:
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
            'statut': 'en_attente'
        }
        supabase.table('reservations').insert(sanitized).execute()
        return True, "✅ Réservation enregistrée avec succès"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def add_devis(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    try:
        sanitized = {k: sanitize_input(str(v), 500) if isinstance(v, str) else v for k, v in data.items()}
        supabase.table('demandes_devis').insert(sanitized).execute()
        return True, "✅ Demande de devis enregistrée"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def add_demande_visa(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    try:
        sanitized = {k: sanitize_input(str(v), 500) if isinstance(v, str) else v for k, v in data.items()}
        supabase.table('demandes_visa').insert(sanitized).execute()
        return True, "✅ Demande de visa enregistrée"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def get_reservations() -> List[Dict]:
    if not supabase:
        return []
    try:
        response = supabase.table('reservations').select("*").order('date_creation', desc=True).execute()
        return response.data if response.data else []
    except:
        return []

def get_contacts() -> List[Dict]:
    if not supabase:
        return []
    try:
        response = supabase.table('contacts').select("*").order('date_creation', desc=True).execute()
        return response.data if response.data else []
    except:
        return []

# ====== PAGES ======
def page_accueil():
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    display_home_image()
    
    st.markdown("""
        <div class="hero-overlay">
            <div style="text-align: center;">
                <h1 class="hero-title" style="color: #1e40af;">HCM VOYAGES</h1>
                <p class="hero-subtitle" style="color: #60a5fa;">L'évasion sur mesure • Explorez • Rêvez • Partez</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistiques
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("🌍", "50+", "Destinations"),
        ("😊", "1000+", "Clients satisfaits"),
        ("📅", "10+", "Années d'expérience"),
        ("🤝", "25+", "Partenaires de confiance")
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
    st.markdown("### 🎁 Nos Services")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">✈️</div>
                <h3 style="color: var(--primary); text-align: center;">Voyages Organisés</h3>
                <p style="text-align: center; color: var(--text-light);">
                    Circuits touristiques, séjours balnéaires et voyages sur mesure adaptés à vos envies
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">📋</div>
                <h3 style="color: var(--primary); text-align: center;">Assistance Visa</h3>
                <p style="text-align: center; color: var(--text-light);">
                    Accompagnement complet pour vos demandes de visa (Schengen, USA, UK, Canada...)
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">💎</div>
                <h3 style="color: var(--primary); text-align: center;">Séjours Premium</h3>
                <p style="text-align: center; color: var(--text-light);">
                    Hôtels de luxe, vols directs et expériences exclusives pour des moments inoubliables
                </p>
            </div>
        """, unsafe_allow_html=True)

def page_destinations():
    st.markdown("# 🌍 Nos Destinations")
    st.markdown("Découvrez nos destinations phares et laissez-vous inspirer pour votre prochain voyage")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    destinations = [
        {
            "nom": "Paris",
            "pays": "France",
            "description": "La ville lumière vous éblouit avec ses monuments iconiques, sa gastronomie raffinée et son art de vivre unique",
            "duree": "5 jours / 4 nuits",
            "icon": "🗼"
        },
        {
            "nom": "Istanbul",
            "pays": "Turquie",
            "description": "Pont entre deux continents, Istanbul fascine par son histoire millénaire et sa culture vibrante",
            "duree": "5 jours / 4 nuits",
            "icon": "🕌"
        },
        {
            "nom": "Dubaï",
            "pays": "Émirats Arabes Unis",
            "description": "Le summum du luxe et de la modernité dans une ville futuriste au cœur du désert",
            "duree": "5 jours / 4 nuits",
            "icon": "🏙️"
        },
        {
            "nom": "Rome",
            "pays": "Italie",
            "description": "La ville éternelle où chaque rue raconte 3000 ans d'histoire et de civilisation",
            "duree": "6 jours / 5 nuits",
            "icon": "🏛️"
        },
        {
            "nom": "Londres",
            "pays": "Royaume-Uni",
            "description": "Capitale cosmopolite alliant tradition britannique et modernité dynamique",
            "duree": "5 jours / 4 nuits",
            "icon": "🎡"
        },
        {
            "nom": "Barcelone",
            "pays": "Espagne",
            "description": "Architecture de Gaudí, plages méditerranéennes et ambiance festive catalane",
            "duree": "5 jours / 4 nuits",
            "icon": "🏖️"
        }
    ]
    
    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="card">
                    <div style="font-size: 3.5em; text-align: center; margin-bottom: 15px;">{dest['icon']}</div>
                    <h3 style="color: var(--primary); text-align: center; margin-bottom: 10px;">
                        {dest['nom']}, {dest['pays']}
                    </h3>
                    <p style="text-align: center; color: var(--text-light); margin-bottom: 15px;">
                        {dest['description']}
                    </p>
                    <p style="text-align: center; font-weight: 600; color: var(--primary);">
                        ⏱️ {dest['duree']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    st.markdown("# 📝 Réservation & Devis")
    st.markdown("Réservez votre voyage de rêve ou demandez un devis personnalisé")
    
    tab1, tab2 = st.tabs(["✈️ Réservation Voyage", "💰 Demande de Devis"])
    
    with tab1:
        st.markdown("### Formulaire de Réservation")
        
        with st.form("reservation_form", clear_on_submit=True):
            st.markdown("#### 👤 Vos Informations")
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom complet *", placeholder="Ex: Ahmed Benali")
                email = st.text_input("Email *", placeholder="exemple@email.com")
                telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            
            with col2:
                destination = st.text_input("Destination *", 
                                           value=st.session_state.get('destination_selectionnee', ''),
                                           placeholder="Ex: Paris, Istanbul...")
                date_depart = st.date_input("Date de départ *", 
                                            min_value=datetime.now().date(),
                                            value=datetime.now().date())
                
                min_retour = date_depart + timedelta(days=1) if date_depart else datetime.now().date() + timedelta(days=1)
                date_retour = st.date_input("Date de retour *", 
                                            min_value=min_retour,
                                            value=min_retour)
            
            nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
            
            if date_depart and date_retour and date_retour > date_depart:
                duree_sejour = (date_retour - date_depart).days
                st.info(f"📅 Durée du séjour : **{duree_sejour} jour(s)**")
            
            message = st.text_area("Message / Demandes spéciales", 
                                  placeholder="Indiquez vos préférences, besoins spéciaux, etc.",
                                  height=120)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("✈️ Envoyer ma demande de réservation", use_container_width=True)
            
            if submitted:
                errors = []
                
                if not nom or len(nom) < 3:
                    errors.append("Le nom doit contenir au moins 3 caractères")
                
                email_valid, email_msg = validate_email(email)
                if not email_valid:
                    errors.append(email_msg)
                
                phone_valid, phone_msg = validate_phone(telephone)
                if not phone_valid:
                    errors.append(phone_msg)
                
                if not destination:
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
                                <h4 style="color: #166534;">📧 Confirmation envoyée !</h4>
                                <p style="color: #166534;">
                                Un email de confirmation a été envoyé à <strong>{email}</strong>
                                </p>
                                <hr style="border-color: #86efac; margin: 20px 0;">
                                <h5 style="color: #166534;">📋 Résumé de votre réservation :</h5>
                                <ul style="color: #166534;">
                                    <li><strong>Destination :</strong> {destination}</li>
                                    <li><strong>Dates :</strong> du {date_depart.strftime('%d/%m/%Y')} au {date_retour.strftime('%d/%m/%Y')} ({duree} jours)</li>
                                    <li><strong>Voyageurs :</strong> {nb_personnes} personne(s)</li>
                                </ul>
                                <p style="color: #166534; margin-top: 15px;">
                                <strong>⏱️ Notre équipe vous contactera dans les 24 heures pour finaliser votre réservation.</strong>
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
                <p style="font-size: 1.05em;">
                <strong>📨 Recevez un devis détaillé et personnalisé</strong><br>
                Indiquez vos dates, destination et préférences. Notre équipe vous répondra sous 24h avec une offre sur mesure.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("devis_form", clear_on_submit=True):
            st.markdown("#### 👤 Vos Coordonnées")
            col1, col2 = st.columns(2)
            
            with col1:
                devis_nom = st.text_input("Nom complet *", placeholder="Votre nom et prénom", key="devis_nom")
                devis_email = st.text_input("Email *", placeholder="votre@email.com", key="devis_email")
                devis_telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX", key="devis_tel")
            
            with col2:
                devis_ville_depart = st.text_input("Ville de départ *", placeholder="Ex: Alger", key="devis_ville_depart")
                devis_nb_adultes = st.number_input("Nombre d'adultes *", min_value=1, max_value=20, value=1, key="devis_adultes")
                devis_nb_enfants = st.number_input("Nombre d'enfants (0-12 ans)", min_value=0, max_value=20, value=0, key="devis_enfants")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🌍 Destination et Dates")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                devis_destination = st.selectbox("Destination *", [
                    "-- Sélectionnez --",
                    "Paris, France",
                    "Istanbul, Turquie", 
                    "Dubaï, EAU",
                    "Londres, UK",
                    "Rome, Italie",
                    "Barcelone, Espagne",
                    "Marrakech, Maroc",
                    "Le Caire, Égypte",
                    "New York, USA",
                    "Tokyo, Japon",
                    "Bali, Indonésie",
                    "Maldives",
                    "Phuket, Thaïlande",
                    "Sydney, Australie",
                    "Autre destination (préciser en commentaire)"
                ], key="devis_dest")
            
            with col4:
                devis_date_depart = st.date_input("Date de départ *", 
                                                   min_value=datetime.now().date(),
                                                   value=datetime.now().date(),
                                                   key="devis_date_dep")
            
            with col5:
                min_retour_devis = devis_date_depart + timedelta(days=1) if devis_date_depart else datetime.now().date() + timedelta(days=1)
                devis_date_retour = st.date_input("Date de retour *", 
                                                   min_value=min_retour_devis,
                                                   value=min_retour_devis,
                                                   key="devis_date_ret")
            
            if devis_date_depart and devis_date_retour and devis_date_retour > devis_date_depart:
                duree_sejour = (devis_date_retour - devis_date_depart).days
                st.info(f"📅 Durée du séjour : **{duree_sejour} jour(s)**")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🏨 Préférences de Voyage")
            
            col6, col7 = st.columns(2)
            
            with col6:
                devis_type_hebergement = st.selectbox("Type d'hébergement *", [
                    "Hôtel 3 étoiles",
                    "Hôtel 4 étoiles",
                    "Hôtel 5 étoiles",
                    "Resort tout inclus",
                    "Appartement/Location",
                    "Auberge de jeunesse",
                    "Pas de préférence"
                ], key="devis_hebergement")
                
                devis_formule = st.selectbox("Formule repas", [
                    "Petit-déjeuner seulement",
                    "Demi-pension (petit-déj + dîner)",
                    "Pension complète (3 repas)",
                    "Tout inclus",
                    "Sans repas"
                ], key="devis_formule")
            
            with col7:
                devis_type_vol = st.selectbox("Type de vol", [
                    "Économique",
                    "Économique Premium",
                    "Affaires",
                    "Première classe",
                    "Vol direct uniquement",
                    "Pas de préférence"
                ], key="devis_vol")
                
                devis_assurance = st.checkbox("Inclure assurance annulation", key="devis_assurance")
                devis_transfert = st.checkbox("Inclure transferts aéroport/hôtel", key="devis_transfert")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 💬 Informations Complémentaires")
            
            devis_activites = st.multiselect("Activités souhaitées", [
                "Visites culturelles",
                "Excursions guidées",
                "Activités nautiques",
                "Randonnée/Nature",
                "Shopping",
                "Gastronomie/Restaurants",
                "Spa/Bien-être",
                "Vie nocturne",
                "Parcs d'attractions"
            ], key="devis_activites")
            
            devis_budget = st.select_slider("Budget approximatif par personne", [
                "Moins de 500€",
                "500€ - 1000€",
                "1000€ - 2000€",
                "2000€ - 3000€",
                "Plus de 3000€",
                "Pas de budget défini"
            ], key="devis_budget")
            
            devis_commentaire = st.text_area(
                "Commentaires / Demandes spéciales",
                placeholder="Ajoutez toute information utile : anniversaire, lune de miel, mobilité réduite, régime alimentaire spécial...",
                height=120,
                key="devis_comment"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted_devis = st.form_submit_button("📨 Recevoir mon devis gratuit", use_container_width=True)
            
            if submitted_devis:
                if not all([devis_nom, devis_email, devis_telephone, devis_destination, 
                           devis_date_depart, devis_date_retour, devis_ville_depart]):
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                elif devis_destination == "-- Sélectionnez --":
                    st.error("❌ Veuillez sélectionner une destination")
                elif devis_date_retour <= devis_date_depart:
                    st.error("❌ La date de retour doit être après la date de départ")
                else:
                    duree = (devis_date_retour - devis_date_depart).days
                    nb_total_personnes = devis_nb_adultes + devis_nb_enfants
                    
                    devis_data = {
                        "nom": devis_nom,
                        "email": devis_email,
                        "telephone": devis_telephone,
                        "ville_depart": devis_ville_depart,
                        "destination": devis_destination,
                        "date_depart": str(devis_date_depart),
                        "date_retour": str(devis_date_retour),
                        "duree_sejour": duree,
                        "nb_adultes": devis_nb_adultes,
                        "nb_enfants": devis_nb_enfants,
                        "nb_total_personnes": nb_total_personnes,
                        "type_hebergement": devis_type_hebergement,
                        "formule_repas": devis_formule,
                        "type_vol": devis_type_vol,
                        "assurance_annulation": devis_assurance,
                        "transferts": devis_transfert,
                        "activites": ", ".join(devis_activites) if devis_activites else "Aucune",
                        "budget_approximatif": devis_budget,
                        "commentaires": devis_commentaire,
                        "statut": "en_attente"
                    }
                    
                    success, msg = add_devis(devis_data)
                    
                    if success:
                        st.success(msg)
                        st.markdown(f"""
                            <div class="info-box success-box">
                                <h4 style="color: #166534;">📧 Demande de devis enregistrée !</h4>
                                <p style="color: #166534;">
                                Un email de confirmation a été envoyé à <strong>{devis_email}</strong>
                                </p>
                                <hr style="border-color: #86efac; margin: 20px 0;">
                                <h5 style="color: #166534;">📋 Résumé de votre demande :</h5>
                                <ul style="color: #166534;">
                                    <li><strong>Destination :</strong> {devis_destination}</li>
                                    <li><strong>Dates :</strong> du {devis_date_depart.strftime('%d/%m/%Y')} au {devis_date_retour.strftime('%d/%m/%Y')} ({duree} jours)</li>
                                    <li><strong>Voyageurs :</strong> {devis_nb_adultes} adulte(s) {f"+ {devis_nb_enfants} enfant(s)" if devis_nb_enfants > 0 else ""}</li>
                                    <li><strong>Budget :</strong> {devis_budget}</li>
                                </ul>
                                <p style="color: #166534; margin-top: 15px;">
                                <strong>⏱️ Délai de réponse :</strong> Vous recevrez votre devis détaillé sous 24 heures ouvrables.
                                </p>
                                <p style="color: #166534;">
                                <strong>📞 Questions urgentes ?</strong> Contactez-nous au +213 XXX XXX XXX
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.error(msg)

def page_demande_visa():
    st.markdown("# 📋 Demande de Visa")
    
    st.markdown("""
        <div class="info-box">
            <h3>🌍 Nos Services d'Assistance Visa</h3>
            <p style="font-size: 1.05em;">
            HCM Voyages vous accompagne dans toutes vos démarches pour l'obtention de visas :
            USA, Royaume-Uni, Espace Schengen, Canada, et bien d'autres destinations.
            </p>
            <p><strong>✅ Notre accompagnement inclut :</strong></p>
            <ul>
                <li>Vérification de vos documents</li>
                <li>Préparation du dossier complet</li>
                <li>Prise de rendez-vous consulaire</li>
                <li>Assistance pour le formulaire</li>
                <li>Suivi de votre demande</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("visa_form", clear_on_submit=True):
        st.markdown("#### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            v_nom = st.text_input("Nom complet *", placeholder="Nom et prénom", key="v_nom")
            v_email = st.text_input("Email *", placeholder="votre@email.com", key="v_email")
            v_tel = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX", key="v_tel")
        
        with col2:
            v_naissance = st.date_input("Date de naissance *", 
                                        min_value=datetime(1920, 1, 1),
                                        max_value=datetime.now().date(),
                                        key="v_naissance")
            v_nationalite = st.text_input("Nationalité *", placeholder="Ex: Algérienne", key="v_nat")
            v_passeport = st.text_input("N° Passeport *", placeholder="Ex: 12345678", key="v_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🌍 Informations sur le Visa")
        
        col3, col4 = st.columns(2)
        
        with col3:
            v_pays = st.selectbox("Pays de destination *", [
                "-- Sélectionnez --",
                "🇺🇸 USA",
                "🇬🇧 Royaume-Uni (UK)",
                "🇫🇷 France (Schengen)",
                "🇩🇪 Allemagne (Schengen)",
                "🇮🇹 Italie (Schengen)",
                "🇪🇸 Espagne (Schengen)",
                "🇨🇦 Canada",
                "🇦🇺 Australie",
                "🇦🇪 Émirats Arabes Unis",
                "🇹🇷 Turquie",
                "Autre pays"
            ], key="v_pays")
            
            v_type = st.selectbox("Type de visa *", [
                "Tourisme",
                "Affaires / Business",
                "Études / Études supérieures",
                "Visite familiale",
                "Transit",
                "Travail",
                "Autre"
            ], key="v_type")
        
        with col4:
            v_depart = st.date_input("Date de départ prévue *", 
                                     min_value=datetime.now().date(),
                                     value=datetime.now().date() + timedelta(days=30),
                                     key="v_depart")
            
            v_duree = st.number_input("Durée du séjour (jours) *", 
                                     min_value=1, 
                                     max_value=365, 
                                     value=15, 
                                     key="v_duree")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📄 Documents et Informations Complémentaires")
        
        v_situation = st.selectbox("Situation professionnelle", [
            "Salarié(e)",
            "Fonctionnaire",
            "Commerçant(e)",
            "Profession libérale",
            "Étudiant(e)",
            "Retraité(e)",
            "Sans emploi",
            "Autre"
        ], key="v_situation")
        
        v_premiere_demande = st.checkbox("C'est ma première demande de visa pour ce pays", 
                                         value=True, 
                                         key="v_premiere")
        
        v_msg = st.text_area("Informations complémentaires / Questions", 
                            placeholder="Ajoutez toute information utile pour votre demande...",
                            height=120,
                            key="v_msg")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        v_accepte = st.checkbox("J'accepte le traitement de mes données personnelles et j'ai lu les conditions générales *", 
                               key="v_accepte")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted_visa = st.form_submit_button("📨 Envoyer ma demande de visa", use_container_width=True)
        
        if submitted_visa:
            if not all([v_nom, v_email, v_tel, v_naissance, v_nationalite, v_passeport, v_accepte]):
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            elif v_pays == "-- Sélectionnez --":
                st.error("❌ Veuillez sélectionner un pays de destination")
            else:
                data = {
                    "nom_complet": v_nom,
                    "email": v_email,
                    "telephone": v_tel,
                    "date_naissance": str(v_naissance),
                    "nationalite": v_nationalite,
                    "numero_passeport": v_passeport,
                    "pays_destination": v_pays,
                    "type_visa": v_type,
                    "date_depart_prevue": str(v_depart),
                    "duree_sejour": v_duree,
                    "situation_professionnelle": v_situation,
                    "premiere_demande": v_premiere_demande,
                    "message_complementaire": v_msg,
                    "statut": "en_attente"
                }
                
                success, msg = add_demande_visa(data)
                
                if success:
                    st.success(msg)
                    st.markdown(f"""
                        <div class="info-box success-box">
                            <h4 style="color: #166534;">📧 Demande de visa enregistrée !</h4>
                            <p style="color: #166534;">
                            Votre demande a été envoyée avec succès. Un email de confirmation a été envoyé à <strong>{v_email}</strong>
                            </p>
                            <hr style="border-color: #86efac; margin: 20px 0;">
                            <h5 style="color: #166534;">📋 Prochaines étapes :</h5>
                            <ol style="color: #166534;">
                                <li>Notre équipe va étudier votre dossier sous 24-48h</li>
                                <li>Vous recevrez la liste des documents à fournir</li>
                                <li>Nous vous assisterons dans la préparation du dossier</li>
                                <li>Prise de rendez-vous consulaire si nécessaire</li>
                            </ol>
                            <p style="color: #166534; margin-top: 15px;">
                            <strong>📞 Contact :</strong> +213 XXX XXX XXX
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(msg)

def page_discover_algeria():
    st.markdown("""
        <div class="hero-section" style="height: 400px;">
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 5em; margin-bottom: 20px;">🇩🇿</div>
                    <h1 class="hero-title" style="font-size: 3.5em;">Discover Algeria</h1>
                    <p class="hero-subtitle">Explorez la beauté et la richesse du Maghreb</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏠 Présentation", "🗺️ Destinations", "🎭 Culture"])
    
    with tab1:
        st.markdown("### 🇩🇿 Bienvenue en Algérie")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="card">
                    <h3 style="color: var(--primary);">Un Pays aux Mille Facettes</h3>
                    <p>
                    L'Algérie, perle du Maghreb, vous invite à découvrir ses trésors cachés.
                    Du Sahara majestueux aux plages méditerranéennes en passant par les montagnes
                    de Kabylie, l'Algérie offre une diversité de paysages à couper le souffle.
                    </p>
                    <p>
                    <strong>🏛️ Patrimoine UNESCO :</strong> 7 sites classés<br>
                    <strong>🏖️ Côte méditerranéenne :</strong> 1200 km<br>
                    <strong>🏜️ Sahara :</strong> 80% du territoire<br>
                    <strong>🗿 Histoire :</strong> 3000 ans de civilisation
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="card">
                    <h3 style="color: var(--primary);">Pourquoi Visiter l'Algérie ?</h3>
                    <ul>
                        <li>🌟 <strong>Patrimoine unique :</strong> Sites romains, villes ottomanes, architecture coloniale</li>
                        <li>🍽️ <strong>Gastronomie riche :</strong> Couscous, tajines, pâtisseries orientales</li>
                        <li>🎨 <strong>Artisanat authentique :</strong> Tapis, poterie, bijoux berbères</li>
                        <li>🤝 <strong>Hospitalité légendaire :</strong> Accueil chaleureux garanti</li>
                        <li>💰 <strong>Prix abordables :</strong> Excellent rapport qualité-prix</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🗺️ Destinations Phares")
        
        destinations_dz = [
            {
                "nom": "Alger",
                "icon": "🏛️",
                "description": "La capitale blanche avec sa célèbre Casbah classée UNESCO, ses musées et son front de mer",
                "highlights": "Casbah, Jardin d'Essai, Mémorial du Martyr"
            },
            {
                "nom": "Oran",
                "icon": "🌊",
                "description": "Ville portuaire méditerranéenne, capitale du raï et de la joie de vivre",
                "highlights": "Fort Santa Cruz, Chapelle Santa Cruz, Front de mer"
            },
            {
                "nom": "Constantine",
                "icon": "🌉",
                "description": "La ville des ponts suspendus, perchée sur un rocher spectaculaire",
                "highlights": "Pont Sidi M'Cid, Palais Ahmed Bey, Gorges du Rhumel"
            },
            {
                "nom": "Sahara (Tamanrasset)",
                "icon": "🏜️",
                "description": "Le plus grand désert du monde, dunes majestueuses et nuits étoilées inoubliables",
                "highlights": "Assekrem, Hoggar, Bivouac dans les dunes"
            },
            {
                "nom": "Tlemcen",
                "icon": "🕌",
                "description": "La perle du Maghreb, cité millénaire aux influences andalouses",
                "highlights": "Grande Mosquée, Mansourah, Grottes de Beni Add"
            },
            {
                "nom": "Tipaza",
                "icon": "⛱️",
                "description": "Ruines romaines face à la mer Méditerranée, site UNESCO exceptionnel",
                "highlights": "Ruines romaines, Tombeau Maurétanien, Plages"
            }
        ]
        
        cols = st.columns(3)
        for idx, dest in enumerate(destinations_dz):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="card">
                        <div style="font-size: 3.5em; text-align: center; margin-bottom: 15px;">{dest['icon']}</div>
                        <h3 style="color: var(--primary); text-align: center; margin-bottom: 10px;">
                            {dest['nom']}
                        </h3>
                        <p style="text-align: center; color: var(--text-light); margin-bottom: 15px;">
                            {dest['description']}
                        </p>
                        <p style="text-align: center; font-size: 0.9em; color: var(--primary); font-weight: 600;">
                            ✨ {dest['highlights']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🎭 Culture et Traditions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="card">
                    <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">🍽️</div>
                    <h3 style="color: var(--primary); text-align: center;">Gastronomie</h3>
                    <ul style="font-size: 0.95em;">
                        <li>Couscous traditionnel</li>
                        <li>Tajine aux pruneaux</li>
                        <li>Chorba algéroise</li>
                        <li>Méchoui et merguez</li>
                        <li>Pâtisseries orientales</li>
                        <li>Thé à la menthe</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="card">
                    <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">🎨</div>
                    <h3 style="color: var(--primary); text-align: center;">Artisanat</h3>
                    <ul style="font-size: 0.95em;">
                        <li>Tapis berbères</li>
                        <li>Poterie de Kabylie</li>
                        <li>Bijoux en argent</li>
                        <li>Dinanderie de Constantine</li>
                        <li>Cuir repoussé</li>
                        <li>Vannerie traditionnelle</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="card">
                    <div style="font-size: 3em; text-align: center; margin-bottom: 15px;">🎵</div>
                    <h3 style="color: var(--primary); text-align: center;">Musique</h3>
                    <ul style="font-size: 0.95em;">
                        <li>Raï d'Oran</li>
                        <li>Chaâbi algérois</li>
                        <li>Musique andalouse</li>
                        <li>Chants kabyles</li>
                        <li>Musique saharienne</li>
                        <li>Gnawa</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

def page_contact():
    st.markdown("# 📞 Contactez-Nous")
    st.markdown("Notre équipe est à votre écoute pour répondre à toutes vos questions et vous accompagner dans vos projets de voyage")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h3 style="color: var(--primary); border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px;">
                    📍 Informations de Contact
                </h3>
                
                <div style="padding: 15px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">🏢</div>
                    <strong style="color: var(--primary);">Adresse :</strong><br>
                    <span style="color: var(--text-light);">
                    Aïn Benian, Alger<br>
                    Algérie 16061
                    </span>
                </div>
                
                <div style="padding: 15px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">📞</div>
                    <strong style="color: var(--primary);">Téléphone :</strong><br>
                    <span style="color: var(--text-light);">+213 XXX XXX XXX</span>
                </div>
                
                <div style="padding: 15px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">📱</div>
                    <strong style="color: var(--primary);">WhatsApp :</strong><br>
                    <span style="color: var(--text-light);">+213 XXX XXX XXX</span>
                </div>
                
                <div style="padding: 15px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">📧</div>
                    <strong style="color: var(--primary);">Email :</strong><br>
                    <span style="color: var(--text-light);">contact@hcmvoyages.dz</span>
                </div>
                
                <div style="padding: 15px 0;">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">🕐</div>
                    <strong style="color: var(--primary);">Horaires d'ouverture :</strong><br>
                    <span style="color: var(--text-light);">
                    Dimanche - Jeudi: 9h00 - 18h00<br>
                    Samedi: 9h00 - 13h00<br>
                    Vendredi: Fermé
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card">
                <h3 style="color: var(--primary); border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px;">
                    🌐 Suivez-nous sur les Réseaux Sociaux
                </h3>
                
                <div style="padding: 12px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">📘</div>
                    <strong style="color: var(--primary);">Facebook :</strong>
                    <span style="color: var(--text-light);"> @HCMVoyages</span>
                </div>
                
                <div style="padding: 12px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">📷</div>
                    <strong style="color: var(--primary);">Instagram :</strong>
                    <span style="color: var(--text-light);"> @hcm_voyages</span>
                </div>
                
                <div style="padding: 12px 0; border-bottom: 1px solid var(--border);">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">🐦</div>
                    <strong style="color: var(--primary);">Twitter :</strong>
                    <span style="color: var(--text-light);"> @HCMVoyages</span>
                </div>
                
                <div style="padding: 12px 0;">
                    <div style="font-size: 1.3em; margin-bottom: 8px;">💼</div>
                    <strong style="color: var(--primary);">LinkedIn :</strong>
                    <span style="color: var(--text-light);"> HCM Voyages</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3 style="color: var(--primary); border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px;">
                    💬 Envoyez-nous un Message
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom complet *", placeholder="Votre nom et prénom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone", placeholder="+213 XXX XXX XXX")
            
            sujet = st.selectbox("Sujet de votre message *", [
                "-- Sélectionnez --",
                "💼 Demande d'information générale",
                "✈️ Question sur une réservation",
                "📋 Question sur un visa",
                "💰 Demande de devis",
                "😊 Réclamation ou suggestion",
                "🤝 Proposition de partenariat",
                "📞 Demande de rappel",
                "🎯 Autre sujet"
            ])
            
            message = st.text_area("Votre message *", 
                                  placeholder="Décrivez votre demande en détail. Plus vous serez précis, mieux nous pourrons vous aider...",
                                  height=200)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📨 Envoyer le message", use_container_width=True)
            
            if submitted:
                errors = []
                
                if not nom or len(nom) < 3:
                    errors.append("Le nom doit contenir au moins 3 caractères")
                
                email_valid, email_msg = validate_email(email)
                if not email_valid:
                    errors.append(email_msg)
                
                if telephone:
                    phone_valid, phone_msg = validate_phone(telephone)
                    if not phone_valid:
                        errors.append(phone_msg)
                
                if sujet == "-- Sélectionnez --":
                    errors.append("Veuillez sélectionner un sujet")
                
                if not message or len(message) < 10:
                    errors.append("Le message doit contenir au moins 10 caractères")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    contact_data = {
                        "nom": nom,
                        "email": email,
                        "telephone": telephone if telephone else "",
                        "sujet": sujet,
                        "message": message
                    }
                    
                    if supabase:
                        try:
                            sanitized = {
                                'nom': sanitize_input(contact_data['nom'], 100),
                                'email': sanitize_input(contact_data['email'], 254).lower(),
                                'telephone': sanitize_input(contact_data['telephone'], 20),
                                'sujet': sanitize_input(contact_data['sujet'], 200),
                                'message': sanitize_input(contact_data['message'], 2000),
                                'lu': False
                            }
                            supabase.table('contacts').insert(sanitized).execute()
                            
                            st.success("✅ Message envoyé avec succès!")
                            st.markdown("""
                                <div class="info-box success-box">
                                    <h4 style="color: #166534;">📧 Confirmation d'Envoi</h4>
                                    <p style="color: #166534;">
                                    Votre message a bien été enregistré. Notre équipe vous répondra dans les plus brefs délais.
                                    </p>
                                    <hr style="border-color: #86efac; margin: 15px 0;">
                                    <p style="color: #166534;">
                                    <strong>⏱️ Délai de réponse habituel :</strong> 24 heures ouvrables
                                    </p>
                                    <p style="color: #166534;">
                                    <strong>📞 Besoin urgent ?</strong> Appelez-nous directement au +213 XXX XXX XXX
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'envoi: {str(e)}")
                    else:
                        st.warning("⚠️ Service temporairement indisponible. Veuillez nous contacter directement par téléphone.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <h4 style="color: var(--primary); margin-bottom: 10px;">⚡ Engagement Qualité</h4>
                <p style="margin-bottom: 8px;">
                ✅ <strong>Réponse rapide :</strong> Tous les messages reçoivent une réponse sous 24h ouvrables
                </p>
                <p style="margin-bottom: 8px;">
                ✅ <strong>Disponibilité :</strong> Notre équipe est disponible du dimanche au jeudi
                </p>
                <p style="margin-bottom: 0;">
                ✅ <strong>Confidentialité :</strong> Vos données sont protégées et ne sont jamais partagées
                </p>
            </div>
        """, unsafe_allow_html=True)

def page_admin():
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
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("🔓 Se connecter", use_container_width=True):
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hash_password(password):
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
        st.markdown("### 👋 Bienvenue dans l'espace d'administration")
    with col2:
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Réservations", "💰 Devis", "📧 Messages", "📊 Statistiques"])
    
    with tab1:
        st.markdown("### 📋 Gestion des Réservations")
        reservations = get_reservations()
        
        if reservations:
            st.markdown(f"""
                <div class="info-box">
                    <strong>📊 Total des réservations :</strong> {len(reservations)}
                </div>
            """, unsafe_allow_html=True)
            
            df = pd.DataFrame(reservations)
            
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'statut' in df.columns:
                    statut_filter = st.multiselect("Filtrer par statut", 
                                                   options=df['statut'].unique(),
                                                   default=df['statut'].unique())
                    df = df[df['statut'].isin(statut_filter)]
            
            with col2:
                if 'destination' in df.columns:
                    dest_filter = st.multiselect("Filtrer par destination",
                                                 options=df['destination'].unique())
                    if dest_filter:
                        df = df[df['destination'].isin(dest_filter)]
            
            # Affichage du tableau
            st.dataframe(df, use_container_width=True, height=400)
            
            # Export
            if st.button("📥 Exporter en CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Télécharger le fichier CSV",
                    data=csv,
                    file_name=f"reservations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("📭 Aucune réservation pour le moment")
    
    with tab2:
        st.markdown("### 💰 Gestion des Demandes de Devis")
        
        if supabase:
            try:
                response = supabase.table('demandes_devis').select("*").order('date_creation', desc=True).execute()
                devis_list = response.data if response.data else []
                
                if devis_list:
                    st.markdown(f"""
                        <div class="info-box">
                            <strong>📊 Total des demandes de devis :</strong> {len(devis_list)}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    df_devis = pd.DataFrame(devis_list)
                    st.dataframe(df_devis, use_container_width=True, height=400)
                    
                    if st.button("📥 Exporter devis en CSV"):
                        csv = df_devis.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Télécharger le fichier CSV",
                            data=csv,
                            file_name=f"devis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("📭 Aucune demande de devis")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
        else:
            st.warning("⚠️ Base de données non connectée")
    
    with tab3:
        st.markdown("### 📧 Gestion des Messages")
        contacts = get_contacts()
        
        if contacts:
            st.markdown(f"""
                <div class="info-box">
                    <strong>📊 Total des messages :</strong> {len(contacts)}
                </div>
            """, unsafe_allow_html=True)
            
            for contact in contacts:
                status = "🔵 Non lu" if not contact.get('lu', False) else "✅ Lu"
                
                with st.expander(f"{status} | {contact.get('nom', 'Anonyme')} - {contact.get('sujet', 'Sans sujet')}", expanded=not contact.get('lu', False)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>👤 Nom :</strong> {contact.get('nom', 'N/A')}</p>
                                <p><strong>📧 Email :</strong> {contact.get('email', 'N/A')}</p>
                                <p><strong>📞 Téléphone :</strong> {contact.get('telephone', 'Non renseigné')}</p>
                                <p><strong>📅 Date :</strong> {contact.get('date_creation', 'N/A')}</p>
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
        else:
            st.info("📭 Aucun message pour le moment")
    
    with tab4:
        st.markdown("### 📊 Statistiques Générales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        reservations = get_reservations()
        contacts = get_contacts()
        
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-number">{len(reservations)}</div>
                    <div class="stat-label">Réservations</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            devis_count = 0
            if supabase:
                try:
                    response = supabase.table('demandes_devis').select("*", count='exact').execute()
                    devis_count = len(response.data) if response.data else 0
                except:
                    pass
            
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">💰</div>
                    <div class="stat-number">{devis_count}</div>
                    <div class="stat-label">Devis</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📧</div>
                    <div class="stat-number">{len(contacts)}</div>
                    <div class="stat-label">Messages</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            visa_count = 0
            if supabase:
                try:
                    response = supabase.table('demandes_visa').select("*", count='exact').execute()
                    visa_count = len(response.data) if response.data else 0
                except:
                    pass
            
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-number">{visa_count}</div>
                    <div class="stat-label">Demandes Visa</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Graphiques
        if reservations:
            st.markdown("### 📈 Évolution des Réservations")
            
            df_res = pd.DataFrame(reservations)
            if 'date_creation' in df_res.columns:
                df_res['date_creation'] = pd.to_datetime(df_res['date_creation'])
                df_res['date'] = df_res['date_creation'].dt.date
                
                daily_counts = df_res.groupby('date').size().reset_index(name='count')
                st.line_chart(daily_counts.set_index('date'))

# ====== NAVIGATION ======
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(size="120px")
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Destinations", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📋", "Demande de Visa", "demande-visa"),
            ("🇩🇿", "Discover Algeria", "discover-algeria"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Admin", "admin"),
        ]
        
        for icon, label, page_id in pages:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
            <div style="text-align: center; padding: 20px 10px;">
                <p style="font-size: 0.9em; color: var(--text-light); margin-bottom: 15px;">
                    <strong>HCM Voyages</strong><br>
                    L'évasion sur mesure
                </p>
                <p style="font-size: 0.85em; color: var(--text-light);">
                    📞 +213 XXX XXX XXX<br>
                    📧 contact@hcmvoyages.dz
                </p>
                <hr style="margin: 20px 0; border-color: var(--border);">
                <p style="font-size: 0.8em; color: var(--text-light);">
                    © 2024 HCM Voyages<br>
                    Tous droits réservés
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Affichage de la page
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "destinations":
        page_destinations()
    elif st.session_state.page == "reservation":
        page_reservation()
    elif st.session_state.page == "demande-visa":
        page_demande_visa()
    elif st.session_state.page == "discover-algeria":
        page_discover_algeria()
    elif st.session_state.page == "contact":
        page_contact()
    elif st.session_state.page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
