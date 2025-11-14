"""
HCM VOYAGES - Application Streamlit Optimisée - VERSION FINALE CORRIGÉE
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Optional, Dict, List, Tuple
import hashlib

st.set_page_config(
    page_title="HCM Voyages - L'évasion sur mesure",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_CREDENTIALS = {"admin": hash_password("admin123")}

@st.cache_resource
def init_supabase() -> Optional[Client]:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erreur connexion: {e}")
        return None

supabase = init_supabase()

def validate_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_phone(phone: str) -> bool:
    clean = phone.replace(' ', '').replace('-', '')
    return bool(re.match(r'^(\+?213|0)[5-7][0-9]{8}$', clean))

def format_currency(amount: float) -> str:
    return f"{amount:,.0f}".replace(',', ' ') + " EUR"

def format_date(date_str: str) -> str:
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')
    except:
        return date_str

def display_logo(size: str = "300px"):
    try:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;"><div style="font-size: {size};">LOGO</div></div>', unsafe_allow_html=True)

def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
        * { font-family: 'Poppins', sans-serif; }
        .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); }
        
        @media only screen and (max-width: 768px) {
            h1 { font-size: 1.8em !important; }
            .hero-section { height: 300px !important; }
            .card { padding: 15px !important; }
        }
        
        .hero-section {
            position: relative; width: 100%; height: 400px; border-radius: 20px;
            overflow: hidden; margin-bottom: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            background: white;
        }
        .hero-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            display: flex; flex-direction: column; justify-content: center;
            align-items: center; padding: 40px;
        }
        .hero-title {
            color: #1e40af; font-size: 3.5em; font-weight: 700; margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1); text-align: center;
        }
        .hero-subtitle {
            color: #2563eb; font-size: 1.5em; font-weight: 300; margin: 20px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1); text-align: center;
        }
        
        .carousel-container {
            position: relative; width: 100%; height: 500px; border-radius: 20px;
            overflow: hidden; margin: 30px 0; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        .carousel-slide {
            position: absolute; width: 100%; height: 100%; display: flex;
            align-items: center; justify-content: center;
            background: linear-gradient(135deg, rgba(30,64,175,0.9), rgba(37,99,235,0.9));
        }
        .carousel-content { text-align: center; color: white; padding: 40px; }
        .carousel-title { font-size: 3em; font-weight: 700; margin-bottom: 20px; }
        
        .card {
            background: white; padding: 25px; border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin: 15px 0;
            transition: all 0.3s ease; border: 2px solid rgba(255,255,255,0.1);
        }
        .card h2, .card h3, .card h4 { color: #1e3a8a !important; }
        .card p, .card span:not(.badge) { color: #1e3a8a !important; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }
        
        .stButton>button {
            background: white; color: #1e40af; border-radius: 25px; padding: 12px 30px;
            border: 2px solid white; font-weight: 600; transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2); width: 100%;
        }
        .stButton>button:hover { transform: translateY(-2px); }
        
        [data-testid="stSidebar"] { background: white; border-right: 2px solid #e5e7eb; }
        [data-testid="stSidebar"] * { color: #1e40af !important; }
        
        .info-box {
            background: white; padding: 20px; border-radius: 12px;
            border-left: 4px solid white; margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        .info-box h3, .info-box h4, .info-box p { color: #1e3a8a !important; }
        .success-box {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left-color: #10b981;
        }
        .success-box h3, .success-box h4, .success-box p { color: #065f46 !important; }
        
        .badge {
            display: inline-block; padding: 5px 12px; border-radius: 20px;
            font-size: 0.85em; font-weight: 600; margin: 0 5px;
        }
        .badge-success { background: #10b981; color: white; }
        .badge-warning { background: #f59e0b; color: white; }
        .badge-info { background: #3b82f6; color: white; }
        
        .accueil-page h1, .accueil-page h2, .accueil-page h3 { color: white !important; }
        .other-page h1, .other-page h2, .other-page h3 { color: white !important; }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 10px; border: 2px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.95); color: #1e40af;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.2); border-radius: 10px 10px 0 0;
            color: white !important; font-weight: 500;
        }
        .stTabs [aria-selected="true"] { background: white; color: #1e3a8a !important; }
        </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_destinations() -> List[Dict]:
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data if response.data else []
        except:
            pass
    return []

def add_reservation(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "Base non connectée"
    try:
        data['statut'] = 'en_attente'
        data['date_creation'] = datetime.now().isoformat()
        supabase.table('reservations').insert(data).execute()
        get_statistics.clear()
        return True, "Réservation enregistrée"
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
            pass
    return []

def update_reservation_status(reservation_id: int, new_status: str) -> bool:
    if supabase:
        try:
            supabase.table('reservations').update({"statut": new_status}).eq('id', reservation_id).execute()
            get_statistics.clear()
            return True
        except:
            pass
    return False

def add_contact(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "Base non connectée"
    try:
        data['lu'] = False
        data['date_creation'] = datetime.now().isoformat()
        supabase.table('contacts').insert(data).execute()
        get_statistics.clear()
        return True, "Message envoyé"
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
            pass
    return []

def mark_contact_as_read(contact_id: int) -> bool:
    if supabase:
        try:
            supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            get_statistics.clear()
            return True
        except:
            pass
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
            <h2>{number}</h2>
            <p>{label}</p>
        </div>
    """, unsafe_allow_html=True)

def display_carousel():
    carousel_data = [
        {"title": "Paris, France", "desc": "La Ville Lumière"},
        {"title": "Istanbul, Turquie", "desc": "Entre Orient et Occident"},
        {"title": "Maldives", "desc": "Paradis tropical"},
        {"title": "Rome, Italie", "desc": "La Ville Éternelle"},
        {"title": "Dubai, EAU", "desc": "Luxe et modernité"}
    ]
    
    if 'carousel_index' not in st.session_state:
        st.session_state.carousel_index = 0
    
    current = carousel_data[st.session_state.carousel_index]
    
    st.markdown(f"""
        <div class="carousel-container">
            <div class="carousel-slide">
                <div class="carousel-content">
                    <div class="carousel-title">{current['title']}</div>
                    <div style="font-size: 1.5em; margin-top: 15px;">{current['desc']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Precedent", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index - 1) % len(carousel_data)
            st.rerun()
    with col3:
        if st.button("Suivant", use_container_width=True):
            st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(carousel_data)
            st.rerun()

def page_accueil():
    st.markdown('<div class="accueil-page">', unsafe_allow_html=True)
    st.markdown('<div class="hero-section"><div class="hero-overlay">', unsafe_allow_html=True)
    display_logo(size="150px")
    st.markdown('<h1 class="hero-title">HCM VOYAGES</h1><p class="hero-subtitle">Evasion sur mesure</p></div></div>', unsafe_allow_html=True)
    
    st.markdown("### Nos Destinations")
    display_carousel()
    
    st.markdown("### Pourquoi nous choisir")
    col1, col2, col3, col4 = st.columns(4)
    with col1: display_stat_card("DEST", "50+", "Destinations")
    with col2: display_stat_card("CLIENT", "1000+", "Clients")
    with col3: display_stat_card("EXP", "10+", "Années")
    with col4: display_stat_card("PART", "25+", "Partenaires")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_destinations():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# Nos Voyages Organisés")
    
    destinations = [
        {"nom": "Istanbul", "pays": "Turquie", "desc": "Ville des deux continents", "duree": "5 jours"},
        {"nom": "Antalya", "pays": "Turquie", "desc": "Riviera turque", "duree": "7 jours"},
        {"nom": "Maldives", "pays": "Maldives", "desc": "Paradis tropical", "duree": "8 jours"},
        {"nom": "Hammamet", "pays": "Tunisie", "desc": "Station balnéaire", "duree": "6 jours"}
    ]
    
    cols = st.columns(2)
    for idx, dest in enumerate(destinations):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="card">
                    <h2>{dest['nom']}</h2>
                    <h4>{dest['pays']}</h4>
                    <p>{dest['desc']}</p>
                    <p>Duree: {dest['duree']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Reserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def page_reservation():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# Reserver Votre Voyage")
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom complet")
            email = st.text_input("Email")
            telephone = st.text_input("Telephone")
        with col2:
            destination = st.text_input("Destination", value=st.session_state.get('destination_selectionnee', ''))
            date_depart = st.date_input("Date depart", value=datetime.now().date())
            nb_personnes = st.number_input("Nombre de personnes", min_value=1, value=1)
        
        submitted = st.form_submit_button("Envoyer", use_container_width=True)
        
        if submitted:
            if all([nom, email, destination, telephone]):
                data = {
                    "nom": nom, "email": email, "telephone": telephone,
                    "destination": destination, "date_depart": str(date_depart),
                    "nb_personnes": nb_personnes
                }
                success, msg = add_reservation(data)
                if success:
                    st.success("Reservation enregistree")
                    st.balloons()
                else:
                    st.error(msg)
            else:
                st.error("Veuillez remplir tous les champs")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_contact():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# Contactez-Nous")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="card">
                <h3>Notre Agence</h3>
                <p><strong>Tel:</strong> +213 783 80 27 12</p>
                <p><strong>Email:</strong> hcmvoyage1@gmail.com</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.form("contact_form"):
            nom = st.text_input("Nom")
            email = st.text_input("Email")
            sujet = st.selectbox("Sujet", ["Information", "Reservation"])
            message = st.text_area("Message")
            
            if st.form_submit_button("Envoyer", use_container_width=True):
                if all([nom, email, message]):
                    success, msg = add_contact({"nom": nom, "email": email, "sujet": sujet, "message": message})
                    if success:
                        st.success("Message envoye")
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("Champs manquants")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_admin():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown("# Administration")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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
        with col1: display_stat_card("RES", str(stats['total_reservations']), "Reservations")
        with col2: display_stat_card("ATT", str(stats['reservations_en_attente']), "En attente")
        with col3: display_stat_card("MSG", str(stats['messages_non_lus']), "Messages")
        
        if st.button("Deconnexion"):
            st.session_state.admin_logged = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_visas():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# Services Visa")
    
    st.markdown("""
        <div class="info-box">
            <h3>Obtenez votre visa facilement</h3>
            <p>HCM Voyages vous accompagne dans vos demarches.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Nos Services par Pays")
    
    visas = [
        {"pays": "USA", "types": ["Normal (4-8 sem)", "Express (1-2 sem)"], "desc": "B1/B2, ESTA"},
        {"pays": "France", "types": ["Normal (15-45 jours)"], "desc": "Schengen court sejour"},
        {"pays": "Espagne", "types": ["Normal (15-30 jours)", "A Domicile"], "desc": "Schengen touristique"}
    ]
    
    for visa in visas:
        st.markdown(f"""
            <div class="card">
                <h2>Visa {visa['pays']}</h2>
                <p>{visa['desc']}</p>
                <p><strong>Services:</strong> {', '.join(visa['types'])}</p>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("Prendre rendez-vous", use_container_width=True):
        st.session_state.page = "demande-visa"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_demande_visa():
    st.markdown('<div class="other-page">', unsafe_allow_html=True)
    st.markdown("# Demande de Rendez-vous Visa")
    
    with st.form("rdv_visa_form"):
        st.markdown("### Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            telephone = st.text_input("Telephone *")
        
        with col2:
            numero_passeport = st.text_input("Numero passeport *")
            date_naissance = st.date_input("Date naissance *", min_value=datetime(1920,1,1).date(), max_value=datetime.now().date())
            profession = st.text_input("Profession")
        
        st.markdown("### Details du Rendez-vous")
        col1, col2 = st.columns(2)
        
        with col1:
            pays_destination = st.selectbox("Pays de destination *", [
                "-- Selectionnez --", "USA", "France", "Espagne"
            ])
            type_visa = st.selectbox("Type de visa *", ["Tourisme", "Affaires", "Visite familiale", "Etudes", "Travail"])
        
        with col2:
            # LOGIQUE CORRIGÉE: USA = Normal/Express, France = Normal uniquement, Espagne = Normal/A Domicile
            if pays_destination == "USA":
                type_service = st.selectbox("Type de service *", [
                    "Normal (4-8 semaines)",
                    "Express (1-2 semaines)"
                ])
            elif pays_destination == "France":
                type_service = st.selectbox("Type de service *", [
                    "Normal (15-45 jours)"
                ])
            elif pays_destination == "Espagne":
                type_service = st.selectbox("Type de service *", [
                    "Normal (15-30 jours)",
                    "A Domicile (rendez-vous chez vous)"
                ])
            else:
                type_service = st.selectbox("Type de service *", ["Normal"])
            
            date_rdv = st.date_input("Date souhaitee *", value=datetime.now().date() + timedelta(days=7), min_value=datetime.now().date() + timedelta(days=3))
        
        adresse = ""
        if "Domicile" in type_service:
            st.markdown("### Adresse pour rendez-vous a domicile")
            adresse = st.text_area("Adresse complete *", height=100)
        
        message = st.text_area("Informations complementaires", height=100)
        
        submitted = st.form_submit_button("Confirmer rendez-vous", use_container_width=True)
        
        if submitted:
            errors = []
            
            if not all([nom, email, telephone, numero_passeport]):
                errors.append("Champs obligatoires manquants")
            elif not validate_email(email):
                errors.append("Email invalide")
            elif not validate_phone(telephone):
                errors.append("Telephone invalide")
            elif pays_destination == "-- Selectionnez --":
                errors.append("Selectionnez un pays")
            elif "Domicile" in type_service and not adresse:
                errors.append("Adresse obligatoire pour service domicile")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                service_type = "Express" if "Express" in type_service else ("A Domicile" if "Domicile" in type_service else "Normal")
                
                st.success("Demande envoyee avec succes!")
                st.markdown(f"""
                    <div class="info-box success-box">
                        <h4>Rendez-vous enregistre</h4>
                        <p><strong>Pays:</strong> {pays_destination}</p>
                        <p><strong>Type visa:</strong> {type_visa}</p>
                        <p><strong>Service:</strong> {service_type}</p>
                        <p><strong>Date:</strong> {date_rdv.strftime('%d/%m/%Y')}</p>
                        {"<p><strong>Adresse:</strong> " + adresse + "</p>" if adresse else ""}
                        <hr>
                        <p>Confirmation envoyee a <strong>{email}</strong></p>
                        <p>Contact sous 48h</p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
    
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
            ("Accueil", "accueil"),
            ("Destinations", "destinations"),
            ("Reservation", "reservation"),
            ("Visa & RDV", "visas"),
            ("Prendre RDV", "demande-visa"),
            ("Contact", "contact"),
            ("Admin", "admin")
        ]
        
        for label, page_id in pages:
            if st.button(label, use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
    
    routes = {
        "accueil": page_accueil,
        "destinations": page_destinations,
        "reservation": page_reservation,
        "visas": page_visas,
        "demande-visa": page_demande_visa,
        "contact": page_contact,
        "admin": page_admin
    }
    
    if st.session_state.page in routes:
        routes[st.session_state.page]()

if __name__ == "__main__":
    main()
