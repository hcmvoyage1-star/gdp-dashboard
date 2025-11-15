"""
HCM VOYAGES - Application Streamlit Complète et Sécurisée
Avec toutes les sections : Devis, Demande de Visa, Discover Algeria
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
    return False, "Format invalide"

def sanitize_input(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'[<>]', '', text)
    return text[:max_length]


Tu as un import streamlit as st à l’intérieur du except → impossible.

La fonction display_home_image est sur une seule ligne mal indentée (def display_home_image():try:) → Python ne peut pas interpréter ça.

Il y a un mélange d’espaces et de tabulations.

✅ Version corrigée et indentée correctement
python
Copier le code
# ====== LOGO ======
def display_logo(size: str = "100%"):
    try:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=None, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown(
            f'<div style="text-align: center; margin: 20px 0; font-size: 5em;">✈️</div>',
            unsafe_allow_html=True
        )

# ====== IMAGE ACCUEIL ======
def display_home_image():
    try:
        st.image("heros.png", use_container_width=True)
    except Exception as e:
        st.error(f"Impossible de charger l'image : {e}")

# ====== IMAGE ACCUEIL ======
def display_home_image():
    try:
        st.image("heros.png", use_container_width=True)
    except Exception as e:
        st.error(f"Impossible de charger l'image : {e}")


# ====== CSS ======
st.markdown("""
    <style>

    /* === PALETTE BLANC PREMIUM === */
    :root {
        --background: #FFFFFF;
        --text-main: #2C2C2C;
        --primary: #3A5BA0;
        --primary-light: #597BC8;
        --accent: #764ba2;
        --card-bg: #F9F9F9;
    }

    body, .stApp {
        background-color: var(--background) !important;
        color: var(--text-main) !important;
        font-family: "Poppins", sans-serif;
    }

    /* --- HERO SECTION --- */
    .hero-section {
        position: relative;
        width: 100%;
        height: 500px;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
    }

    .hero-overlay {
        position: absolute; top: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(58,91,160,0.7), rgba(118,75,162,0.7));
        display: flex; justify-content: center; align-items: center;
        padding: 40px;
    }

    .hero-title {
        color: white; font-size: 4em; font-weight: 700; margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.25);
    }

    .hero-subtitle {
        color: white; font-size: 1.7em; font-weight: 300; margin: 20px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }

    /* --- CARDS --- */
    .card {
        background: var(--card-bg);
        padding: 25px;
        border-radius: 20px;
        margin: 15px 0;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0px 8px 20px rgba(0,0,0,0.05);
        transition: 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 14px 35px rgba(58,91,160,0.1);
        border-color: var(--primary-light);
    }

    /* --- BOUTONS --- */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white !important;
        border-radius: 30px;
        padding: 12px 35px;
        border: none;
        font-weight: 600;
        transition: 0.2s ease;
        box-shadow: 0 5px 15px rgba(58,91,160,0.2);
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(58,91,160,0.35);
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        color: var(--text-main) !important;
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-main) !important;
        font-weight: 500;
    }

    /* --- BOITES D’INFO --- */
    .info-box {
        background: rgba(58,91,160,0.08);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--primary);
        margin: 20px 0;
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
        return True, "✅ Réservation enregistrée"
    except Exception as e:
        return False, f"❌ Erreur: {str(e)}"

def add_devis(data: Dict) -> Tuple[bool, str]:
    if not supabase:
        return False, "⚠️ Base de données non disponible"
    try:
        sanitized = {k: sanitize_input(str(v), 500) if isinstance(v, str) else v for k, v in data.items()}
        supabase.table('demandes_devis').insert(sanitized).execute()
        return True, "✅ Devis enregistré"
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
    try:
        st.image("heros.png", use_container_width=True)
    except Exception as e:
        st.error(f"Impossible de charger l'image : {e}")

    st.markdown("""
        <div class="hero-overlay">
            <div style="text-align: center;">
    """, unsafe_allow_html=True)
    display_logo(size="200px")
    st.markdown("""
                <h1 class="hero-title">HCM VOYAGES</h1>
                <p class="hero-subtitle">L'évasion sur mesure, explorez, rêvez, partez</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    stats = [("🌍", "50+", "Destinations"), ("😊", "1000+", "Clients"), ("📅", "10+", "Années"), ("🤝", "25+", "Partenaires")]
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div style="font-size: 3em;">{icon}</div>
                    <h2 style="color: #667eea;">{num}</h2>
                    <p>{label}</p>
                </div>
            """, unsafe_allow_html=True)

def page_destinations():
    st.markdown("# 🌍 Nos Destinations")
    destinations = [
        {"nom": "Istanbul", "pays": "Turquie", "description": "Entre deux continents", "duree": "5j"},
        {"nom": "Paris", "pays": "France", "description": "La ville lumière", "duree": "5j"},
        {"nom": "Dubaï", "pays": "EAU", "description": "Luxe et modernité", "duree": "5j"},
    ]
    
    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="card">
                    <h3>📍 {dest['nom']}, {dest['pays']}</h3>
                    <p>{dest['description']}</p>
                    <p>⏱️ {dest['duree']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"✈️ Réserver", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    st.markdown("# 📝 Réservation & Devis")
    
    tab1, tab2 = st.tabs(["✈️ Réservation Voyage", "💰 Demande de Devis"])
    
    with tab1:
        st.markdown("### Formulaire de Réservation")
        with st.form("reservation_form", clear_on_submit=True):
            st.markdown("#### 👤 Informations Personnelles")
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
                                            min_value=datetime.now().date())
                date_retour = st.date_input("Date de retour *", 
                                            min_value=datetime.now().date() + timedelta(days=1))
                nb_personnes = st.number_input("Nombre de personnes", min_value=1, max_value=20, value=1)
            
            # Calcul automatique de la durée
            if date_depart and date_retour:
                if date_retour > date_depart:
                    duree_sejour = (date_retour - date_depart).days
                    st.info(f"📅 Durée du séjour : **{duree_sejour} jour(s)**")
                else:
                    st.warning("⚠️ La date de retour doit être après la date de départ")
            
            message = st.text_area("Message / Demandes spéciales", height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("✈️ Envoyer la demande de réservation", use_container_width=True)
            
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
                            <div class="info-box" style="background: #d4edda; border-left-color: #28a745;">
                                <h4 style="color: #155724;">📧 Confirmation envoyée</h4>
                                <p style="color: #155724;">
                                Un email de confirmation vous a été envoyé à <strong>{email}</strong>
                                </p>
                                <hr style="border-color: #c3e6cb;">
                                <h5 style="color: #155724;">📋 Résumé de votre réservation :</h5>
                                <ul style="color: #155724;">
                                    <li><strong>Destination :</strong> {destination}</li>
                                    <li><strong>Dates :</strong> du {date_depart.strftime('%d/%m/%Y')} au {date_retour.strftime('%d/%m/%Y')} ({duree} jours)</li>
                                    <li><strong>Voyageurs :</strong> {nb_personnes} personne(s)</li>
                                </ul>
                                <p style="color: #155724; margin-top: 15px;">
                                Notre équipe vous contactera dans les 24 heures pour finaliser votre réservation.
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
                Recevez un devis détaillé et personnalisé pour votre voyage. 
                Indiquez vos dates, destination et préférences, et notre équipe vous répondra sous 24h.
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
                                                   key="devis_date_dep")
            
            with col5:
                devis_date_retour = st.date_input("Date de retour *", 
                                                   min_value=datetime.now().date() + timedelta(days=1),
                                                   key="devis_date_ret")
            
            # Calcul automatique de la durée
            if devis_date_depart and devis_date_retour:
                if devis_date_retour > devis_date_depart:
                    duree_sejour = (devis_date_retour - devis_date_depart).days
                    st.info(f"📅 Durée du séjour : **{duree_sejour} jour(s)**")
                else:
                    st.warning("⚠️ La date de retour doit être après la date de départ")
            
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
            
            # Bouton de soumission
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted_devis = st.form_submit_button("📨 Recevoir mon devis gratuit", use_container_width=True)
            
            if submitted_devis:
                # Validation
                if not all([devis_nom, devis_email, devis_telephone, devis_destination, 
                           devis_date_depart, devis_date_retour, devis_ville_depart]):
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                elif devis_destination == "-- Sélectionnez --":
                    st.error("❌ Veuillez sélectionner une destination")
                elif devis_date_retour <= devis_date_depart:
                    st.error("❌ La date de retour doit être après la date de départ")
                else:
                    # Calcul de la durée
                    duree = (devis_date_retour - devis_date_depart).days
                    nb_total_personnes = devis_nb_adultes + devis_nb_enfants
                    
                    # Préparation des données
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
                    
                    # Envoi vers Supabase
                    success, msg = add_devis(devis_data)
                    
                    if success:
                        st.success(msg)
                        st.markdown(f"""
                            <div class="info-box" style="background: #d4edda; border-left-color: #28a745;">
                                <h4 style="color: #155724;">📧 Demande de devis enregistrée</h4>
                                <p style="color: #155724;">
                                Un email de confirmation a été envoyé à <strong>{devis_email}</strong>
                                </p>
                                <hr style="border-color: #c3e6cb;">
                                <h5 style="color: #155724;">📋 Résumé de votre demande :</h5>
                                <ul style="color: #155724;">
                                    <li><strong>Destination :</strong> {devis_destination}</li>
                                    <li><strong>Dates :</strong> du {devis_date_depart.strftime('%d/%m/%Y')} au {devis_date_retour.strftime('%d/%m/%Y')} ({duree} jours)</li>
                                    <li><strong>Voyageurs :</strong> {devis_nb_adultes} adulte(s) {f"+ {devis_nb_enfants} enfant(s)" if devis_nb_enfants > 0 else ""}</li>
                                    <li><strong>Budget :</strong> {devis_budget}</li>
                                </ul>
                                <p style="color: #155724; margin-top: 15px;">
                                <strong>⏱️ Délai de réponse :</strong> Vous recevrez votre devis détaillé sous 24 heures ouvrables.
                                </p>
                                <p style="color: #155724;">
                                <strong>📞 Questions ?</strong> Contactez-nous au +213 XXX XXX XXX
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
            <h3>🌍 Nos Services Visa</h3>
            <p>HCM Voyages vous accompagne pour l'obtention de vos visas (USA, UK, Schengen, Canada...)</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("visa_form", clear_on_submit=True):
        st.markdown("#### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        with col1:
            v_nom = st.text_input("Nom complet *", key="v_nom")
            v_naissance = st.date_input("Date de naissance *", key="v_naissance")
            v_nationalite = st.text_input("Nationalité *", key="v_nat")
        with col2:
            v_email = st.text_input("Email *", key="v_email")
            v_tel = st.text_input("Téléphone *", key="v_tel")
            v_passeport = st.text_input("N° Passeport *", key="v_pass")
        
        st.markdown("#### 🌍 Informations Visa")
        col3, col4 = st.columns(2)
        with col3:
            v_pays = st.selectbox("Pays *", ["USA", "UK", "France (Schengen)", "Canada", "Autre"], key="v_pays")
            v_type = st.selectbox("Type *", ["Tourisme", "Affaires", "Études", "Visite familiale"], key="v_type")
        with col4:
            v_depart = st.date_input("Date départ prévue *", min_value=datetime.now().date(), key="v_depart")
            v_duree = st.number_input("Durée (jours) *", min_value=1, value=15, key="v_duree")
        
        v_msg = st.text_area("Informations complémentaires", key="v_msg")
        
        v_accepte = st.checkbox("J'accepte le traitement de mes données *", key="v_accepte")
        
        submitted_visa = st.form_submit_button("📨 Envoyer ma demande", use_container_width=True)
        
        if submitted_visa:
            if all([v_nom, v_email, v_tel, v_pays, v_type, v_accepte]):
                data = {
                    "nom_complet": v_nom, "email": v_email, "telephone": v_tel,
                    "date_naissance": str(v_naissance), "nationalite": v_nationalite,
                    "numero_passeport": v_passeport, "pays_destination": v_pays,
                    "type_visa": v_type, "date_depart_prevue": str(v_depart),
                    "duree_sejour": v_duree, "message_complementaire": v_msg,
                    "statut": "en_attente"
                }
                success, msg = add_demande_visa(data)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
            else:
                st.error("❌ Remplissez tous les champs obligatoires")

def page_discover_algeria():
    st.markdown("""
        <div class="hero-section" style="height: 400px;">
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 4em;">🇩🇿</div>
                    <h1 class="hero-title">Discover Algeria</h1>
                    <p class="hero-subtitle">Explorez la beauté du Maghreb</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏠 Présentation", "🗺️ Destinations"])
    
    with tab1:
        st.markdown("""
            <div class="info-box">
                <h3>🇩🇿 Bienvenue en Algérie</h3>
                <p>L'Algérie, perle du Maghreb, vous invite à découvrir ses trésors. 
                Du Sahara majestueux aux plages méditerranéennes.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        destinations_dz = [
            {"nom": "Alger", "description": "La capitale avec sa Casbah UNESCO"},
            {"nom": "Sahara", "description": "Le plus grand désert du monde"},
            {"nom": "Constantine", "description": "Ville des ponts suspendus"}
        ]
        cols = st.columns(3)
        for idx, dest in enumerate(destinations_dz):
            with cols[idx]:
                st.markdown(f"""
                    <div class="card">
                        <h3>🇩🇿 {dest['nom']}</h3>
                        <p>{dest['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

def page_contact():
    st.markdown("# 📞 Contactez-Nous")
    st.markdown("Notre équipe est à votre écoute pour répondre à toutes vos questions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h3 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">📍 Notre Agence</h3>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>🏢 Adresse:</strong><br>
                    Aïn Benian, Alger<br>
                    Algérie 16061
                </div>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>📞 Téléphone:</strong><br>
                    +213 XXX XXX XXX
                </div>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>📱 WhatsApp:</strong><br>
                    +213 XXX XXX XXX
                </div>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>📧 Email:</strong><br>
                    contact@hcmvoyages.dz
                </div>
                <div style="padding: 10px 0;">
                    <strong>🕐 Horaires d'ouverture:</strong><br>
                    Dimanche - Jeudi: 9h00 - 18h00<br>
                    Samedi: 9h00 - 13h00<br>
                    Vendredi: Fermé
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card">
                <h3 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">🌐 Suivez-nous</h3>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>📘 Facebook:</strong> @HCMVoyages
                </div>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>📷 Instagram:</strong> @hcm_voyages
                </div>
                <div style="padding: 10px 0; border-bottom: 1px solid #f0f0f0;">
                    <strong>🐦 Twitter:</strong> @HCMVoyages
                </div>
                <div style="padding: 10px 0;">
                    <strong>💼 LinkedIn:</strong> HCM Voyages
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">💬 Envoyez-nous un message</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone", placeholder="+213 XXX XXX XXX")
            sujet = st.selectbox("Sujet *", [
                "-- Sélectionnez --",
                "Demande d'information",
                "Réservation",
                "Réclamation",
                "Partenariat",
                "Autre"
            ])
            message = st.text_area("Message *", height=200, 
                                  placeholder="Décrivez votre demande en détail...")
            
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
                    
                    # Enregistrement dans Supabase
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
                                <div class="info-box" style="background: #d4edda; border-left-color: #28a745;">
                                    <h4 style="color: #155724;">📧 Confirmation</h4>
                                    <p style="color: #155724;">
                                    Votre message a bien été enregistré. Notre équipe vous répondra dans les plus brefs délais.
                                    </p>
                                    <p style="color: #155724;">
                                    <strong>📞 Besoin urgent ?</strong> Appelez-nous au +213 XXX XXX XXX
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'envoi: {str(e)}")
                    else:
                        st.warning("⚠️ Base de données non connectée. Veuillez nous contacter directement.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <h4 style="color: #667eea;">⚡ Réponse rapide</h4>
                <p>Nous nous engageons à répondre à tous les messages dans un délai de 24 heures ouvrables.</p>
            </div>
        """, unsafe_allow_html=True)

def page_admin():
    st.markdown("# 🔐 Administration")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login"):
            username = st.text_input("Utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Connexion"):
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hash_password(password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        return
    
    if st.button("🚪 Déconnexion"):
        st.session_state.authenticated = False
        st.rerun()
    
    tab1, tab2 = st.tabs(["📋 Réservations", "📧 Messages"])
    
    with tab1:
        reservations = get_reservations()
        if reservations:
            df = pd.DataFrame(reservations)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucune réservation")
    
    with tab2:
        contacts = get_contacts()
        if contacts:
            for c in contacts:
                with st.expander(f"{c.get('nom')} - {c.get('sujet')}"):
                    st.write(f"**Email:** {c.get('email')}")
                    st.write(f"**Message:** {c.get('message')}")
        else:
            st.info("Aucun message")

# ====== NAVIGATION ======
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(size="120px")
        st.markdown("---")
        
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
            if st.button(f"{icon} {label}", use_container_width=True):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("<div style='text-align: center;'>© 2024 HCM Voyages</div>", unsafe_allow_html=True)
    
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
