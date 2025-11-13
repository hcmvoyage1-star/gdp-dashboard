"""
HCM VOYAGES - Application Streamlit
Agence de voyage complète avec gestion des réservations, destinations et visas

SCHÉMA SQL ADDITIONNEL POUR LES VISAS (à ajouter dans Supabase) :

CREATE TABLE demandes_visa (
    id BIGSERIAL PRIMARY KEY,
    reference VARCHAR(20) UNIQUE,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telephone VARCHAR(50) NOT NULL,
    date_naissance DATE,
    lieu_naissance VARCHAR(255),
    adresse TEXT,
    profession VARCHAR(255),
    type_visa VARCHAR(100) NOT NULL,
    pays_destination VARCHAR(100),
    motif_voyage TEXT,
    date_arrivee DATE,
    date_depart_voyage DATE,
    duree_sejour INTEGER,
    statut VARCHAR(50) DEFAULT 'En cours' CHECK (statut IN ('En cours', 'RDV programmé', 'Documents incomplets', 'Approuvé', 'Rejeté', 'En attente')),
    date_demande TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_rdv TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    voyage_anterieur BOOLEAN DEFAULT FALSE,
    service_prioritaire BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX idx_demandes_visa_statut ON demandes_visa(statut);
CREATE INDEX idx_demandes_visa_email ON demandes_visa(email);
CREATE INDEX idx_demandes_visa_date ON demandes_visa(date_demande DESC);
CREATE INDEX idx_demandes_visa_type ON demandes_visa(type_visa);

-- Générer automatiquement une référence unique
CREATE OR REPLACE FUNCTION generate_visa_reference()
RETURNS TRIGGER AS $
BEGIN
    NEW.reference := CONCAT(
        CASE 
            WHEN NEW.type_visa LIKE '%USA%' THEN 'VUS'
            WHEN NEW.type_visa LIKE '%UK%' THEN 'VUK'
            WHEN NEW.type_visa LIKE '%Schengen%' THEN 'VSC'
            ELSE 'VIS'
        END,
        LPAD(CAST(NEW.id AS TEXT), 4, '0')
    );
    RETURN NEW;
END;
$ LANGUAGE plpgsql;

CREATE TRIGGER set_visa_reference
    AFTER INSERT ON demandes_visa
    FOR EACH ROW
    EXECUTE FUNCTION generate_visa_reference();

-- Trigger pour updated_at
CREATE TRIGGER update_demandes_visa_modtime
    BEFORE UPDATE ON demandes_visa
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- RLS Policies
ALTER TABLE demandes_visa ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert visa requests"
    ON demandes_visa FOR INSERT
    WITH CHECK (true);
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image
import requests

# Configuration de la page
st.set_page_config(
    page_title="HCM Voyages - L'évasion sur mesure",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONFIGURATION SUPABASE ======
SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"  # ex: https://xxxxx.supabase.co
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"  # Votre clé API publique



# OPTION 2 : Chemin local du logo
LOGO_PATH = "logo.png"  # Si le logo est dans le même dossier que l'app

# Initialisation du client Supabase
@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

# ====== FONCTION POUR CHARGER LE LOGO ======
@st.cache_data
def get_logo_base64(image_path):
    """Convertit une image locale en base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def display_logo(size="150px"):
    """Affiche le logo (URL ou local)"""
    try:
        # Essayer d'abord l'URL
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <img src="{LOGO_URL}" width="{size}" style="border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            </div>
        """, unsafe_allow_html=True)
    except:
        # Si l'URL ne fonctionne pas, essayer le fichier local
        logo_base64 = get_logo_base64(LOGO_PATH)
        if logo_base64:
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{logo_base64}" width="{size}" style="border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                </div>
            """, unsafe_allow_html=True)
        else:
            # Afficher emoji par défaut si aucun logo n'est trouvé
            st.markdown(f"""
                <div style="text-align: center; margin: 20px 0; font-size: 5em;">
                    ✈️
                </div>
            """, unsafe_allow_html=True)

# ====== CSS PERSONNALISÉ AMÉLIORÉ ======
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Hero Section */
    .hero-section {
        position: relative;
        width: 100%;
        height: 500px;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .hero-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.7);
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px;
    }
    
    .hero-title {
        color: white;
        font-size: 4em;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: fadeInDown 1s ease-out;
    }
    
    .hero-subtitle {
        color: white;
        font-size: 1.8em;
        font-weight: 300;
        margin: 20px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        animation: fadeInUp 1s ease-out 0.3s backwards;
    }
    
    .hero-logo {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: white;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: bounceIn 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Destination Cards */
    .destination-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .destination-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0;
        transition: opacity 0.4s;
        z-index: 0;
    }
    
    .destination-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        border-color: #667eea;
    }
    
    .destination-card:hover::before {
        opacity: 0.05;
    }
    
    .destination-card > * {
        position: relative;
        z-index: 1;
    }
    
    .destination-card h3 {
        color: #667eea;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    .destination-card:hover h3 {
        color: #764ba2;
    }
    
    .price-tag {
        color: #ff6b6b;
        font-size: 28px;
        font-weight: 700;
        margin-top: 15px;
        display: inline-block;
        padding: 10px 20px;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
        border-radius: 15px;
    }
    
    /* Service Cards */
    .service-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.3s ease;
        text-align: center;
        border: 2px solid transparent;
    }
    
    .service-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .service-icon {
        font-size: 3em;
        margin-bottom: 15px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px;
        padding: 12px 35px;
        border: none;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2em;
        color: #667eea;
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: white;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Forms */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>div,
    .stNumberInput>div>div>input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 20px 0;
    }
    
    /* Contact card */
    .contact-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
    
    .contact-card h3 {
        color: #667eea;
        margin-bottom: 20px;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    
    .contact-item {
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .contact-item:last-child {
        border-bottom: none;
    }
    
    /* Admin section */
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    /* Animations */
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
    
    .animate-slide-in {
        animation: slideInLeft 0.6s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5em;
        }
        .hero-subtitle {
            font-size: 1.2em;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======

def get_destinations():
    """Récupère toutes les destinations actives depuis Supabase"""
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur de connexion à Supabase: {e}")
            return []
    return []

def add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
    """Ajoute une réservation dans Supabase"""
    if supabase:
        try:
            data = {
                "nom": nom,
                "email": email,
                "telephone": telephone,
                "destination": destination,
                "date_depart": str(date_depart),
                "nb_personnes": nb_personnes,
                "message": message,
                "statut": "en_attente"
            }
            response = supabase.table('reservations').insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erreur lors de l'ajout: {e}")
            return False
    return False

def get_reservations():
    """Récupère toutes les réservations"""
    if supabase:
        try:
            response = supabase.table('reservations').select("*").order('date_creation', desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur: {e}")
            return []
    return []

def add_destination(nom, pays, description, prix, categorie, image_url):
    """Ajoute une nouvelle destination"""
    if supabase:
        try:
            data = {
                "nom": nom,
                "pays": pays,
                "description": description,
                "prix": prix,
                "categorie": categorie,
                "image_url": image_url,
                "actif": True
            }
            response = supabase.table('destinations').insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def update_reservation_status(reservation_id, nouveau_statut):
    """Met à jour le statut d'une réservation"""
    if supabase:
        try:
            response = supabase.table('reservations').update(
                {"statut": nouveau_statut}
            ).eq('id', reservation_id).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def delete_destination(destination_id):
    """Désactive une destination (soft delete)"""
    if supabase:
        try:
            response = supabase.table('destinations').update(
                {"actif": False}
            ).eq('id', destination_id).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def update_destination(destination_id, data):
    """Met à jour une destination"""
    if supabase:
        try:
            response = supabase.table('destinations').update(data).eq('id', destination_id).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def add_contact(nom, email, sujet, message):
    """Ajoute un message de contact"""
    if supabase:
        try:
            data = {
                "nom": nom,
                "email": email,
                "sujet": sujet,
                "message": message,
                "lu": False
            }
            response = supabase.table('contacts').insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def get_contacts(lu=None):
    """Récupère les messages de contact"""
    if supabase:
        try:
            query = supabase.table('contacts').select("*").order('date_creation', desc=True)
            if lu is not None:
                query = query.eq('lu', lu)
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur: {e}")
            return []
    return []

def mark_contact_as_read(contact_id):
    """Marque un message de contact comme lu"""
    if supabase:
        try:
            response = supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def get_stats_reservations():
    """Récupère les statistiques des réservations"""
    if supabase:
        try:
            response = supabase.table('stats_reservations').select("*").execute()
            return response.data
        except Exception as e:
            return []
    return []

def get_destinations_populaires():
    """Récupère les destinations populaires"""
    if supabase:
        try:
            response = supabase.table('destinations_populaires').select("*").limit(5).execute()
            return response.data
        except Exception as e:
            return []
    return []

# ====== FONCTIONS VISA (à ajouter au schéma SQL) ======

def add_demande_visa(data):
    """Ajoute une demande de visa"""
    if supabase:
        try:
            response = supabase.table('demandes_visa').insert(data).execute()
            return True, response.data[0].get('id') if response.data else None
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False, None
    return False, None

def get_demandes_visa(statut=None):
    """Récupère les demandes de visa"""
    if supabase:
        try:
            query = supabase.table('demandes_visa').select("*").order('date_demande', desc=True)
            if statut:
                query = query.eq('statut', statut)
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur: {e}")
            return []
    return []

def update_visa_status(visa_id, nouveau_statut, notes=None):
    """Met à jour le statut d'une demande de visa"""
    if supabase:
        try:
            data = {"statut": nouveau_statut}
            if notes:
                data["notes"] = notes
            response = supabase.table('demandes_visa').update(data).eq('id', visa_id).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

# ====== PAGES DE L'APPLICATION ======

def page_accueil():
    """Page d'accueil avec hero section"""
    
    # Hero Section avec l'image de couverture et logo
    st.markdown("""
        <div class="hero-section">
            <img src="https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1920&h=600&fit=crop" 
                 alt="HCM Voyages" class="hero-image"/>
            <div class="hero-overlay">
                <div style="text-align: center;">
    """, unsafe_allow_html=True)
    
    # Afficher le logo
    display_logo(size="200px")
    
    st.markdown("""
                    <h1 class="hero-title">HCM VOYAGES</h1>
                    <p class="hero-subtitle">L'évasion sur mesure, explorez, rêvez, partez</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistiques avec animation
    st.markdown("### 🎯 Pourquoi nous choisir ?")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div style="font-size: 3em; margin-bottom: 10px;">🌍</div>
                <h2 style="color: #667eea; margin: 0;">50+</h2>
                <p style="margin: 10px 0 0 0; color: #666;">Destinations</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div style="font-size: 3em; margin-bottom: 10px;">😊</div>
                <h2 style="color: #667eea; margin: 0;">1000+</h2>
                <p style="margin: 10px 0 0 0; color: #666;">Clients Satisfaits</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="stat-card">
                <div style="font-size: 3em; margin-bottom: 10px;">📅</div>
                <h2 style="color: #667eea; margin: 0;">10+</h2>
                <p style="margin: 10px 0 0 0; color: #666;">Années d'Expérience</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="stat-card">
                <div style="font-size: 3em; margin-bottom: 10px;">🤝</div>
                <h2 style="color: #667eea; margin: 0;">25+</h2>
                <p style="margin: 10px 0 0 0; color: #666;">Partenaires</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Nos services
    st.markdown("### 🎯 Nos Services Premium")
    
    col1, col2, col3 = st.columns(3)
    
    services = [
        ("🎫", "Billets d'Avion", "Les meilleurs tarifs pour toutes destinations mondiales"),
        ("🏨", "Réservation Hôtels", "Hébergements de qualité soigneusement sélectionnés"),
        ("🎒", "Circuits Organisés", "Voyages tout compris clés en main"),
        ("🚗", "Location de Voitures", "Mobilité à destination garantie"),
        ("📋", "Assistance Visa", "Aide complète pour vos démarches administratives"),
        ("💼", "Voyages Affaires", "Solutions professionnelles sur mesure")
    ]
    
    for i, (icon, titre, desc) in enumerate(services):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
                <div class="service-card">
                    <div class="service-icon">{icon}</div>
                    <h3 style="color: #667eea; margin: 15px 0;">{titre}</h3>
                    <p style="color: #666; margin: 0;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="info-box" style="text-align: center; border-left: none;">
                <h3 style="color: #667eea; margin-bottom: 15px;">🌟 Prêt pour l'aventure ?</h3>
                <p style="font-size: 1.1em; color: #666;">Découvrez nos destinations de rêve et réservez votre prochain voyage en quelques clics</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🌍 Découvrir nos destinations", key="cta_destinations", use_container_width=True):
            st.session_state.page = "destinations"
            st.rerun()

def page_destinations():
    """Page des destinations améliorée"""
    st.markdown("# 🌍 Nos Destinations de Rêve")
    st.markdown("Explorez le monde avec HCM Voyages")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filtres améliorés
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Rechercher une destination", "", placeholder="Paris, Istanbul, Maldives...")
    with col2:
        categorie = st.selectbox("📍 Continent", ["Toutes", "Europe", "Asie", "Afrique", "Amérique", "Océanie"])
    with col3:
        tri = st.selectbox("💰 Trier par", ["Prix croissant", "Prix décroissant", "Nom A-Z"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Récupération des destinations
    destinations = get_destinations()
    
    if not destinations:
        st.info("📌 Connectez votre base de données Supabase pour afficher les destinations réelles")
        # Destinations exemple avec plus de détails
        destinations = [
            {"nom": "Paris", "pays": "France", "description": "La ville lumière vous accueille avec ses monuments iconiques", "prix": 799, "categorie": "Europe", "duree": "5 jours"},
            {"nom": "Istanbul", "pays": "Turquie", "description": "Entre Orient et Occident, découvrez une ville fascinante", "prix": 599, "categorie": "Europe", "duree": "4 jours"},
            {"nom": "Maldives", "pays": "Maldives", "description": "Paradis tropical aux eaux cristallines", "prix": 1499, "categorie": "Asie", "duree": "7 jours"},
            {"nom": "Tokyo", "pays": "Japon", "description": "Tradition et modernité dans la capitale nippone", "prix": 1299, "categorie": "Asie", "duree": "6 jours"},
            {"nom": "Dubaï", "pays": "EAU", "description": "Luxe et désert dans la cité futuriste", "prix": 899, "categorie": "Asie", "duree": "5 jours"},
            {"nom": "Rome", "pays": "Italie", "description": "Histoire antique et dolce vita", "prix": 699, "categorie": "Europe", "duree": "4 jours"},
            {"nom": "Barcelone", "pays": "Espagne", "description": "Art, plages et gastronomie catalane", "prix": 649, "categorie": "Europe", "duree": "4 jours"},
            {"nom": "New York", "pays": "USA", "description": "La ville qui ne dort jamais", "prix": 1099, "categorie": "Amérique", "duree": "6 jours"},
            {"nom": "Bali", "pays": "Indonésie", "description": "Îles des dieux, temples et rizières", "prix": 1199, "categorie": "Asie", "duree": "8 jours"},
        ]
    
    # Filtrage
    if search:
        destinations = [d for d in destinations if 
                       search.lower() in d['nom'].lower() or 
                       search.lower() in d['pays'].lower()]
    
    if categorie != "Toutes":
        destinations = [d for d in destinations if d.get('categorie') == categorie]
    
    # Tri
    if tri == "Prix croissant":
        destinations = sorted(destinations, key=lambda x: x['prix'])
    elif tri == "Prix décroissant":
        destinations = sorted(destinations, key=lambda x: x['prix'], reverse=True)
    else:
        destinations = sorted(destinations, key=lambda x: x['nom'])
    
    # Affichage en grille
    if destinations:
        st.markdown(f"### {len(destinations)} destination(s) trouvée(s)")
        
        cols = st.columns(3)
        for idx, dest in enumerate(destinations):
            with cols[idx % 3]:
                duree = dest.get('duree', '5 jours')
                st.markdown(f"""
                    <div class="destination-card">
                        <h3>📍 {dest['nom']}, {dest['pays']}</h3>
                        <p style="color: #666; margin: 10px 0;">{dest['description']}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
                            <span style="color: #888;">⏱️ {duree}</span>
                        </div>
                        <div class="price-tag">À partir de {dest['prix']}€</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.destination_selectionnee = dest['nom']
                    st.session_state.page = "reservation"
                    st.rerun()
    else:
        st.warning("😔 Aucune destination ne correspond à votre recherche")

def page_reservation():
    """Page de réservation améliorée"""
    st.markdown("# 📝 Réserver Votre Voyage de Rêve")
    st.markdown("Remplissez le formulaire ci-dessous et notre équipe vous contactera rapidement")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("reservation_form", clear_on_submit=True):
        st.markdown("### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Ex: Ahmed Benali")
            email = st.text_input("Email *", placeholder="exemple@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("Destination *", 
                                       value=st.session_state.get('destination_selectionnee', ''),
                                       placeholder="Ex: Paris, Istanbul...")
            date_depart = st.date_input("Date de départ *", min_value=datetime.now().date())
            nb_personnes = st.number_input("Nombre de personnes", min_value=1, max_value=20, value=1)
        
        st.markdown("### 💬 Informations Complémentaires")
        message = st.text_area("Message / Demandes spéciales", 
                              placeholder="Vos préférences, questions, besoins particuliers...",
                              height=150)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("✈️ Envoyer la demande de réservation", use_container_width=True)
        
        if submitted:
            if nom and email and telephone and destination:
                if add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
                    st.success("✅ Votre demande a été envoyée avec succès!")
                    st.markdown("""
                        <div class="info-box">
                            <h4>📧 Confirmation envoyée</h4>
                            <p>Un email de confirmation vous a été envoyé à <strong>{}</strong></p>
                            <p>Notre équipe vous contactera dans les 24 heures pour finaliser votre réservation.</p>
                        </div>
                    """.format(email), unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning("⚠️ Demande enregistrée localement. Connectez Supabase pour la sauvegarde permanente.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

def page_visas():
    """Page de gestion des visas"""
    st.markdown("# 📋 Rendez-vous & Traitement de Visas")
    st.markdown("Nous vous accompagnons dans toutes vos démarches de visa")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section informative
    st.markdown("""
        <div class="info-box" style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);">
            <h3 style="color: #667eea; margin-bottom: 15px;">🎯 Nos Services Visa</h3>
            <p>HCM Voyages vous accompagne dans l'obtention de vos visas pour les destinations suivantes :</p>
            <ul>
                <li><strong>🇺🇸 USA (Visa B1/B2, ESTA)</strong> - Tourisme & Affaires</li>
                <li><strong>🇬🇧 UK (Visa Standard Visitor)</strong> - Tourisme, Famille, Affaires</li>
                <li><strong>🇪🇺 Schengen (Type C)</strong> - 26 pays européens</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sélection du type de visa
    tab1, tab2, tab3, tab4 = st.tabs([
        "🇺🇸 Visa USA", 
        "🇬🇧 Visa UK", 
        "🇪🇺 Visa Schengen",
        "📋 Mes Demandes"
    ])
    
    with tab1:
        visa_usa_section()
    
    with tab2:
        visa_uk_section()
    
    with tab3:
        visa_schengen_section()
    
    with tab4:
        mes_demandes_visa()

def visa_usa_section():
    """Section visa USA"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="service-card" style="text-align: left;">
                <h3 style="color: #667eea;">🇺🇸 Visa USA - Informations</h3>
                
                <h4 style="color: #764ba2; margin-top: 20px;">Types de visa disponibles :</h4>
                <ul>
                    <li><strong>B1/B2</strong> - Tourisme & Affaires (6 mois)</li>
                    <li><strong>ESTA</strong> - Exemption de visa (90 jours)</li>
                </ul>
                
                <h4 style="color: #764ba2; margin-top: 20px;">📄 Documents requis :</h4>
                <ul>
                    <li>Passeport valide (6 mois minimum)</li>
                    <li>Photo d'identité récente (format US)</li>
                    <li>Formulaire DS-160 complété</li>
                    <li>Justificatifs financiers</li>
                    <li>Lettre d'invitation (si applicable)</li>
                    <li>Attestation de travail</li>
                    <li>Relevés bancaires (3 derniers mois)</li>
                </ul>
                
                <h4 style="color: #764ba2; margin-top: 20px;">⏱️ Délai de traitement :</h4>
                <p>3 à 6 semaines après l'entretien</p>
                
                <h4 style="color: #764ba2; margin-top: 20px;">💰 Tarifs :</h4>
                <ul>
                    <li>Frais consulaires : 160 USD</li>
                    <li>Nos services : 15 000 DZD</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📝 Demande de Rendez-vous Visa USA")
        
        with st.form("visa_usa_form"):
            type_visa_usa = st.selectbox("Type de visa", ["B1/B2 - Tourisme & Affaires", "ESTA"])
            
            st.markdown("#### 👤 Informations Personnelles")
            nom = st.text_input("Nom complet *", placeholder="Nom et prénom")
            date_naissance = st.date_input("Date de naissance *", 
                                          min_value=datetime(1920, 1, 1),
                                          max_value=datetime.now() - timedelta(days=365*18))
            lieu_naissance = st.text_input("Lieu de naissance *")
            
            col_a, col_b = st.columns(2)
            with col_a:
                email = st.text_input("Email *", placeholder="votre@email.com")
                telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            with col_b:
                adresse = st.text_input("Adresse complète *")
                profession = st.text_input("Profession *")
            
            st.markdown("#### 🎯 Détails du Voyage")
            motif = st.selectbox("Motif du voyage", [
                "Tourisme",
                "Visite familiale",
                "Affaires",
                "Conférence/Séminaire",
                "Études",
                "Autre"
            ])
            
            col_c, col_d = st.columns(2)
            with col_c:
                date_depart_souhaitee = st.date_input("Date de départ souhaitée", 
                                                      min_value=datetime.now().date())
                duree_sejour = st.number_input("Durée du séjour (jours)", 
                                              min_value=1, max_value=180, value=15)
            with col_d:
                destination_usa = st.text_input("Ville de destination", placeholder="New York, Los Angeles...")
                voyage_anterieur = st.selectbox("Voyage antérieur aux USA ?", ["Non", "Oui"])
            
            a_passeport = st.checkbox("Je possède un passeport valide (min. 6 mois)")
            
            message = st.text_area("Informations complémentaires", 
                                  placeholder="Précisez vos besoins, questions...",
                                  height=100)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("📨 Envoyer la demande", use_container_width=True):
                if nom and email and telephone and a_passeport:
                    # Sauvegarder la demande (à implémenter avec Supabase)
                    st.success("✅ Votre demande de visa USA a été envoyée avec succès!")
                    st.markdown("""
                        <div class="info-box">
                            <h4>📧 Prochaines étapes</h4>
                            <ol>
                                <li>Vous recevrez un email de confirmation</li>
                                <li>Notre équipe vous contactera sous 24h</li>
                                <li>Préparation du dossier et prise de RDV</li>
                                <li>Accompagnement jusqu'à l'obtention du visa</li>
                            </ol>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")

def visa_uk_section():
    """Section visa UK"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="service-card" style="text-align: left;">
                <h3 style="color: #667eea;">🇬🇧 Visa UK - Informations</h3>
                
                <h4 style="color: #764ba2; margin-top: 20px;">Types de visa disponibles :</h4>
                <ul>
                    <li><strong>Standard Visitor</strong> - Tourisme (6 mois)</li>
                    <li><strong>Family Visitor</strong> - Visite familiale</li>
                    <li><strong>Business Visitor</strong> - Affaires</li>
                </ul>
                
                <h4 style="color: #764ba2; margin-top: 20px;">📄 Documents requis :</h4>
                <ul>
                    <li>Passeport valide (6 mois minimum)</li>
                    <li>Photo d'identité biométrique</li>
                    <li>Formulaire en ligne complété</li>
                    <li>Justificatifs d'hébergement</li>
                    <li>Relevés bancaires (6 derniers mois)</li>
                    <li>Attestation de travail et salaire</li>
                    <li>Lettre d'invitation (si applicable)</li>
                    <li>Réservation de vol (aller-retour)</li>
                </ul>
                
                <h4 style="color: #764ba2; margin-top: 20px;">⏱️ Délai de traitement :</h4>
                <p>3 semaines (service standard)<br>
                5 jours (service prioritaire - supplément)</p>
                
                <h4 style="color: #764ba2; margin-top: 20px;">💰 Tarifs :</h4>
                <ul>
                    <li>Frais consulaires : £100 (≈ 14 000 DZD)</li>
                    <li>Nos services : 12 000 DZD</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📝 Demande de Rendez-vous Visa UK")
        
        with st.form("visa_uk_form"):
            type_visa_uk = st.selectbox("Type de visa", [
                "Standard Visitor - Tourisme",
                "Family Visitor - Visite familiale",
                "Business Visitor - Affaires"
            ])
            
            st.markdown("#### 👤 Informations Personnelles")
            nom = st.text_input("Nom complet *", placeholder="Nom et prénom")
            date_naissance = st.date_input("Date de naissance *",
                                          min_value=datetime(1920, 1, 1),
                                          max_value=datetime.now() - timedelta(days=365*18))
            
            col_a, col_b = st.columns(2)
            with col_a:
                email = st.text_input("Email *", placeholder="votre@email.com")
                telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            with col_b:
                profession = st.text_input("Profession *")
                revenu_mensuel = st.number_input("Revenu mensuel (DZD)", min_value=0)
            
            st.markdown("#### 🎯 Détails du Voyage")
            motif = st.selectbox("Motif principal", [
                "Tourisme",
                "Visite familiale",
                "Affaires",
                "Conférence",
                "Événement",
                "Autre"
            ])
            
            col_c, col_d = st.columns(2)
            with col_c:
                date_arrivee = st.date_input("Date d'arrivée prévue",
                                            min_value=datetime.now().date())
                duree = st.number_input("Durée (jours)", min_value=1, max_value=180, value=10)
            with col_d:
                ville_uk = st.text_input("Ville principale", placeholder="Londres, Manchester...")
                hebergement_type = st.selectbox("Type d'hébergement", [
                    "Hôtel",
                    "Chez famille/amis",
                    "Location Airbnb",
                    "Autre"
                ])
            
            service_prioritaire = st.checkbox("Service prioritaire (5 jours - supplément £212)")
            
            message = st.text_area("Informations complémentaires", height=100)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("📨 Envoyer la demande", use_container_width=True):
                if nom and email and telephone:
                    st.success("✅ Votre demande de visa UK a été envoyée!")
                    st.info("📧 Notre équipe vous contactera sous 24h pour la suite du processus")
                    st.balloons()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")

def visa_schengen_section():
    """Section visa Schengen"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="service-card" style="text-align: left;">
                <h3 style="color: #667eea;">🇪🇺 Visa Schengen - Informations</h3>
                
                <h4 style="color: #764ba2; margin-top: 20px;">Pays Schengen (26 pays) :</h4>
                <p style="font-size: 0.9em;">
                🇫🇷 France • 🇩🇪 Allemagne • 🇮🇹 Italie • 🇪🇸 Espagne • 🇵🇹 Portugal<br>
                🇬🇷 Grèce • 🇦🇹 Autriche • 🇧🇪 Belgique • 🇳🇱 Pays-Bas • 🇨🇭 Suisse<br>
                🇸🇪 Suède • 🇳🇴 Norvège • 🇩🇰 Danemark • 🇫🇮 Finlande • 🇵🇱 Pologne<br>
                🇨🇿 Tchéquie • 🇭🇺 Hongrie • 🇸🇮 Slovénie • 🇸🇰 Slovaquie<br>
                🇪🇪 Estonie • 🇱🇻 Lettonie • 🇱🇹 Lituanie • 🇮🇸 Islande<br>
                🇱🇮 Liechtenstein • 🇱🇺 Luxembourg • 🇲🇹 Malte
                </p>
                
                <h4 style="color: #764ba2; margin-top: 20px;">📄 Documents requis :</h4>
                <ul>
                    <li>Passeport valide (3 mois après le retour)</li>
                    <li>2 photos d'identité récentes</li>
                    <li>Formulaire de demande signé</li>
                    <li>Assurance voyage (30 000€ minimum)</li>
                    <li>Réservation de vol aller-retour</li>
                    <li>Réservation d'hébergement</li>
                    <li>Justificatifs financiers (100€/jour)</li>
                    <li>Attestation de travail</li>
                    <li>Relevés bancaires (3 mois)</li>
                </ul>
                
                <h4 style="color: #764ba2; margin-top: 20px;">⏱️ Délai de traitement :</h4>
                <p>15 jours (peut aller jusqu'à 45 jours)</p>
                
                <h4 style="color: #764ba2; margin-top: 20px;">💰 Tarifs :</h4>
                <ul>
                    <li>Frais consulaires : 80€ (≈ 11 000 DZD)</li>
                    <li>Nos services : 10 000 DZD</li>
                    <li>Assurance voyage : à partir de 3 000 DZD</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📝 Demande de Rendez-vous Visa Schengen")
        
        with st.form("visa_schengen_form"):
            # Sélection du pays
            pays_schengen = st.selectbox("Pays de destination principale *", [
                "🇫🇷 France",
                "🇩🇪 Allemagne",
                "🇮🇹 Italie",
                "🇪🇸 Espagne",
                "🇵🇹 Portugal",
                "🇬🇷 Grèce",
                "🇦🇹 Autriche",
                "🇧🇪 Belgique",
                "🇳🇱 Pays-Bas",
                "🇨🇭 Suisse",
                "🇸🇪 Suède",
                "🇳🇴 Norvège",
                "🇩🇰 Danemark",
                "Autre pays Schengen"
            ])
            
            type_visa_schengen = st.selectbox("Type de visa", [
                "Court séjour - Tourisme (Type C)",
                "Court séjour - Affaires (Type C)",
                "Court séjour - Visite familiale (Type C)",
                "Transit aéroportuaire (Type A)"
            ])
            
            st.markdown("#### 👤 Informations Personnelles")
            nom = st.text_input("Nom complet *", placeholder="Nom et prénom")
            date_naissance = st.date_input("Date de naissance *",
                                          min_value=datetime(1920, 1, 1),
                                          max_value=datetime.now() - timedelta(days=365*18))
            
            col_a, col_b = st.columns(2)
            with col_a:
                email = st.text_input("Email *", placeholder="votre@email.com")
                telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            with col_b:
                profession = st.text_input("Profession *")
                situation_familiale = st.selectbox("Situation familiale", [
                    "Célibataire",
                    "Marié(e)",
                    "Divorcé(e)",
                    "Veuf(ve)"
                ])
            
            st.markdown("#### 🎯 Détails du Voyage")
            col_c, col_d = st.columns(2)
            with col_c:
                date_arrivee = st.date_input("Date d'arrivée",
                                            min_value=datetime.now().date())
                date_depart = st.date_input("Date de départ",
                                           min_value=datetime.now().date())
            with col_d:
                nb_entrees = st.selectbox("Nombre d'entrées", ["Entrée unique", "Entrées multiples"])
                voyage_anterieur_schengen = st.selectbox("Voyage antérieur Schengen ?", ["Non", "Oui"])
            
            motif_detaille = st.text_area("Motif détaillé du voyage *", 
                                         placeholder="Décrivez le but de votre voyage...",
                                         height=100)
            
            # Services additionnels
            st.markdown("#### ➕ Services Additionnels")
            assurance_voyage = st.checkbox("Souscrire à l'assurance voyage (obligatoire)")
            assistance_complete = st.checkbox("Assistance complète (remplissage formulaire + vérification documents)")
            
            message = st.text_area("Informations complémentaires", height=80)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("📨 Envoyer la demande", use_container_width=True):
                if nom and email and telephone and motif_detaille:
                    st.success("✅ Votre demande de visa Schengen a été envoyée!")
                    st.markdown("""
                        <div class="info-box">
                            <h4>📋 Prochaines étapes</h4>
                            <ol>
                                <li>Confirmation par email sous 24h</li>
                                <li>Liste complète des documents à fournir</li>
                                <li>Prise de rendez-vous au consulat</li>
                                <li>Accompagnement personnalisé</li>
                            </ol>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")

def mes_demandes_visa():
    """Affiche les demandes de visa de l'utilisateur"""
    st.markdown("### 📋 Suivi de Mes Demandes")
    
    # Simuler des demandes (à remplacer par vraies données Supabase)
    demandes_exemple = [
        {
            "id": "VUS001",
            "type": "🇺🇸 Visa USA B1/B2",
            "date_demande": "2024-11-01",
            "statut": "En cours",
            "etape": "Dossier en préparation",
            "rdv_date": "2024-11-20"
        },
        {
            "id": "VSC002",
            "type": "🇫🇷 Visa Schengen France",
            "date_demande": "2024-10-25",
            "statut": "Confirmé",
            "etape": "RDV programmé",
            "rdv_date": "2024-11-15"
        }
    ]
    
    st.info("🔐 Connectez-vous pour voir vos demandes réelles")
    
    for demande in demandes_exemple:
        statut_color = {
            'En cours': '#ffa500',
            'Confirmé': '#4caf50',
            'Rejeté': '#f44336',
            'En attente': '#2196f3'
        }.get(demande['statut'], '#666')
        
        with st.expander(f"{demande['type']} - Réf: {demande['id']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                **📅 Date de demande:**  
                {demande['date_demande']}
                
                **🎯 Statut:**  
                <span style="color: {statut_color}; font-weight: bold;">{demande['statut']}</span>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                **📍 Étape actuelle:**  
                {demande['etape']}
                
                **📆 RDV consulat:**  
                {demande['rdv_date']}
                """)
            
            with col3:
                st.button("📄 Voir détails", key=f"detail_{demande['id']}", use_container_width=True)
                st.button("💬 Contacter conseiller", key=f"contact_{demande['id']}", use_container_width=True)

def page_contact():
    """Page de contact améliorée"""
    st.markdown("# 📞 Contactez-Nous")
    st.markdown("Notre équipe est à votre écoute pour répondre à toutes vos questions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="contact-card">
                <h3>📍 Notre Agence</h3>
                <div class="contact-item">
                    <strong>🏢 Adresse:</strong><br>
                    Aïn Benian, Alger<br>
                    Algérie 16061
                </div>
                <div class="contact-item">
                    <strong>📞 Téléphone:</strong><br>
                    +213 XXX XXX XXX
                </div>
                <div class="contact-item">
                    <strong>📱 WhatsApp:</strong><br>
                    +213 XXX XXX XXX
                </div>
                <div class="contact-item">
                    <strong>📧 Email:</strong><br>
                    contact@hcmvoyages.dz
                </div>
                <div class="contact-item">
                    <strong>🕐 Horaires d'ouverture:</strong><br>
                    Dimanche - Jeudi: 9h00 - 18h00<br>
                    Samedi: 9h00 - 13h00<br>
                    Vendredi: Fermé
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="contact-card">
                <h3>🌐 Suivez-nous</h3>
                <div class="contact-item">
                    <strong>📘 Facebook:</strong> @HCMVoyages
                </div>
                <div class="contact-item">
                    <strong>📷 Instagram:</strong> @hcm_voyages
                </div>
                <div class="contact-item">
                    <strong>🐦 Twitter:</strong> @HCMVoyages
                </div>
                <div class="contact-item">
                    <strong>💼 LinkedIn:</strong> HCM Voyages
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="contact-card">
                <h3>💬 Envoyez-nous un message</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("contact_form"):
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone", placeholder="+213 XXX XXX XXX")
            sujet = st.selectbox("Sujet *", [
                "Demande d'information",
                "Réservation",
                "Réclamation",
                "Partenariat",
                "Autre"
            ])
            message = st.text_area("Message *", height=200, 
                                  placeholder="Décrivez votre demande en détail...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("📨 Envoyer le message", use_container_width=True):
                if nom and email and message:
                    st.success("✅ Message envoyé avec succès! Nous vous répondrons dans les plus brefs délais.")
                    st.balloons()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <h4>⚡ Réponse rapide</h4>
                <p>Nous nous engageons à répondre à tous les messages dans un délai de 24 heures ouvrables.</p>
            </div>
        """, unsafe_allow_html=True)

def page_admin():
    """Page d'administration améliorée"""
    
    # Authentification
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown("""
            <div class="admin-header">
                <h1>🔐 Espace Administration</h1>
                <p>Connectez-vous pour accéder au panneau d'administration</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### 👤 Connexion")
                username = st.text_input("Nom d'utilisateur", placeholder="admin")
                password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("🔓 Se connecter", use_container_width=True):
                    if username == "admin" and password == "admin123":  # À changer en production!
                        st.session_state.admin_logged = True
                        st.success("✅ Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
        return
    
    # Dashboard admin
    st.markdown("""
        <div class="admin-header">
            <h1>⚙️ Tableau de Bord Administration</h1>
            <p>Gérez votre agence de voyage</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Réservations", 
        "📝 Demandes Visa",
        "💬 Messages Contact",
        "➕ Ajouter Destination", 
        "📊 Statistiques",
        "🌍 Gérer Destinations"
    ])
    
    with tab1:
        st.markdown("### 📋 Gestion des Réservations")
        
        reservations = get_reservations()
        
        if reservations:
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                statut_filtre = st.selectbox("Statut", ["Tous", "en_attente", "confirmee", "annulee"])
            with col2:
                date_debut = st.date_input("Date début", datetime.now().date() - timedelta(days=30))
            with col3:
                date_fin = st.date_input("Date fin", datetime.now().date())
            
            # Conversion en DataFrame
            df = pd.DataFrame(reservations)
            
            # Application des filtres
            if statut_filtre != "Tous":
                df = df[df['statut'] == statut_filtre]
            
            st.markdown(f"**{len(df)} réservation(s) trouvée(s)**")
            
            # Affichage des réservations
            for idx, reservation in df.iterrows():
                with st.expander(f"🎫 {reservation['nom']} - {reservation['destination']} ({reservation['statut']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **👤 Client:** {reservation['nom']}  
                        **📧 Email:** {reservation['email']}  
                        **📞 Téléphone:** {reservation['telephone']}  
                        **👥 Personnes:** {reservation['nb_personnes']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **🌍 Destination:** {reservation['destination']}  
                        **📅 Date départ:** {reservation['date_depart']}  
                        **📝 Statut:** {reservation['statut']}  
                        **🕐 Créée le:** {reservation.get('date_creation', 'N/A')[:10]}
                        """)
                    
                    if reservation.get('message'):
                        st.markdown(f"**💬 Message:**  \n{reservation['message']}")
                    
                    # Actions
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✅ Confirmer", key=f"conf_{idx}"):
                            if update_reservation_status(reservation['id'], 'confirmee'):
                                st.success("Réservation confirmée!")
                                st.rerun()
                    with col2:
                        if st.button("⏳ En attente", key=f"wait_{idx}"):
                            if update_reservation_status(reservation['id'], 'en_attente'):
                                st.success("Statut mis à jour!")
                                st.rerun()
                    with col3:
                        if st.button("❌ Annuler", key=f"cancel_{idx}"):
                            if update_reservation_status(reservation['id'], 'annulee'):
                                st.warning("Réservation annulée!")
                                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Télécharger toutes les réservations (CSV)",
                csv,
                f"reservations_hcm_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("📭 Aucune réservation pour le moment")
    
    with tab2:
        st.markdown("### 📝 Gestion des Demandes de Visa")
        
        # Simuler des demandes de visa (à remplacer par Supabase)
        demandes_visa_admin = [
            {
                "id": "VUS001",
                "nom": "Ahmed Benali",
                "email": "ahmed@email.com",
                "telephone": "+213 555 123 456",
                "type_visa": "🇺🇸 USA B1/B2",
                "date_demande": "2024-11-01",
                "statut": "En cours",
                "date_voyage": "2024-12-15"
            },
            {
                "id": "VSC002",
                "nom": "Fatima Mansouri",
                "email": "fatima@email.com",
                "telephone": "+213 666 789 012",
                "type_visa": "🇫🇷 Schengen France",
                "date_demande": "2024-10-28",
                "statut": "RDV programmé",
                "date_voyage": "2024-12-01"
            },
            {
                "id": "VUK003",
                "nom": "Karim Boudiaf",
                "email": "karim@email.com",
                "telephone": "+213 777 345 678",
                "type_visa": "🇬🇧 UK Visitor",
                "date_demande": "2024-10-30",
                "statut": "Documents incomplets",
                "date_voyage": "2024-11-25"
            }
        ]
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            statut_visa_filtre = st.selectbox("Filtrer par statut", 
                ["Tous", "En cours", "RDV programmé", "Documents incomplets", "Approuvé", "Rejeté"])
        with col2:
            type_visa_filtre = st.selectbox("Type de visa", 
                ["Tous", "USA", "UK", "Schengen"])
        with col3:
            tri_date = st.selectbox("Trier par", ["Plus récentes", "Plus anciennes"])
        
        st.markdown(f"**{len(demandes_visa_admin)} demande(s) de visa**")
        
        # Affichage des demandes
        for demande in demandes_visa_admin:
            statut_color = {
                'En cours': '#ffa500',
                'RDV programmé': '#2196f3',
                'Documents incomplets': '#ff6b6b',
                'Approuvé': '#4caf50',
                'Rejeté': '#f44336'
            }.get(demande['statut'], '#666')
            
            with st.expander(f"{demande['type_visa']} - {demande['nom']} (Réf: {demande['id']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **👤 Demandeur:**  
                    {demande['nom']}
                    
                    **📧 Email:**  
                    {demande['email']}
                    
                    **📞 Téléphone:**  
                    {demande['telephone']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📋 Type de visa:**  
                    {demande['type_visa']}
                    
                    **📅 Date demande:**  
                    {demande['date_demande']}
                    
                    **✈️ Date voyage:**  
                    {demande['date_voyage']}
                    """)
                
                with col3:
                    st.markdown(f"""
                    **🎯 Statut:**  
                    <span style="color: {statut_color}; font-weight: bold; font-size: 1.1em;">
                    {demande['statut']}
                    </span>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Actions
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    st.button("📄 Voir dossier", key=f"voir_{demande['id']}", use_container_width=True)
                with col_b:
                    st.button("✅ Approuver", key=f"app_{demande['id']}", use_container_width=True)
                with col_c:
                    st.button("📅 Prog. RDV", key=f"rdv_{demande['id']}", use_container_width=True)
                with col_d:
                    st.button("📧 Contacter", key=f"cont_{demande['id']}", use_container_width=True)
                with col_e:
                    st.button("❌ Rejeter", key=f"rej_{demande['id']}", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Export CSV
        if st.button("⬇️ Exporter les demandes de visa (CSV)", use_container_width=True):
            df_visa = pd.DataFrame(demandes_visa_admin)
            csv = df_visa.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Télécharger",
                csv,
                f"demandes_visa_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    
    with tab3:
        st.markdown("### 💬 Gestion des Messages de Contact")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            filtre_lu = st.selectbox("Statut", ["Tous", "Non lus", "Lus"])
        with col2:
            tri_contact = st.selectbox("Trier par", ["Plus récents", "Plus anciens"])
        
        # Récupération des messages
        if filtre_lu == "Non lus":
            contacts = get_contacts(lu=False)
        elif filtre_lu == "Lus":
            contacts = get_contacts(lu=True)
        else:
            contacts = get_contacts()
        
        if contacts:
            st.markdown(f"**{len(contacts)} message(s)** - {len([c for c in contacts if not c.get('lu', False)])} non lu(s)")
            
            for contact in contacts:
                lu = contact.get('lu', False)
                lu_icon = "✅" if lu else "🔴"
                lu_style = "opacity: 0.7;" if lu else ""
                
                with st.expander(f"{lu_icon} {contact['sujet']} - {contact['nom']}", expanded=not lu):
                    st.markdown(f"""
                        <div style="{lu_style}">
                            <strong>👤 De:</strong> {contact['nom']}<br>
                            <strong>📧 Email:</strong> {contact['email']}<br>
                            <strong>📅 Date:</strong> {contact.get('date_creation', 'N/A')[:16]}<br>
                            <strong>📋 Sujet:</strong> {contact['sujet']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"**💬 Message:**")
                    st.markdown(f"<div style='background: #f8f9fa; padding: 15px; border-radius: 10px; {lu_style}'>{contact['message']}</div>", 
                               unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if not lu:
                            if st.button("✅ Marquer comme lu", key=f"lu_{contact['id']}", use_container_width=True):
                                if mark_contact_as_read(contact['id']):
                                    st.success("Message marqué comme lu!")
                                    st.rerun()
                    with col_b:
                        if st.button(f"📧 Répondre à {contact['email']}", key=f"rep_{contact['id']}", use_container_width=True):
                            st.info(f"Ouvrir votre client email pour répondre à {contact['email']}")
                    with col_c:
                        if st.button("🗑️ Archiver", key=f"arch_{contact['id']}", use_container_width=True):
                            st.warning("Fonction d'archivage à implémenter")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Export
            if st.button("⬇️ Exporter les messages (CSV)", use_container_width=True):
                df_contacts = pd.DataFrame(contacts)
                csv = df_contacts.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Télécharger",
                    csv,
                    f"messages_contact_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        else:
            st.info("📭 Aucun message de contact")
    
    with tab4:
        st.markdown("### ➕ Ajouter une Nouvelle Destination")
        
        with st.form("add_destination_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom de la ville *", placeholder="Ex: Paris")
                pays = st.text_input("Pays *", placeholder="Ex: France")
                prix = st.number_input("Prix (€) *", min_value=0, value=500, step=50)
                duree = st.text_input("Durée", placeholder="Ex: 5 jours", value="5 jours")
            
            with col2:
                categorie = st.selectbox("Catégorie *", ["Europe", "Asie", "Afrique", "Amérique", "Océanie"])
                image_url = st.text_input("URL de l'image", 
                                         placeholder="https://example.com/image.jpg")
                disponible = st.checkbox("Destination disponible", value=True)
            
            description = st.text_area("Description *", 
                                      placeholder="Décrivez la destination, ses attraits...",
                                      height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("✅ Ajouter la destination", use_container_width=True):
                if nom and pays and description and prix > 0:
                    if add_destination(nom, pays, description, prix, categorie, image_url):
                        st.success(f"✅ Destination '{nom}' ajoutée avec succès!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Connectez Supabase pour ajouter des destinations permanentes")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab5:
        st.markdown("### 📊 Statistiques et Analyses")
        
        reservations = get_reservations()
        
        if reservations:
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(reservations)
            en_attente = len([r for r in reservations if r.get('statut') == 'en_attente'])
            confirmees = len([r for r in reservations if r.get('statut') == 'confirmee'])
            annulees = len([r for r in reservations if r.get('statut') == 'annulee'])
            
            with col1:
                st.markdown(f"""
                    <div class="stat-card">
                        <div style="font-size: 2.5em;">📊</div>
                        <h2 style="color: #667eea; margin: 10px 0;">{total}</h2>
                        <p style="margin: 0; color: #666;">Total réservations</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #ffa500;">
                        <div style="font-size: 2.5em;">⏳</div>
                        <h2 style="color: #ffa500; margin: 10px 0;">{en_attente}</h2>
                        <p style="margin: 0; color: #666;">En attente</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #4caf50;">
                        <div style="font-size: 2.5em;">✅</div>
                        <h2 style="color: #4caf50; margin: 10px 0;">{confirmees}</h2>
                        <p style="margin: 0; color: #666;">Confirmées</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="stat-card" style="border-left-color: #f44336;">
                        <div style="font-size: 2.5em;">❌</div>
                        <h2 style="color: #f44336; margin: 10px 0;">{annulees}</h2>
                        <p style="margin: 0; color: #666;">Annulées</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Destinations populaires
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🌟 Destinations les plus demandées")
                df = pd.DataFrame(reservations)
                dest_count = df['destination'].value_counts().head(5)
                
                for dest, count in dest_count.items():
                    st.markdown(f"""
                        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                            <strong>{dest}</strong>
                            <div style="background: #667eea; height: 10px; border-radius: 5px; 
                                        width: {(count/dest_count.max())*100}%; margin-top: 5px;"></div>
                            <small>{count} réservation(s)</small>
                        </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📅 Réservations récentes")
                recent = df.sort_values('date_creation', ascending=False).head(5)
                
                for _, res in recent.iterrows():
                    statut_color = {
                        'en_attente': '#ffa500',
                        'confirmee': '#4caf50',
                        'annulee': '#f44336'
                    }.get(res['statut'], '#666')
                    
                    st.markdown(f"""
                        <div style="background: white; padding: 15px; border-radius: 10px; 
                                    margin: 10px 0; border-left: 4px solid {statut_color};">
                            <strong>{res['nom']}</strong> → {res['destination']}<br>
                            <small style="color: #666;">
                                {res.get('date_creation', 'N/A')[:10]} | 
                                {res['nb_personnes']} pers. | 
                                <span style="color: {statut_color};">{res['statut']}</span>
                            </small>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📭 Pas encore de données statistiques disponibles")
    
    with tab6:
        st.markdown("### 🌍 Gérer les Destinations")
        
        destinations = get_destinations()
        
        if destinations:
            st.markdown(f"**{len(destinations)} destination(s) active(s)**")
            
            # Affichage des destinations
            cols = st.columns(3)
            for idx, dest in enumerate(destinations):
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class="destination-card">
                            <h4>{dest['nom']}, {dest['pays']}</h4>
                            <p style="color: #666; font-size: 0.9em;">{dest['description'][:100]}...</p>
                            <p style="color: #667eea; font-weight: bold;">{dest['prix']}€</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.button("✏️ Modifier", key=f"edit_{idx}", use_container_width=True)
                    with col2:
                        st.button("🗑️ Supprimer", key=f"del_{idx}", use_container_width=True)
        else:
            st.info("📭 Aucune destination enregistrée")
    
    # Bouton de déconnexion
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.admin_logged = False
        st.rerun()

# ====== NAVIGATION ======
def main():
    """Fonction principale avec navigation"""
    
    # Initialisation de la session
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    # Sidebar améliorée
    with st.sidebar:
        # Logo dans la sidebar
        display_logo(size="120px")
        
        st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <h2 style="margin: 10px 0; color: white;">HCM VOYAGES</h2>
                <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9;">L'évasion sur mesure</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        
        # Boutons de navigation
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.page = "accueil"
            st.rerun()
        
        if st.button("🌍 Destinations", use_container_width=True):
            st.session_state.page = "destinations"
            st.rerun()
        
        if st.button("📝 Réservation", use_container_width=True):
            st.session_state.page = "reservation"
            st.rerun()
        
        if st.button("📋 Visas", use_container_width=True):
            st.session_state.page = "visas"
            st.rerun()
        
        if st.button("📞 Contact", use_container_width=True):
            st.session_state.page = "contact"
            st.rerun()
        
        st.markdown("---")
        
        if st.button("⚙️ Administration", use_container_width=True):
            st.session_state.page = "admin"
            st.rerun()
        
        st.markdown("---")
        
        # Informations de contact
        st.markdown("""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;">
                <h4 style="margin-top: 0;">📍 Contact</h4>
                <p style="margin: 5px 0; font-size: 0.9em;">
                    📧 contact@hcmvoyages.dz<br>
                    📞 +213 XXX XXX XXX<br>
                    🏢 Aïn Benian, Alger
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; font-size: 0.8em; opacity: 0.7;">
                © 2024 HCM Voyages<br>
                Tous droits réservés
            </div>
        """, unsafe_allow_html=True)
    
    # Affichage de la page sélectionnée
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "destinations":
        page_destinations()
    elif st.session_state.page == "reservation":
        page_reservation()
    elif st.session_state.page == "visas":
        page_visas()
    elif st.session_state.page == "contact":
        page_contact()
    elif st.session_state.page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
