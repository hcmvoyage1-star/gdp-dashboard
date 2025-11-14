"""
HCM VOYAGES - Application Streamlit
Agence de voyage complète avec gestion des réservations, destinations et visas
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

# ====== CONFIGURATION LOGO ======
# OPTION 1 : URL directe de votre logo (recommandé)
LOGO_URL = "https://votre-site.com/logo.png"  # Remplacez par l'URL de votre logo

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
    
    /* Destination Cards */
    .destination-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
    }
    
    .destination-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        border-color: #667eea;
    }
    
    .destination-card h3 {
        color: #667eea;
        margin-bottom: 15px;
        font-weight: 600;
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
    
    /* Admin section */
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
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

def add_destination(nom, pays, description, prix, categorie, image_url, duree="5 jours"):
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
                "duree": duree,
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

# ====== PAGES DE L'APPLICATION ======

def page_accueil():
    """Page d'accueil avec hero section"""
    
    # Hero Section avec l'image de couverture et logo
    st.markdown("""
        <div class="hero-section">
            <img src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1920&h=600&fit=crop&q=80" 
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
                    <div style="font-size: 3em; margin-bottom: 15px;">{icon}</div>
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
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Galerie de destinations populaires avec images
    st.markdown("### 🌟 Destinations Populaires")
    
    destinations_vedettes = [
        {
            "nom": "Paris",
            "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&h=300&fit=crop&q=80",
            "description": "Tour Eiffel & Champs-Élysées",
            "prix": "799€"
        },
        {
            "nom": "Dubaï",
            "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400&h=300&fit=crop&q=80",
            "description": "Burj Khalifa & Marina",
            "prix": "899€"
        },
        {
            "nom": "Maldives",
            "image": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=400&h=300&fit=crop&q=80",
            "description": "Îles paradisiaques",
            "prix": "1499€"
        },
        {
            "nom": "Tokyo",
            "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop&q=80",
            "description": "Temples & Technologie",
            "prix": "1299€"
        }
    ]
    
    cols = st.columns(4)
    for idx, dest in enumerate(destinations_vedettes):
        with cols[idx]:
            st.image(dest["image"], use_container_width=True)
            st.markdown(f"""
                <div style="text-align: center; padding: 10px;">
                    <h4 style="margin: 10px 0; color: #667eea;">{dest["nom"]}</h4>
                    <p style="margin: 5px 0; color: #666; font-size: 0.9em;">{dest["description"]}</p>
                    <p style="margin: 10px 0; color: #ff6b6b; font-weight: bold; font-size: 1.2em;">{dest["prix"]}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Voir {dest['nom']}", key=f"vedette_{idx}", use_container_width=True):
                st.session_state.page = "destinations"
                st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Section témoignages avec images
    st.markdown("### 💬 Nos Clients Témoignent")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("https://images.unsplash.com/photo-1527631746610-bca00a040d60?w=300&h=300&fit=crop&q=80", 
                 use_container_width=True)
        st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; margin-top: -20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
                <p style="font-style: italic; color: #666;">"Un voyage inoubliable à Paris ! L'équipe HCM a tout organisé parfaitement."</p>
                <p style="text-align: right; color: #667eea; font-weight: bold;">- Amina B.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1542909168-82c3e7fdca44?w=300&h=300&fit=crop&q=80", 
                 use_container_width=True)
        st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; margin-top: -20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
                <p style="font-style: italic; color: #666;">"Service impeccable pour mon visa Schengen. Obtenu en 15 jours !"</p>
                <p style="text-align: right; color: #667eea; font-weight: bold;">- Karim M.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.image("https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300&h=300&fit=crop&q=80", 
                 use_container_width=True)
        st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 15px; margin-top: -20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
                <p style="font-style: italic; color: #666;">"Les Maldives en famille, un rêve devenu réalité grâce à HCM Voyages !"</p>
                <p style="text-align: right; color: #667eea; font-weight: bold;">- Sarah L.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Section partenaires avec logos
    st.markdown("### 🤝 Nos Partenaires de Confiance")
    
    st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 20px; text-align: center;">
            <p style="color: #666; margin-bottom: 20px;">Nous travaillons avec les meilleurs partenaires pour vous garantir un service de qualité</p>
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 20px;">
                <div style="font-size: 2em; opacity: 0.6;">✈️ Airlines</div>
                <div style="font-size: 2em; opacity: 0.6;">🏨 Hotels</div>
                <div style="font-size: 2em; opacity: 0.6;">🚗 Car Rental</div>
                <div style="font-size: 2em; opacity: 0.6;">🛡️ Insurance</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
            {
                "nom": "Paris", 
                "pays": "France", 
                "description": "La ville lumière vous accueille avec ses monuments iconiques", 
                "prix": 799, 
                "categorie": "Europe", 
                "duree": "5 jours",
                "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Istanbul", 
                "pays": "Turquie", 
                "description": "Entre Orient et Occident, découvrez une ville fascinante", 
                "prix": 599, 
                "categorie": "Europe", 
                "duree": "4 jours",
                "image_url": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Maldives", 
                "pays": "Maldives", 
                "description": "Paradis tropical aux eaux cristallines", 
                "prix": 1499, 
                "categorie": "Asie", 
                "duree": "7 jours",
                "image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Tokyo", 
                "pays": "Japon", 
                "description": "Tradition et modernité dans la capitale nippone", 
                "prix": 1299, 
                "categorie": "Asie", 
                "duree": "6 jours",
                "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Dubaï", 
                "pays": "EAU", 
                "description": "Luxe et désert dans la cité futuriste", 
                "prix": 899, 
                "categorie": "Asie", 
                "duree": "5 jours",
                "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Rome", 
                "pays": "Italie", 
                "description": "Histoire antique et dolce vita", 
                "prix": 699, 
                "categorie": "Europe", 
                "duree": "4 jours",
                "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Barcelone", 
                "pays": "Espagne", 
                "description": "Art, plages et gastronomie catalane", 
                "prix": 649, 
                "categorie": "Europe", 
                "duree": "4 jours",
                "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "New York", 
                "pays": "USA", 
                "description": "La ville qui ne dort jamais", 
                "prix": 1099, 
                "categorie": "Amérique", 
                "duree": "6 jours",
                "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Bali", 
                "pays": "Indonésie", 
                "description": "Îles des dieux, temples et rizières", 
                "prix": 1199, 
                "categorie": "Asie", 
                "duree": "8 jours",
                "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Marrakech", 
                "pays": "Maroc", 
                "description": "Cité impériale aux souks colorés", 
                "prix": 399, 
                "categorie": "Afrique", 
                "duree": "5 jours",
                "image_url": "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Le Caire", 
                "pays": "Égypte", 
                "description": "Pyramides et civilisation antique", 
                "prix": 699, 
                "categorie": "Afrique", 
                "duree": "6 jours",
                "image_url": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a?w=400&h=300&fit=crop&q=80"
            },
            {
                "nom": "Londres", 
                "pays": "Royaume-Uni", 
                "description": "Royauté britannique et culture", 
                "prix": 749, 
                "categorie": "Europe", 
                "duree": "5 jours",
                "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=400&h=300&fit=crop&q=80"
            },
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
                image_url = dest.get('image_url', 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=400&h=300&fit=crop&q=80')
                
                # Afficher l'image
                st.image(image_url, use_container_width=True)
                
                st.markdown(f"""
                    <div class="destination-card" style="margin-top: -10px;">
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
    
    # Image hero réservation
    st.image("https://images.unsplash.com/photo-1488085061387-422e29b40080?w=1200&h=250&fit=crop&q=80", 
             use_container_width=True)
    
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
                    st.markdown(f"""
                        <div class="info-box">
                            <h4>📧 Confirmation envoyée</h4>
                            <p>Un email de confirmation vous a été envoyé à <strong>{email}</strong></p>
                            <p>Notre équipe vous contactera dans les 24 heures pour finaliser votre réservation.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning("⚠️ Demande enregistrée localement. Connectez Supabase pour la sauvegarde permanente.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

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
            <div class="contact-card">
                <h3>🌐 Suivez-nous</h3>
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
                    if add_contact(nom, email, sujet, message):
                        st.success("✅ Message envoyé avec succès! Nous vous répondrons dans les plus brefs délais.")
                        st.balloons()
                    else:
                        st.warning("⚠️ Erreur lors de l'envoi. Veuillez réessayer.")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="info-box">
                <h4>⚡ Réponse rapide</h4>
                <p>Nous nous engageons à répondre à tous les messages dans un délai de 24 heures ouvrables.</p>
            </div>
        """, unsafe_allow_html=True)

def page_visas():
    """Page simplifiée des visas"""
    st.markdown("# 📋 Services Visa")
    st.markdown("Assistance complète pour vos démarches de visa")
    
    # Image hero
    st.image("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1200&h=300&fit=crop&q=80", 
             use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Informations
    st.markdown("""
        <div class="info-box">
            <h3 style="color: #667eea; margin-bottom: 15px;">🎯 Nos Services Visa</h3>
            <p>HCM Voyages vous accompagne dans l'obtention de vos visas pour :</p>
            <ul>
                <li><strong>🇺🇸 USA (Visa B1/B2, ESTA)</strong> - Tourisme & Affaires</li>
                <li><strong>🇬🇧 UK (Visa Standard Visitor)</strong> - Tourisme, Famille, Affaires</li>
                <li><strong>🇪🇺 Schengen (Type C)</strong> - 26 pays européens</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cartes de services
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="service-card">
                <h3 style="color: #667eea;">🇺🇸 Visa USA</h3>
                <p><strong>Types:</strong> B1/B2, ESTA</p>
                <p><strong>Délai:</strong> 3-6 semaines</p>
                <p><strong>Tarif:</strong> 160 USD + 15 000 DZD</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Demander un visa USA", key="visa_usa", use_container_width=True):
            st.info("Contactez-nous pour votre demande de visa USA")
    
    with col2:
        st.markdown("""
            <div class="service-card">
                <h3 style="color: #667eea;">🇬🇧 Visa UK</h3>
                <p><strong>Types:</strong> Standard, Family, Business</p>
                <p><strong>Délai:</strong> 3 semaines</p>
                <p><strong>Tarif:</strong> £100 + 12 000 DZD</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Demander un visa UK", key="visa_uk", use_container_width=True):
            st.info("Contactez-nous pour votre demande de visa UK")
    
    with col3:
        st.markdown("""
            <div class="service-card">
                <h3 style="color: #667eea;">🇪🇺 Visa Schengen</h3>
                <p><strong>Pays:</strong> 26 pays européens</p>
                <p><strong>Délai:</strong> 15-45 jours</p>
                <p><strong>Tarif:</strong> 80€ + 10 000 DZD</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Demander un visa Schengen", key="visa_schengen", use_container_width=True):
            st.info("Contactez-nous pour votre demande de visa Schengen")

def page_admin():
    """Page d'administration"""
    
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
                    if username == "admin" and password == "admin123":
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
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Réservations", 
        "💬 Messages Contact",
        "➕ Ajouter Destination", 
        "📊 Statistiques"
    ])
    
    with tab1:
        st.markdown("### 📋 Gestion des Réservations")
        
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Télécharger en CSV",
                csv,
                f"reservations_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("📭 Aucune réservation pour le moment")
    
    with tab2:
        st.markdown("### 💬 Messages de Contact")
        
        contacts = get_contacts()
        
        if contacts:
            for contact in contacts:
                lu = contact.get('lu', False)
                lu_icon = "✅" if lu else "🔴"
                
                with st.expander(f"{lu_icon} {contact.get('sujet', 'Sans sujet')} - {contact['nom']}"):
                    st.markdown(f"""
                    **👤 De:** {contact['nom']}  
                    **📧 Email:** {contact['email']}  
                    **📅 Date:** {contact.get('date_creation', 'N/A')[:16]}
                    
                    **💬 Message:**  
                    {contact['message']}
                    """)
                    
                    if not lu and st.button("✅ Marquer comme lu", key=f"lu_{contact['id']}"):
                        if mark_contact_as_read(contact['id']):
                            st.success("Message marqué comme lu!")
                            st.rerun()
        else:
            st.info("📭 Aucun message de contact")
    
    with tab3:
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
            
            description = st.text_area("Description *", 
                                      placeholder="Décrivez la destination...",
                                      height=150)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("✅ Ajouter la destination", use_container_width=True):
                if nom and pays and description and prix > 0:
                    if add_destination(nom, pays, description, prix, categorie, image_url, duree):
                        st.success(f"✅ Destination '{nom}' ajoutée avec succès!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Connectez Supabase pour ajouter des destinations")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab4:
        st.markdown("### 📊 Statistiques")
        
        reservations = get_reservations()
        contacts = get_contacts()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 2.5em;">📊</div>
                    <h2 style="color: #667eea; margin: 10px 0;">{len(reservations)}</h2>
                    <p style="margin: 0; color: #666;">Réservations</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            en_attente = len([r for r in reservations if r.get('statut') == 'en_attente'])
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 2.5em;">⏳</div>
                    <h2 style="color: #ffa500; margin: 10px 0;">{en_attente}</h2>
                    <p style="margin: 0; color: #666;">En attente</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            confirmees = len([r for r in reservations if r.get('statut') == 'confirmee'])
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 2.5em;">✅</div>
                    <h2 style="color: #4caf50; margin: 10px 0;">{confirmees}</h2>
                    <p style="margin: 0; color: #666;">Confirmées</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            non_lus = len([c for c in contacts if not c.get('lu', False)])
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 2.5em;">💬</div>
                    <h2 style="color: #667eea; margin: 10px 0;">{non_lus}</h2>
                    <p style="margin: 0; color: #666;">Messages non lus</p>
                </div>
            """, unsafe_allow_html=True)
    
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
