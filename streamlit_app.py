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

# ====== LOGO ======
def display_logo(size: str = "150px"):
    try:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown(f'<div style="text-align: center; margin: 20px 0; font-size: {size};">✈️</div>', 
                   unsafe_allow_html=True)

# ====== CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    .hero-section {
        position: relative; width: 100%; height: 500px; border-radius: 20px;
        overflow: hidden; margin-bottom: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .hero-overlay {
        position: absolute; top: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        display: flex; justify-content: center; align-items: center; padding: 40px;
    }
    .hero-title { color: white; font-size: 4em; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .hero-subtitle { color: white; font-size: 1.8em; font-weight: 300; margin: 20px 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); }
    
    .card {
        background: white; padding: 25px; border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 15px 0;
        transition: all 0.3s ease; border: 2px solid transparent;
    }
    .card:hover { transform: translateY(-8px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3); border-color: #667eea; }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        border-radius: 30px; padding: 12px 35px; border: none; font-weight: 600;
        transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5); }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 20px; border-radius: 15px; border-left: 5px solid #667eea; margin: 20px 0;
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
    except:
        pass
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
    
    tab1, tab2 = st.tabs(["✈️ Réservation", "💰 Demande de Devis"])
    
    with tab1:
        with st.form("reservation_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom complet *")
                email = st.text_input("Email *")
                telephone = st.text_input("Téléphone *")
            with col2:
                destination = st.text_input("Destination *", value=st.session_state.get('destination_selectionnee', ''))
                date_depart = st.date_input("Date départ *", min_value=datetime.now().date())
                date_retour = st.date_input("Date retour *", min_value=datetime.now().date() + timedelta(days=1))
                nb_personnes = st.number_input("Personnes", min_value=1, value=1)
            
            message = st.text_area("Message", height=100)
            submitted = st.form_submit_button("✈️ Envoyer", use_container_width=True)
            
            if submitted:
                if all([nom, email, telephone, destination]) and date_retour > date_depart:
                    duree = (date_retour - date_depart).days
                    data = {"nom": nom, "email": email, "telephone": telephone, "destination": destination,
                           "date_depart": date_depart, "date_retour": date_retour, "nb_personnes": nb_personnes,
                           "duree_sejour": duree, "message": message}
                    success, msg = add_reservation(data)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Vérifiez les champs")
    
    with tab2:
        st.markdown("### 💰 Demande de Devis Personnalisé")
        with st.form("devis_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                d_nom = st.text_input("Nom *", key="d_nom")
                d_email = st.text_input("Email *", key="d_email")
                d_tel = st.text_input("Téléphone *", key="d_tel")
            with col2:
                d_dest = st.selectbox("Destination *", ["Paris", "Istanbul", "Dubaï", "Autre"], key="d_dest")
                d_dep = st.date_input("Date départ *", min_value=datetime.now().date(), key="d_dep")
                d_ret = st.date_input("Date retour *", min_value=datetime.now().date() + timedelta(days=1), key="d_ret")
            
            d_adultes = st.number_input("Adultes", min_value=1, value=1, key="d_adultes")
            d_enfants = st.number_input("Enfants", min_value=0, value=0, key="d_enfants")
            d_budget = st.select_slider("Budget", ["500-1000€", "1000-2000€", "2000-3000€", "3000€+"], key="d_budget")
            d_msg = st.text_area("Commentaires", key="d_msg")
            
            submitted_devis = st.form_submit_button("📨 Recevoir mon devis", use_container_width=True)
            
            if submitted_devis:
                if all([d_nom, d_email, d_tel, d_dest]) and d_ret > d_dep:
                    duree = (d_ret - d_dep).days
                    data = {"nom": d_nom, "email": d_email, "telephone": d_tel, "destination": d_dest,
                           "date_depart": str(d_dep), "date_retour": str(d_ret), "duree_sejour": duree,
                           "nb_adultes": d_adultes, "nb_enfants": d_enfants, "budget_approximatif": d_budget,
                           "commentaires": d_msg, "statut": "en_attente"}
                    success, msg = add_devis(data)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.error("❌ Vérifiez les champs")

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
