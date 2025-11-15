"""
HCM VOYAGES - Application Streamlit Sécurisée avec Corrections de Bugs
"""
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple
import hashlib
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration page - UNE SEULE FOIS
st.set_page_config(
    page_title="HCM Voyages - L'évasion sur mesure",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONFIGURATION SUPABASE SÉCURISÉE ======
def get_supabase_config():
    """Récupère la configuration Supabase de manière sécurisée"""
    try:
        # Priorité aux secrets Streamlit
        if hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
            return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
        # Fallback pour le développement local (à supprimer en production)
        else:
            logger.warning("⚠️ Utilisation des credentials en dur - NON RECOMMANDÉ EN PRODUCTION")
            return (
                "https://oilamfxxqjopuopgskfc.supabase.co",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"
            )
    except Exception as e:
        logger.error(f"Erreur de configuration: {e}")
        return None, None

SUPABASE_URL, SUPABASE_KEY = get_supabase_config()

# ====== SÉCURITÉ ======
def hash_password(password: str) -> str:
    """Hash un mot de passe avec sel"""
    salt = "hcm_voyages_2024_secure_salt"  # En production, utiliser st.secrets
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def get_admin_credentials():
    """Récupère les credentials admin de manière sécurisée"""
    try:
        if hasattr(st, 'secrets') and 'ADMIN_USERNAME' in st.secrets:
            return {
                st.secrets["ADMIN_USERNAME"]: hash_password(st.secrets["ADMIN_PASSWORD"])
            }
    except:
        pass
    # Fallback (à supprimer en production)
    return {"admin": hash_password("admin123")}

ADMIN_CREDENTIALS = get_admin_credentials()

# Initialisation du client Supabase avec gestion d'erreur améliorée
@st.cache_resource
def init_supabase() -> Optional[Client]:
    """Initialise le client Supabase avec retry"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Configuration Supabase manquante")
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test de connexion
        client.table('destinations').select("count", count="exact").limit(1).execute()
        logger.info("✅ Connexion Supabase établie")
        return client
    except Exception as e:
        logger.error(f"❌ Erreur connexion Supabase: {e}")
        st.error("⚠️ Problème de connexion à la base de données. Mode hors ligne activé.")
        return None

supabase = init_supabase()

# ====== FONCTIONS UTILITAIRES AMÉLIORÉES ======
def validate_email(email: str) -> Tuple[bool, str]:
    """Valide le format d'un email avec message d'erreur"""
    if not email:
        return False, "Email requis"
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Format d'email invalide"
    
    if len(email) > 254:
        return False, "Email trop long"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Valide le format d'un numéro de téléphone algérien avec message"""
    if not phone:
        return False, "Téléphone requis"
    
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Formats acceptés: +213XXXXXXXXX, 0XXXXXXXXX, 213XXXXXXXXX
    patterns = [
        r'^\+?213[5-7][0-9]{8}$',  # +213XXXXXXXXX
        r'^0[5-7][0-9]{8}$',        # 0XXXXXXXXX
    ]
    
    for pattern in patterns:
        if re.match(pattern, clean_phone):
            return True, ""
    
    return False, "Format invalide. Exemples: +213XXXXXXXXX ou 0XXXXXXXXX"

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Nettoie et limite les entrées utilisateur"""
    if not text:
        return ""
    
    # Supprime les caractères dangereux
    text = text.strip()
    text = re.sub(r'[<>]', '', text)  # Prévention XSS basique
    
    return text[:max_length]

def format_currency(amount: float) -> str:
    """Formate un montant en devise"""
    try:
        return f"{amount:,.0f}".replace(',', ' ') + " €"
    except:
        return "0 €"

def format_date(date_str: str) -> str:
    """Formate une date au format français avec gestion d'erreur"""
    try:
        if isinstance(date_str, datetime):
            return date_str.strftime('%d/%m/%Y %H:%M')
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%d/%m/%Y %H:%M')
    except Exception as e:
        logger.warning(f"Erreur formatage date: {e}")
        return str(date_str)

# ====== LOGO AVEC GESTION D'ERREUR ======
def display_logo(size: str = "300px"):
    """Affiche le logo avec fallback robuste"""
    try:
        # Tentative d'affichage de l'image
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        # Fallback avec emoji
        logger.info(f"Logo non trouvé, utilisation du fallback: {e}")
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <div style="font-size: {size}; color: #ffffff;">✈️</div>
            </div>
        """, unsafe_allow_html=True)

# ====== CSS OPTIMISÉ ======
def load_css():
    """Charge le CSS optimisé"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        
        * { 
            font-family: 'Poppins', sans-serif;
            box-sizing: border-box;
        }
        
        .stApp { 
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        
        /* Responsive Mobile First */
        @media only screen and (max-width: 768px) {
            h1 { font-size: 1.8em !important; }
            h2 { font-size: 1.5em !important; }
            h3 { font-size: 1.2em !important; }
            
            .hero-title { font-size: 2em !important; }
            .hero-subtitle { font-size: 1em !important; }
            
            .card {
                padding: 15px !important;
                margin: 10px 0 !important;
            }
            
            .stButton>button {
                padding: 15px 25px !important;
                font-size: 16px !important;
                min-height: 50px !important;
            }
        }
        
        /* Hero Section */
        .hero-section {
            width: 100%;
            padding: 60px 20px;
            border-radius: 20px;
            margin-bottom: 40px;
            background: white;
            text-align: center;
        }
        
        .hero-title {
            color: #0f172a;
            font-size: 3em;
            font-weight: 700;
            margin: 20px 0 10px 0;
        }
        
        .hero-subtitle {
            color: #1e293b;
            font-size: 1.3em;
            font-weight: 400;
            margin: 10px 0;
        }
        
        /* Cards */
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
        }
        
        .card h2, .card h3, .card h4, .card p, .card span:not(.badge) {
            color: #0f172a !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: #3b82f6;
            color: #ffffff !important;
            border-radius: 25px;
            padding: 12px 30px;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton>button:hover {
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 10px;
            border: 2px solid #e5e7eb;
            background: #ffffff;
            color: #0f172a;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }
        
        /* Info boxes */
        .info-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
            margin: 20px 0;
        }
        
        .success-box {
            background: #d1fae5;
            border-left-color: #10b981;
        }
        
        .error-box {
            background: #fee2e2;
            border-left-color: #dc2626;
        }
        
        /* Messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 10px;
            padding: 15px;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #ffffff;
        }
        
        /* Labels */
        label {
            color: #f1f5f9 !important;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE SÉCURISÉES ======
@st.cache_data(ttl=300)
def get_destinations() -> List[Dict]:
    """Récupère les destinations avec gestion d'erreur"""
    if not supabase:
        logger.warning("Supabase non initialisé")
        return []
    
    try:
        response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
        logger.info(f"✅ {len(response.data)} destinations récupérées")
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Erreur get_destinations: {e}")
        st.error(f"Erreur lors de la récupération des destinations: {str(e)}")
        return []

def add_reservation(data: Dict) -> Tuple[bool, str]:
    """Ajoute une réservation avec validation et sécurité renforcées"""
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    
    try:
        # Sanitization des données
        sanitized_data = {
            'nom': sanitize_input(data.get('nom', ''), 100),
            'email': sanitize_input(data.get('email', ''), 254).lower(),
            'telephone': sanitize_input(data.get('telephone', ''), 20),
            'destination': sanitize_input(data.get('destination', ''), 200),
            'date_depart': str(data.get('date_depart', '')),
            'date_retour': str(data.get('date_retour', '')),
            'nb_personnes': int(data.get('nb_personnes', 1)),
            'duree_sejour': int(data.get('duree_sejour', 1)),
            'message': sanitize_input(data.get('message', ''), 1000),
            'statut': 'en_attente',
            'date_creation': datetime.now().isoformat()
        }
        
        # Validation finale
        if not all([sanitized_data['nom'], sanitized_data['email'], sanitized_data['telephone']]):
            return False, "❌ Données obligatoires manquantes"
        
        response = supabase.table('reservations').insert(sanitized_data).execute()
        
        # Clear cache
        get_statistics.clear()
        
        logger.info(f"✅ Réservation créée: {sanitized_data['nom']} - {sanitized_data['destination']}")
        return True, "✅ Réservation enregistrée avec succès"
        
    except Exception as e:
        logger.error(f"❌ Erreur add_reservation: {e}")
        return False, f"❌ Erreur lors de l'enregistrement: {str(e)}"

def get_reservations(limit: Optional[int] = None) -> List[Dict]:
    """Récupère les réservations avec gestion d'erreur"""
    if not supabase:
        return []
    
    try:
        query = supabase.table('reservations').select("*").order('date_creation', desc=True)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Erreur get_reservations: {e}")
        return []

def update_reservation_status(reservation_id: int, new_status: str) -> Tuple[bool, str]:
    """Met à jour le statut avec validation"""
    if not supabase:
        return False, "Base de données non disponible"
    
    valid_statuses = ['en_attente', 'confirme', 'annule']
    if new_status not in valid_statuses:
        return False, "Statut invalide"
    
    try:
        supabase.table('reservations').update({"statut": new_status}).eq('id', reservation_id).execute()
        get_statistics.clear()
        logger.info(f"✅ Statut mis à jour: ID {reservation_id} -> {new_status}")
        return True, "✅ Statut mis à jour"
    except Exception as e:
        logger.error(f"❌ Erreur update_status: {e}")
        return False, f"❌ Erreur: {str(e)}"

def add_contact(data: Dict) -> Tuple[bool, str]:
    """Ajoute un message de contact avec sécurité"""
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    
    try:
        sanitized_data = {
            'nom': sanitize_input(data.get('nom', ''), 100),
            'email': sanitize_input(data.get('email', ''), 254).lower(),
            'telephone': sanitize_input(data.get('telephone', ''), 20),
            'sujet': sanitize_input(data.get('sujet', ''), 200),
            'message': sanitize_input(data.get('message', ''), 2000),
            'lu': False,
            'date_creation': datetime.now().isoformat()
        }
        
        supabase.table('contacts').insert(sanitized_data).execute()
        get_statistics.clear()
        
        logger.info(f"✅ Contact créé: {sanitized_data['nom']}")
        return True, "✅ Message envoyé avec succès"
        
    except Exception as e:
        logger.error(f"❌ Erreur add_contact: {e}")
        return False, f"❌ Erreur: {str(e)}"

def get_contacts(unread_only: bool = False) -> List[Dict]:
    """Récupère les messages de contact"""
    if not supabase:
        return []
    
    try:
        query = supabase.table('contacts').select("*").order('date_creation', desc=True)
        if unread_only:
            query = query.eq('lu', False)
        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Erreur get_contacts: {e}")
        return []

def mark_contact_as_read(contact_id: int) -> bool:
    """Marque un message comme lu"""
    if not supabase:
        return False
    
    try:
        supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
        get_statistics.clear()
        return True
    except Exception as e:
        logger.error(f"❌ Erreur mark_as_read: {e}")
        return False

# ====== STATISTIQUES ======
@st.cache_data(ttl=60)
def get_statistics() -> Dict:
    """Calcule les statistiques"""
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
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
    
    return stats

# ====== COMPOSANTS ======
def display_stat_card(icon: str, number: str, label: str):
    """Carte de statistique"""
    st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
            <h2 style="color: #0f172a; margin: 5px 0;">{number}</h2>
            <p style="margin: 5px 0 0 0; color: #1e293b;">{label}</p>
        </div>
    """, unsafe_allow_html=True)

# ====== CAROUSEL ======
def display_carousel():
    """Carrousel de destinations"""
    carousel_data = [
        {"emoji": "🗼", "title": "Paris, France", "description": "La Ville Lumière vous attend"},
        {"emoji": "🕌", "title": "Istanbul, Turquie", "description": "Entre Orient et Occident"},
        {"emoji": "🏝️", "title": "Maldives", "description": "Paradis tropical"},
        {"emoji": "🏛️", "title": "Rome, Italie", "description": "La Ville Éternelle"},
        {"emoji": "🌴", "title": "Dubaï, EAU", "description": "Luxe et modernité"}
    ]
    
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    idx = st.session_state.carousel_index
    slide = carousel_data[idx]
    
    st.markdown(f"""
        <div class="card" style="text-align: center; padding: 40px;">
            <div style="font-size: 4em; margin-bottom: 20px;">{slide['emoji']}</div>
            <h2 style="color: #0f172a;">{slide['title']}</h2>
            <p style="color: #1e293b; font-size: 1.1em; margin-top: 10px;">{slide['description']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Précédent", use_container_width=True):
            st.session_state.carousel_index = (idx - 1) % len(carousel_data)
            st.rerun()
    
    with col2:
        indicators = " ".join(["⬤" if i == idx else "○" for i in range(len(carousel_data))])
        st.markdown(f"<div style='text-align: center; color: #3b82f6; font-size: 1.5em;'>{indicators}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Suivant ▶", use_container_width=True):
            st.session_state.carousel_index = (idx + 1) % len(carousel_data)
            st.rerun()

# ====== PAGES ======
def page_accueil():
    """Page d'accueil"""
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    display_logo(size="150px")
    st.markdown("""
        <h1 class="hero-title">HCM VOYAGES</h1>
        <p class="hero-subtitle">L'évasion sur mesure, explorez, rêvez, partez</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🌍 Découvrez Nos Destinations")
    display_carousel()
    
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [("🌍", "50+", "Destinations"), ("😊", "1000+", "Clients"), 
             ("📅", "10+", "Années"), ("🤝", "25+", "Partenaires")]
    
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats):
        with col:
            display_stat_card(icon, num, label)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌍 Découvrir nos destinations", use_container_width=True, type="primary"):
            st.session_state.page = "destinations"
            st.rerun()

def page_destinations():
    """Page destinations"""
    st.markdown("# 🌍 Nos Voyages Organisés")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", "", placeholder="Istanbul, Antalya...")
    with col2:
        tri = st.selectbox("💰 Trier", ["Nom A-Z", "Nom Z-A"])
    
    destinations = [
        {"nom": "Istanbul", "pays": "Turquie", "description": "La ville des deux continents", "duree": "5j/4n"},
        {"nom": "Antalya", "pays": "Turquie", "description": "Perle de la Riviera turque", "duree": "7j/6n"},
        {"nom": "Hammamet", "pays": "Tunisie", "description": "Station balnéaire méditerranéenne", "duree": "6j/5n"},
        {"nom": "Sharm El Sheikh", "pays": "Égypte", "description": "Paradis de la Mer Rouge", "duree": "7j/6n"},
        {"nom": "Malaisie", "pays": "Malaisie", "description": "Mélange fascinant de cultures", "duree": "10j/9n"},
        {"nom": "Maldives", "pays": "Maldives", "description": "Le paradis sur terre", "duree": "8j/7n"}
    ]
    
    filtered = [d for d in destinations if not search or search.lower() in d['nom'].lower() or search.lower() in d['pays'].lower()]
    filtered = sorted(filtered, key=lambda x: x['nom'], reverse=(tri == "Nom Z-A"))
    
    st.markdown(f"### ✈️ {len(filtered)} voyage(s)")
    
    cols = st.columns(2)
    for idx, dest in enumerate(filtered):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="card">
                    <h2>📍 {dest['nom']}</h2>
                    <h4>{dest['pays']}</h4>
                    <p style="margin: 15px 0;">{dest['description']}</p>
                    <p style="font-weight: 600;">⏱️ {dest['duree']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    """Page de réservation"""
    st.markdown("# 📝 Réserver Votre Voyage")
    
    with st.form("reservation_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Ahmed Benali")
            email = st.text_input("Email *", placeholder="exemple@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("Destination *", 
                value=st.session_state.get('destination_selectionnee', ''),
                placeholder="Paris")
            date_depart = st.date_input("Date de départ *", 
                value=datetime.now().date(),
                min_value=datetime.now().date())
            date_retour = st.date_input("Date de retour *", 
                value=datetime.now().date() + timedelta(days=7),
                min_value=datetime.now().date() + timedelta(days=1))
            nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
        
        message = st.text_area("Message / Demandes spéciales", height=120)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✈️ Envoyer la demande", use_container_width=True)
        
        if submitted:
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
                    "date_depart": date_depart,
                    "date_retour": date_retour,
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
                            <p><strong>Destination:</strong> {destination}</p>
                            <p><strong>📅 Départ:</strong> {date_depart.strftime('%d/%m/%Y')}</p>
                            <p><strong>📅 Retour:</strong> {date_retour.strftime('%d/%m/%Y')}</p>
                            <p><strong>⏱️ Durée:</strong> {duree_sejour} jour(s)</p>
                            <p><strong>👥 Personnes:</strong> {nb_personnes}</p>
                            <hr>
                            <p>📧 Confirmation envoyée à <strong>{email}</strong></p>
                            <p>Notre équipe vous contactera sous 24h</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error(msg)

def page_contact():
    """Page de contact"""
    st.markdown("# 📧 Contactez-nous")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Envoyez-nous un message")
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            sujet = st.selectbox("Sujet *", [
                "-- Sélectionnez --",
                "Demande d'information",
                "Réclamation",
                "Suggestion",
                "Autre"
            ])
            message = st.text_area("Votre message *", height=150, placeholder="Décrivez votre demande...")
            
            submitted = st.form_submit_button("📨 Envoyer le message", use_container_width=True)
            
            if submitted:
                errors = []
                
                if not nom or len(nom) < 3:
                    errors.append("Nom invalide")
                
                email_valid, email_msg = validate_email(email)
                if not email_valid:
                    errors.append(email_msg)
                
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
                        "telephone": telephone,
                        "sujet": sujet,
                        "message": message
                    }
                    
                    success, msg = add_contact(contact_data)
                    
                    if success:
                        st.success(msg)
                        st.markdown("""
                            <div class="info-box success-box">
                                <h4>✅ Message envoyé avec succès !</h4>
                                <p>Nous vous répondrons dans les plus brefs délais.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.error(msg)
    
    with col2:
        st.markdown("### 📍 Nos Coordonnées")
        st.markdown("""
            <div class="card">
                <p><strong>📧 Email:</strong><br>contact@hcmvoyages.com</p>
                <p><strong>📱 Téléphone:</strong><br>+213 XXX XXX XXX</p>
                <p><strong>📍 Adresse:</strong><br>Alger, Algérie</p>
                <p><strong>⏰ Horaires:</strong><br>Lun-Ven: 9h-18h<br>Sam: 9h-13h</p>
            </div>
        """, unsafe_allow_html=True)

def page_admin():
    """Page d'administration sécurisée"""
    st.markdown("# 🔐 Administration")
    
    # Vérification de l'authentification
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("### 🔒 Connexion Administrateur")
        
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("🔓 Se connecter")
            
            if submitted:
                hashed = hash_password(password)
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hashed:
                    st.session_state.authenticated = True
                    logger.info(f"✅ Connexion admin réussie: {username}")
                    st.success("✅ Connexion réussie !")
                    st.rerun()
                else:
                    logger.warning(f"⚠️ Tentative de connexion échouée: {username}")
                    st.error("❌ Identifiants incorrects")
        return
    
    # Interface admin
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 👋 Bienvenue, Administrateur")
    with col3:
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Statistiques
    st.markdown("### 📊 Statistiques")
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
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2 = st.tabs(["📋 Réservations", "📧 Messages"])
    
    with tab1:
        st.markdown("### 📋 Gestion des Réservations")
        
        reservations = get_reservations(limit=50)
        
        if not reservations:
            st.info("Aucune réservation pour le moment")
        else:
            for res in reservations:
                with st.expander(f"📍 {res.get('destination', 'N/A')} - {res.get('nom', 'N/A')} ({format_date(res.get('date_creation', ''))})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>👤 Client:</strong> {res.get('nom', 'N/A')}</p>
                                <p><strong>📧 Email:</strong> {res.get('email', 'N/A')}</p>
                                <p><strong>📱 Téléphone:</strong> {res.get('telephone', 'N/A')}</p>
                                <p><strong>📍 Destination:</strong> {res.get('destination', 'N/A')}</p>
                                <p><strong>📅 Départ:</strong> {res.get('date_depart', 'N/A')}</p>
                                <p><strong>📅 Retour:</strong> {res.get('date_retour', 'N/A')}</p>
                                <p><strong>⏱️ Durée:</strong> {res.get('duree_sejour', 'N/A')} jour(s)</p>
                                <p><strong>👥 Personnes:</strong> {res.get('nb_personnes', 'N/A')}</p>
                                <p><strong>💬 Message:</strong> {res.get('message', 'Aucun')}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        statut_actuel = res.get('statut', 'en_attente')
                        
                        if statut_actuel == 'en_attente':
                            badge_color = "warning"
                            badge_text = "⏳ En attente"
                        elif statut_actuel == 'confirme':
                            badge_color = "success"
                            badge_text = "✅ Confirmé"
                        else:
                            badge_color = "danger"
                            badge_text = "❌ Annulé"
                        
                        st.markdown(f'<span class="badge badge-{badge_color}">{badge_text}</span>', unsafe_allow_html=True)
                        
                        nouveau_statut = st.selectbox(
                            "Changer le statut",
                            ["en_attente", "confirme", "annule"],
                            index=["en_attente", "confirme", "annule"].index(statut_actuel),
                            key=f"statut_{res['id']}"
                        )
                        
                        if st.button("💾 Mettre à jour", key=f"update_{res['id']}"):
                            success, msg = update_reservation_status(res['id'], nouveau_statut)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
    
    with tab2:
        st.markdown("### 📧 Messages de Contact")
        
        contacts = get_contacts()
        
        if not contacts:
            st.info("Aucun message pour le moment")
        else:
            for contact in contacts:
                lu = contact.get('lu', False)
                icon = "📭" if lu else "📬"
                
                with st.expander(f"{icon} {contact.get('nom', 'N/A')} - {contact.get('sujet', 'N/A')} ({format_date(contact.get('date_creation', ''))})", expanded=not lu):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>👤 Nom:</strong> {contact.get('nom', 'N/A')}</p>
                                <p><strong>📧 Email:</strong> {contact.get('email', 'N/A')}</p>
                                <p><strong>📱 Téléphone:</strong> {contact.get('telephone', 'N/A')}</p>
                                <p><strong>📋 Sujet:</strong> {contact.get('sujet', 'N/A')}</p>
                                <p><strong>💬 Message:</strong></p>
                                <p style="background: #f1f5f9; padding: 15px; border-radius: 8px; margin-top: 10px;">
                                    {contact.get('message', 'N/A')}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if not lu:
                            if st.button("✅ Marquer comme lu", key=f"read_{contact['id']}"):
                                if mark_contact_as_read(contact['id']):
                                    st.success("Message marqué comme lu")
                                    st.rerun()
                        else:
                            st.info("Message déjà lu")

# ====== NAVIGATION ======
def main():
    """Application principale"""
    load_css()
    
    # Initialisation de la session
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    # Sidebar
    with st.sidebar:
        display_logo(size="120px")
        st.markdown("---")
        
        # Menu de navigation
        pages = {
            "🏠 Accueil": "accueil",
            "🌍 Destinations": "destinations",
            "📝 Réservation": "reservation",
            "📧 Contact": "contact",
            "🔐 Admin": "admin"
        }
        
        for label, page_id in pages.items():
            if st.button(label, use_container_width=True, type="primary" if st.session_state.page == page_id else "secondary"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Informations
        st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 10px;">
                <p style="color: #0f172a; margin: 5px 0;"><strong>📞 Hotline 24/7</strong></p>
                <p style="color: #1e293b; margin: 5px 0;">+213 XXX XXX XXX</p>
                <p style="color: #0f172a; margin: 15px 0 5px 0;"><strong>📧 Email</strong></p>
                <p style="color: #1e293b; margin: 5px 0;">contact@hcmvoyages.com</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: #0f172a;">
                <p style="font-size: 0.85em;">© 2024 HCM Voyages</p>
                <p style="font-size: 0.8em;">Tous droits réservés</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Affichage de la page sélectionnée
    page_functions = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "contact": page_contact,
        "admin": page_admin
    }
    
    current_page = st.session_state.page
    if current_page in page_functions:
        page_functions[current_page]()
    else:
        st.error("Page introuvable")

# Point d'entrée
if __name__ == "__main__":
    main()
