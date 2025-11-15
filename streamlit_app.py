"""
HCM VOYAGES - Application Streamlit Complète
Version Finale avec toutes les fonctionnalités
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



# ====== FONCTIONS UTILITAIRES ======
def hash_password(password: str) -> str:
    salt = "hcm_voyages_2024"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

@st.cache_resource
def init_supabase() -> Optional[Client]:
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
    if not email:
        return False, "Email requis"
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Format d'email invalide"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone:
        return False, "Téléphone requis"
    clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    patterns = [
        r'^\+?213[5-7][0-9]{8}$',
        r'^0[5-7][0-9]{8}$'
    ]
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

def display_logo(width: int = 200):
    st.markdown('<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; font-size: 3em; color: #667eea;">
            ✈️ HCM VOYAGES
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====== CSS PREMIUM ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .stat-card {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    
    .stat-card:hover {
        transform: scale(1.08) rotate(2deg);
        box-shadow: 0 20px 50px rgba(102,126,234,0.5);
    }
    
    .stat-icon {
        font-size: 3.5em;
        margin-bottom: 15px;
        animation: bounce 2s infinite;
    }
    
    .stat-number {
        font-size: 3em;
        font-weight: 800;
        margin: 15px 0;
    }
    
    .stat-label {
        font-size: 1.15em;
        font-weight: 400;
        opacity: 0.95;
    }
    
    .card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(102,126,234,0.1);
        transition: all 0.4s ease;
    }
    
    .card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102,126,234,0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        border-radius: 50px;
        padding: 16px 45px;
        border: none;
        font-weight: 600;
        font-size: 1.1em;
        transition: all 0.4s ease;
        box-shadow: 0 10px 25px rgba(102,126,234,0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 15px 40px rgba(102,126,234,0.6);
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 25px 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(74,222,128,0.15), rgba(34,197,94,0.15));
        border-left-color: #4ade80;
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======
def add_reservation(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Service temporairement indisponible"
    
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
            'statut': 'en_attente',
            'date_creation': datetime.now().isoformat()
        }
        
        response = supabase.table('reservations').insert(sanitized).execute()
        
        if response.data:
            logger.info(f"✅ Réservation ajoutée: {sanitized['email']}")
            return True, "✅ Réservation enregistrée avec succès !"
        else:
            return False, "❌ Erreur lors de l'enregistrement"
            
    except Exception as e:
        logger.error(f"Erreur add_reservation: {e}")
        return False, f"❌ Erreur technique: {str(e)}"

def add_contact(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Service temporairement indisponible"
    
    try:
        sanitized = {
            'nom': sanitize_input(data['nom'], 100),
            'email': sanitize_input(data['email'], 254).lower(),
            'telephone': sanitize_input(data.get('telephone', ''), 20),
            'sujet': sanitize_input(data['sujet'], 200),
            'message': sanitize_input(data['message'], 2000),
            'date_creation': datetime.now().isoformat()
        }
        
        response = supabase.table('contacts').insert(sanitized).execute()
        
        if response.data:
            return True, "✅ Message envoyé avec succès !"
        return False, "❌ Erreur lors de l'envoi"
    except Exception as e:
        logger.error(f"Erreur add_contact: {e}")
        return False, f"❌ Erreur: {str(e)}"

def add_demande_visa(data: Dict) -> Tuple[bool, str]:
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

@st.cache_data(ttl=300)
def get_reservations() -> List[Dict]:
    if not supabase:
        return []
    try:
        response = supabase.table('reservations').select("*").order('date_creation', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Erreur get_reservations: {e}")
        return []

@st.cache_data(ttl=300)
def get_destinations() -> List[Dict]:
    if not supabase:
        return []
    try:
        response = supabase.table('destinations').select("*").eq('actif', True).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Erreur get_destinations: {e}")
        return []

@st.cache_data(ttl=300)
def get_statistics() -> Dict:
    if not supabase:
        return {"reservations": 0, "contacts": 0, "visa": 0}
    
    try:
        stats = {
            "reservations": len(get_reservations()),
            "contacts": len(supabase.table('contacts').select("*").execute().data or []),
            "visa": len(supabase.table('demandes_visa').select("*").execute().data or [])
        }
        return stats
    except:
        return {"reservations": 0, "contacts": 0, "visa": 0}

# ====== PAGES ======
def page_accueil():
    st.markdown("# 🌍 Bienvenue chez HCM Voyages")
    st.markdown("### L'évasion sur mesure • Explorez • Rêvez • Partez")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
    stats_data = [
        ("🌍", "50+", "Destinations"),
        ("😊", "1000+", "Clients satisfaits"),
        ("📅", "10+", "Années d'expérience"),
        ("🤝", "25+", "Partenaires")
    ]
    
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats_data):
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
                <h3 style="color: #667eea; text-align: center;">Voyages Organisés</h3>
                <p style="text-align: center; color: #64748b;">
                    Circuits touristiques et séjours sur mesure
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3.5em; text-align: center; margin-bottom: 20px;">📋</div>
                <h3 style="color: #667eea; text-align: center;">Assistance Visa</h3>
                <p style="text-align: center; color: #64748b;">
                    Accompagnement complet pour vos demandes
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="card">
                <div style="font-size: 3.5em; text-align: center; margin-bottom: 20px;">💎</div>
                <h3 style="color: #667eea; text-align: center;">Séjours Premium</h3>
                <p style="text-align: center; color: #64748b;">
                    Hôtels de luxe et expériences exclusives
                </p>
            </div>
        """, unsafe_allow_html=True)

def page_destinations():
    st.markdown("# 🌍 Nos Destinations")
    
    destinations = get_destinations()
    
    if not destinations:
        st.info("🔄 Chargement des destinations...")
        return
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        continents = list(set([d.get('continent', 'Autre') for d in destinations if d.get('continent')]))
        continent_filter = st.selectbox("🌎 Continent", ["Tous"] + continents)
    
    # Application du filtre
    filtered = destinations
    if continent_filter != "Tous":
        filtered = [d for d in destinations if d.get('continent') == continent_filter]
    
    # Affichage
    cols = st.columns(3)
    for idx, dest in enumerate(filtered):
        with cols[idx % 3]:
            prix = dest.get('prix', dest.get('prix_minimum', 0))
            st.markdown(f"""
                <div class="card">
                    <h3 style="color: #667eea;">{dest.get('nom', 'Destination')}</h3>
                    <p><strong>Pays:</strong> {dest.get('pays', 'N/A')}</p>
                    <p>{dest.get('description', 'Belle destination')}</p>
                    <p style="font-size: 1.3em; color: #764ba2; font-weight: bold;">
                        À partir de {prix:,.0f} DZD
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver", key=f"btn_{idx}"):
                st.session_state.destination_selectionnee = dest.get('nom')
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    st.markdown("# 📝 Réservation")
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Ahmed Benali")
            email = st.text_input("Email *", placeholder="exemple@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("Destination *", 
                value=st.session_state.get('destination_selectionnee', ''))
            date_depart = st.date_input("Date de départ *", 
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=30))
            date_retour = st.date_input("Date de retour *", 
                min_value=date_depart + timedelta(days=1),
                value=date_depart + timedelta(days=5))
        
        nb_personnes = st.number_input("Nombre de voyageurs *", 
            min_value=1, max_value=20, value=2)
        
        message = st.text_area("Demandes spéciales", height=100)
        
        submitted = st.form_submit_button("✈️ Valider ma réservation", use_container_width=True)
        
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
                    st.balloons()
                else:
                    st.error(msg)

def page_demande_visa():
    st.markdown("# 📋 Demande de Visa")
    
    with st.form("visa_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom *")
            prenom = st.text_input("Prénom *")
            email = st.text_input("Email *")
            telephone = st.text_input("Téléphone *")
            date_naissance = st.date_input("Date de naissance *")
        
        with col2:
            nationalite = st.text_input("Nationalité *", value="Algérienne")
            numero_passeport = st.text_input("Numéro de passeport")
            pays_destination = st.selectbox("Pays de destination *", 
                ["France", "Espagne", "Italie", "UK", "USA", "Canada", "Autre"])
            type_visa = st.selectbox("Type de visa *", 
                ["Tourisme", "Affaires", "Études", "Travail", "Famille"])
            date_depart_prevue = st.date_input("Date de départ prévue")
        
        message = st.text_area("Informations complémentaires")
        
        submitted = st.form_submit_button("📤 Envoyer ma demande", use_container_width=True)
        
        if submitted:
            data = {
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "telephone": telephone,
                "date_naissance": date_naissance,
                "nationalite": nationalite,
                "numero_passeport": numero_passeport,
                "pays_destination": pays_destination,
                "type_visa": type_visa.lower(),
                "date_depart_prevue": date_depart_prevue,
                "message": message,
                "statut": "soumise"
            }
            
            success, msg = add_demande_visa(data)
            
            if success:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)

def page_contact():
    st.markdown("# 📞 Contactez-nous")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("contact_form"):
            nom = st.text_input("Nom *")
            email = st.text_input("Email *")
            telephone = st.text_input("Téléphone")
            sujet = st.text_input("Sujet *")
            message = st.text_area("Message *", height=150)
            
            submitted = st.form_submit_button("📤 Envoyer", use_container_width=True)
            
            if submitted:
                data = {
                    "nom": nom,
                    "email": email,
                    "telephone": telephone,
                    "sujet": sujet,
                    "message": message
                }
                
                success, msg = add_contact(data)
                
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3 style="color: #667eea;">📍 Coordonnées</h3>
                <p><strong>📧 Email:</strong><br>contact@hcmvoyages.dz</p>
                <p><strong>📞 Téléphone:</strong><br>+213 XXX XXX XXX</p>
                <p><strong>📍 Adresse:</strong><br>Alger, Algérie</p>
                <p><strong>🕒 Horaires:</strong><br>Dim-Jeu: 9h-17h</p>
            </div>
        """, unsafe_allow_html=True)

def page_admin():
    st.markdown("# 🔐 Espace Administration")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔒 Mot de passe", type="password")
            
            if st.form_submit_button("🔓 Se connecter"):
                if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        return
    
    # Dashboard admin
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("### 📊 Statistiques")
    
    stats = get_statistics()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📋</div>
                <div class="stat-number">{stats['reservations']}</div>
                <div class="stat-label">Réservations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📧</div>
                <div class="stat-number">{stats['contacts']}</div>
                <div class="stat-label">Messages</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">✈️</div>
                <div class="stat-number">{stats['visa']}</div>
                <div class="stat-label">Visas</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tableau des réservations
    st.markdown("### 📋 Réservations Récentes")
    reservations = get_reservations()
    
    if reservations:
        df = pd.DataFrame(reservations)
        st.dataframe(df, use_container_width=True, height=400)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Exporter CSV",
            data=csv,
            file_name=f"reservations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 Aucune réservation")

# ====== NAVIGATION ======
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo()
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Destinations", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📋", "Demande de Visa", "demande-visa"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Admin", "admin"),
        ]
        
        for icon, label, page_id in pages:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <p style="color: #667eea; font-weight: 600;">✈️ HCM VOYAGES</p>
                <p style="font-size: 0.9em; color: #64748b;">L'évasion sur mesure</p>
                <p style="font-size: 0.8em; color: #94a3b8;">© 2024 Tous droits réservés</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Routing
    pages_map = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "demande-visa": page_demande_visa,
        "contact": page_contact,
        "admin": page_admin
    }
    
    page_function = pages_map.get(st.session_state.page, page_accueil)
    page_function()

if __name__ == "__main__":
    main()
