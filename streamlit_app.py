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
        
        * { font-family: 'Poppins', sans-serif; }
        .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); }
        
        /* Mobile First */
        @media only screen and (max-width: 768px) {
            h1 { font-size: 1.8em !important; }
            h2 { font-size: 1.5em !important; }
            h3 { font-size: 1.2em !important; }
            .hero-section { height: 300px !important; }
            .hero-title { font-size: 2em !important; }
            .hero-subtitle { font-size: 1em !important; }
            .carousel-container { height: 350px !important; }
            .card { padding: 15px !important; margin: 10px 0 !important; }
            .stButton>button { padding: 15px 25px !important; font-size: 16px !important; min-height: 50px !important; }
        }
        
        /* Hero Section */
        .hero-section {
            position: relative; width: 100%; height: 400px; border-radius: 20px;
            overflow: hidden; margin-bottom: 40px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            background: white;
        }
        .hero-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px;
        }
        .hero-title {
            color: #1e40af; font-size: 3.5em; font-weight: 700; margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1); animation: fadeInDown 0.8s ease-out; text-align: center;
        }
        .hero-subtitle {
            color: #2563eb; font-size: 1.5em; font-weight: 300; margin: 20px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1); animation: fadeInUp 0.8s ease-out 0.2s backwards; text-align: center;
        }
        
        /* Carousel */
        .carousel-container {
            position: relative; width: 100%; height: 500px; border-radius: 20px;
            overflow: hidden; margin: 30px 0; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        .carousel-slide {
            position: absolute; width: 100%; height: 100%; display: flex;
            align-items: center; justify-content: center; font-size: 8em;
            animation: slideIn 0.5s ease-out;
            background: linear-gradient(135deg, rgba(30, 64, 175, 0.9), rgba(37, 99, 235, 0.9));
        }
        .carousel-content { text-align: center; color: white; padding: 40px; }
        .carousel-title { font-size: 0.4em; font-weight: 700; margin-bottom: 20px; text-shadow: 2px 2px 8px rgba(0,0,0,0.3); }
        .carousel-description { font-size: 0.2em; font-weight: 300; margin-top: 15px; text-shadow: 1px 1px 4px rgba(0,0,0,0.3); }
        
        @keyframes slideIn { from { opacity: 0; transform: translateX(100px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Cards */
        .card {
            background: white; padding: 25px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); margin: 15px 0;
            transition: all 0.3s ease; border: 2px solid rgba(255, 255, 255, 0.1);
        }
        .card h2, .card h3, .card h4 { color: #1e3a8a !important; }
        .card p, .card span:not(.badge), .card strong { color: #1e3a8a !important; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4); border-color: #1e3a8a; }
        
        .price-tag {
            color: #dc2626; font-size: 24px; font-weight: 700; margin-top: 15px;
            display: inline-block; padding: 10px 20px;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px;
        }
        
        /* Buttons */
        .stButton>button {
            background: white; color: #1e40af; border-radius: 25px; padding: 12px 30px;
            border: 2px solid white; font-weight: 600; transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); width: 100%;
        }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3); background: #f8fafc; }
        
        /* Sidebar */
        [data-testid="stSidebar"] { background: white; border-right: 2px solid #e5e7eb; }
        [data-testid="stSidebar"] * { color: #1e40af !important; }
        
        /* Info boxes */
        .info-box {
            background: white; padding: 20px; border-radius: 12px;
            border-left: 4px solid white; margin: 20px 0; box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }
        .info-box h3, .info-box h4, .info-box p, .info-box strong { color: #1e3a8a !important; }
        .success-box { background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left-color: #10b981; }
        .success-box h3, .success-box h4, .success-box p, .success-box strong { color: #065f46 !important; }
        
        /* Badge */
        .badge {
            display: inline-block; padding: 5px 12px; border-radius: 20px;
            font-size: 0.85em; font-weight: 600; margin: 0 5px;
        }
        .badge-success { background: #10b981; color: white; }
        .badge-warning { background: #f59e0b; color: white; }
        .badge-danger { background: #dc2626; color: white; }
        .badge-info { background: #3b82f6; color: white; }
        
        /* Headers */
        .accueil-page h1, .accueil-page h2, .accueil-page h3 { color: white !important; }
        .other-page h1, .other-page h2, .other-page h3 { color: white !important; }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
            border-radius: 10px; border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.95); color: #1e40af; transition: all 0.3s ease;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.2); border-radius: 10px 10px 0 0;
            color: white !important; font-weight: 500;
        }
        .stTabs [aria-selected="true"] { background: white; color: #1e3a8a !important; }
        </style>
    """, unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======
@st.cache_data(ttl=300)
def get_destinations() -> List[Dict]:
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Erreur: {e}")
    return []

def add_reservation(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "Base de données non connectée"
    try:
        data['statut'] = 'en_attente'
        data['date_creation'] = datetime.now().isoformat()
        response = supabase.table('reservations').insert(data).execute()
        get_statistics.clear()
        return True, "Réservation enregistrée avec succès"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def get_reservations(limit: Optional[int] = None) -> List[Dict]:
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
    if supabase:
        try:
            supabase.table('reservations').update({"statut": new_status}).eq('id', reservation_id).execute()
            get_statistics.clear()
            return True
        except:
            return False
    return False

def add_contact(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "Base de données non connectée"
    try:
        data['lu'] = False
        data['date_creation'] = datetime.now().isoformat()
        supabase.table('contacts').insert(data).execute()
        get_statistics.clear()
        return True, "Message envoyé avec succès"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def get_contacts(unread_only: bool = False) -> List[Dict]:
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
    if supabase:
        try:
            supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            get_statistics.clear()
            return True
        except:
            return False
    return False

@st.cache_data(ttl=60)
def get_statistics() -> Dict:
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

def display_stat_card(icon: str, number: str, label: str):
    st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
            <h2 style="color: #1e40af; margin: 5px 0;">{number}</h2>
            <p style="margin: 5px 0 0 0; color: #374151;">{label}</p>
        </div>
    """, unsafe_allow_html=True)

def display_carousel():
    carousel_data = [
        {"emoji": "🗼", "title": "Paris, France", "description": "La Ville Lumière vous attend"},
        {"emoji": "🕌", "title": "Istanbul, Turquie", "description": "Entre Orient et Occident"},
        {"emoji": "🏝️", "title": "Maldives", "description": "Paradis tropical aux eaux cristallines"},
        {"emoji": "🏛️", "title": "Rome, Italie", "description": "L'histoire antique prend vie"},
        {"emoji": "🌴", "title": "Dubaï, EAU", "description": "Luxe et modernité dans le désert"}
    ]
    
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    current_slide = carousel_data[st.session_state.carousel_index]
    
    st.markdown(f"""
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
    with col3:
        if st.button("Suivant ▶", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_data)
            st.rerun()

# ====== PAGES ======
def page_accueil():
    st.markdown('<div class="accueil-page">', unsafe_allow_html=True)
    st.markdown('<div class="hero-section"><div class="hero-overlay">', unsafe_allow_html=True)
    display_logo(size="150px")
    st.markdown('<h1 class="hero-title">HCM VOYAGES</h1><p class="hero-subtitle">L\'évasion sur mesure</p></div></div>', unsafe_allow_html=True)
    
    st.markdown("### 🌍 Découvrez Nos Destinations Phares")
    display_carousel()
    
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    with col1: display_stat_card("🌍", "50+", "Destinations")
    with col2: display_stat_card("😊", "1000+", "Clients Satisfaits")
    with col3: display_stat_card("📅", "10+", "Années")
    with col4: display_stat_card("🤝", "25+", "Partenaires")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_destinations():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 🌍 Nos Voyages Organisés")
    
    destinations = [
        {"nom": "Istanbul", "pays": "Turquie", "description": "La ville des deux continents", "duree": "5 jours / 4 nuits"},
        {"nom": "Antalya", "pays": "Turquie", "description": "Perle de la Riviera turque", "duree": "7 jours / 6 nuits"},
        {"nom": "Maldives", "pays": "Maldives", "description": "Le paradis sur terre", "duree": "8 jours / 7 nuits"}
    ]
    
    cols = st.columns(2)
    for idx, dest in enumerate(destinations):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="card">
                    <h2>📍 {dest['nom']}</h2>
                    <h4>{dest['pays']}</h4>
                    <p>{dest['description']}</p>
                    <p>⏱️ {dest['duree']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def page_reservation():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📝 Réserver Votre Voyage")
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
        with col2:
            destination = st.text_input("Destination *", value=st.session_state.get('destination_selectionnee', ''))
            telephone = st.text_input("Téléphone *")
        
        submitted = st.form_submit_button("✈️ Envoyer", use_container_width=True)
        if submitted:
            if all([nom, email, destination, telephone]):
                st.success("✅ Réservation enregistrée!")
                st.balloons()
            else:
                st.error("❌ Veuillez remplir tous les champs")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_contact():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# 📞 Contactez-Nous")
    st.markdown("""
        <div class="card">
            <h3>📍 Notre Agence</h3>
            <p><strong>📞 Téléphone:</strong> +213 783 80 27 12</p>
            <p><strong>📧 Email:</strong> hcmvoyage1@gmail.com</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def page_admin():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        with st.form("login_form"):
            username = st.text_input("Utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion"):
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hash_password(password):
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
    else:
        st.markdown("# Dashboard Admin")
        stats = get_statistics()
        col1, col2, col3 = st.columns(3)
        with col1: display_stat_card("📋", str(stats['total_reservations']), "Réservations")
        with col2: display_stat_card("⏳", str(stats['reservations_en_attente']), "En attente")
        with col3: display_stat_card("✅", str(stats['reservations_confirmees']), "Confirmées")
        
        if st.button("Déconnexion"):
            st.session_state.admin_logged = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    load_css()
    
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(size="120px")
        st.markdown('<h2 style="text-align: center;">HCM VOYAGES</h2>', unsafe_allow_html=True)
        st.markdown("---")
        
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Destinations", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Admin", "admin")
        ]
        
        for icon, label, page_id in pages:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
    
    routes = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "contact": page_contact,
        "admin": page_admin
    }
    
    if st.session_state.page in routes:
        routes[st.session_state.page]()

if __name__ == "__main__":
    main()
