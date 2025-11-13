import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import requests

# Configuration de la page
st.set_page_config(
    page_title="HCM Voyages",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====== CONFIGURATION SUPABASE ======
SUPABASE_URL = "https://oilamfxxqjopuopgskfc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9pbGFtZnh4cWpvcHVvcGdza2ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNDY4NTYsImV4cCI6MjA3ODYyMjg1Nn0.PzIJjkIAKQ8dzNcTA4t6PSaCoAWG6kWZQxEibG5gUwE"

# Initialisation du client Supabase
@st.cache_resource
def init_supabase():
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase_client
    except Exception as e:
        st.error(f"Erreur de connexion à Supabase: {e}")
        return None

supabase = init_supabase()

# ====== CSS PERSONNALISÉ ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Cards avec glassmorphism */
    .destination-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(255, 255, 255, 0.18);
        position: relative;
        overflow: hidden;
    }
    
    .destination-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .destination-card:hover::before {
        left: 100%;
    }
    
    .destination-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.3);
    }
    
    /* Price tag avec animation */
    .price-tag {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        font-size: 26px;
        font-weight: 700;
        padding: 10px 20px;
        border-radius: 15px;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* En-têtes stylisés */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h2, h3 {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Boutons améliorés */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px;
        padding: 12px 35px;
        border: none;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
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
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar stylisée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        width: 100%;
        margin: 5px 0;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateX(5px);
    }
    
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Inputs améliorés */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        transition: all 0.3s;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus, .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Métriques améliorées */
    [data-testid="stMetricValue"] {
        font-size: 2em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Bouton WhatsApp flottant amélioré */
    .whatsapp-float {
        position: fixed;
        width: 65px;
        height: 65px;
        bottom: 40px;
        right: 40px;
        background: linear-gradient(135deg, #25d366 0%, #128C7E 100%);
        color: #FFF;
        border-radius: 50%;
        text-align: center;
        font-size: 32px;
        box-shadow: 0 6px 25px rgba(37, 211, 102, 0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    
    .whatsapp-float:hover {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 10px 40px rgba(37, 211, 102, 0.6);
    }
    
    .whatsapp-float::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 2px solid #25d366;
        animation: ripple 1.5s infinite;
    }
    
    @keyframes ripple {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        100% {
            transform: scale(1.5);
            opacity: 0;
        }
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 30px;
        margin-bottom: 40px;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '✈️';
        position: absolute;
        font-size: 200px;
        opacity: 0.1;
        top: -50px;
        right: -50px;
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .hero-section h1 {
        color: white !important;
        -webkit-text-fill-color: white;
        font-size: 3.5em;
        margin: 0 0 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-section p {
        color: white;
        font-size: 1.5em;
        margin: 0;
    }
    
    /* Tabs personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px;
        padding: 10px 20px;
        background: rgba(102, 126, 234, 0.1);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Dataframe stylisé */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
    }
    </style>
    
    <!-- Bouton WhatsApp flottant -->
    <a href="https://wa.me/213783802712" class="whatsapp-float" target="_blank" title="Contactez-nous sur WhatsApp">
        <span>💬</span>
    </a>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======

def get_destinations():
    """Récupère toutes les destinations depuis Supabase"""
    if supabase:
        try:
            response = supabase.table('destinations').select("*").execute()
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
                "date_creation": datetime.now().isoformat(),
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
                "image_url": image_url
            }
            response = supabase.table('destinations').insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

# ====== PAGES DE L'APPLICATION ======

def page_accueil():
    """Page d'accueil"""
    # Hero Section amélioré
    try:
        st.image("logo_hcm.png", use_container_width=True)
    except:
        st.markdown("""
            <div class='hero-section'>
                <h1>✈️ HCM VOYAGES</h1>
                <p>L'évasion sur mesure, explorez, rêvez, partez</p>
                <div style='margin-top: 30px;'>
                    <span style='font-size: 1.2em; color: rgba(255,255,255,0.9);'>
                        🌍 Votre passeport vers l'aventure commence ici
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Statistiques avec animation
    st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='destination-card' style='text-align: center;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>🌍</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #667eea;'>50+</div>
                <div style='color: #666; font-weight: 600;'>Destinations</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='destination-card' style='text-align: center;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>😊</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #667eea;'>1000+</div>
                <div style='color: #666; font-weight: 600;'>Clients Satisfaits</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='destination-card' style='text-align: center;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>📅</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #667eea;'>10+</div>
                <div style='color: #666; font-weight: 600;'>Années d'Expérience</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class='destination-card' style='text-align: center;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>🤝</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #667eea;'>25+</div>
                <div style='color: #666; font-weight: 600;'>Partenaires</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Nos services
    st.markdown("<h1 style='margin-top: 50px;'>🎯 Nos Services Premium</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>🎫</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Billets d'Avion</h3>
                <p style='text-align: center; color: #666;'>Les meilleurs tarifs pour toutes destinations mondiales</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>🏨</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Réservation Hôtels</h3>
                <p style='text-align: center; color: #666;'>Hébergements de qualité soigneusement sélectionnés</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>🎒</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Circuits Organisés</h3>
                <p style='text-align: center; color: #666;'>Voyages tout compris clés en main personnalisés</p>
            </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>🚗</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Location de Voitures</h3>
                <p style='text-align: center; color: #666;'>Mobilité à destination garantie et flexible</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>📋</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Assistance Visa</h3>
                <p style='text-align: center; color: #666;'>Accompagnement complet pour vos démarches</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col6:
        st.markdown("""
            <div class='destination-card'>
                <div style='text-align: center; font-size: 3.5em; margin-bottom: 15px;'>💼</div>
                <h3 style='text-align: center; margin-bottom: 15px;'>Voyages Affaires</h3>
                <p style='text-align: center; color: #666;'>Solutions professionnelles sur mesure efficaces</p>
            </div>
        """, unsafe_allow_html=True)

def page_destinations():
    """Page des destinations"""
    st.markdown("<h1>🌍 Nos Destinations de Rêve</h1>", unsafe_allow_html=True)
    
    # Filtres améliorés
    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher une destination", "", placeholder="Tapez une ville, un pays...")
    with col2:
        categorie = st.selectbox("🗺️ Catégorie", ["Toutes", "Europe", "Asie", "Afrique", "Amérique", "Océanie"])
    
    # Récupération des destinations
    destinations = get_destinations()
    
    if not destinations:
        st.warning("⚠️ Aucune destination trouvée. Vérifiez votre connexion Supabase.")
        return
    
    # Filtrage
    if search:
        destinations = [d for d in destinations if search.lower() in d['nom'].lower() or search.lower() in d['pays'].lower()]
    if categorie != "Toutes":
        destinations = [d for d in destinations if d.get('categorie') == categorie]
    
    st.markdown(f"<p style='text-align: center; color: #667eea; font-size: 1.2em; margin: 20px 0;'>✨ {len(destinations)} destinations trouvées</p>", unsafe_allow_html=True)
    
    # Affichage en grille
    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            # Afficher l'image si disponible
            if dest.get('image_url'):
                try:
                    st.image(dest['image_url'], use_container_width=True)
                except:
                    pass
            
            st.markdown(f"""
                <div class='destination-card'>
                    <h3 style='margin-bottom: 15px;'>📍 {dest['nom']}, {dest['pays']}</h3>
                    <p style='color: #666; margin-bottom: 20px;'>{dest['description']}</p>
                    <div style='text-align: center;'>
                        <span class='price-tag'>À partir de {dest['prix']}€</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    """Page de réservation"""
    st.markdown("<h1>📝 Réservez Votre Voyage de Rêve</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='destination-card' style='text-align: center; margin: 30px 0;'>
            <p style='font-size: 1.2em; color: #667eea;'>
                ✨ Remplissez le formulaire ci-dessous et notre équipe vous contactera dans les plus brefs délais
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("👤 Nom complet *", placeholder="Ex: Ahmed Benali")
            email = st.text_input("📧 Email *", placeholder="exemple@email.com")
            telephone = st.text_input("📱 Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("🌍 Destination *", 
                                       value=st.session_state.get('destination_selectionnee', ''),
                                       placeholder="Ex: Paris, Istanbul...")
            date_depart = st.date_input("📅 Date de départ *")
            nb_personnes = st.number_input("👥 Nombre de personnes", min_value=1, max_value=20, value=1)
        
        message = st.text_area("💬 Message / Demandes spéciales", 
                              placeholder="Vos préférences, questions ou demandes particulières...",
                              height=100)
        
        st.markdown("<div style='text-align: center; margin-top: 30px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✈️ Envoyer ma demande de réservation", use_container_width=True)
        
        if submitted:
            if nom and email and telephone and destination:
                if add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
                    st.success("✅ Votre demande a été envoyée avec succès! Nous vous contacterons rapidement.")
                    st.balloons()
                    st.markdown("""
                        <div class='destination-card' style='text-align: center; margin-top: 20px;'>
                            <h3>🎉 Merci pour votre confiance !</h3>
                            <p>Notre équipe traite votre demande. Pour toute urgence :</p>
                            <a href='https://wa.me/213783802712' target='_blank' 
                               style='display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #25d366 0%, #128C7E 100%); 
                               color: white; text-decoration: none; border-radius: 25px; margin: 10px; font-weight: 600;'>
                                💬 Contactez-nous sur WhatsApp
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Erreur lors de l'envoi de la réservation.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

def page_contact():
    """Page de contact"""
    st.markdown("<h1>📞 Contactez-Nous</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='destination-card'>
                <h3>📍 Notre Agence</h3>
                <p><strong>Adresse:</strong><br>EL MOHAMMADIA, Alger<br>Algérie</p>
                <p><strong>📞 Téléphone:</strong><br>
                <a href="tel:+213783802712" style="color: #667eea; text-decoration: none; font-weight: 600;">+213 7 83 80 27 12</a></p>
                <p><strong>📧 Email:</strong><br>
                <a href="mailto:hcmvoyage1@gmail.com" style="color: #667eea; text-decoration: none; font-weight: 600;">hcmvoyage1@gmail.com</a></p>
                <p><strong>🕐 Horaires:</strong><br>Dim - Jeu: 9h - 18h<br>Sam: 9h - 13h</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='destination-card'>
                <h3 style='text-align: center; margin-bottom: 20px;'>🌐 Contactez-nous directement</h3>
                <div style='text-align: center;'>
                    <a href="https://wa.me/213783802712" target="_blank" 
                       style="display: inline-block; padding: 12px 25px; background: linear-gradient(135deg, #25d366 0%, #128C7E 100%); 
                       color: white; text-decoration: none; border-radius: 25px; margin: 8px; font-weight: 600; transition: all 0.3s;">
                        💬 WhatsApp
                    </a>
                </div>
                <div style='text-align: center;'>
                    <a href="mailto:hcmvoyage1@gmail.com" 
                       style="display: inline-block; padding: 12px 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; text-decoration: none; border-radius: 25px; margin: 8px; font-weight: 600; transition: all 0.3s;">
                        📧 Email
                    </a>
                </div>
                <div style='text-align: center;'>
                    <a href="tel:+213783802712" 
                       style="display: inline-block; padding: 12px 25px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                       color: white; text-decoration: none; border-radius: 25px; margin: 8px; font-weight: 600; transition: all 0.3s;">
                        📞 Appeler
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3 style='color: #667eea;'>💬 Envoyez-nous un message</h3>", unsafe_allow_html=True)
        with st.form("contact_form"):
            nom = st.text_input("👤 Nom *")
            email = st.text_input("📧 Email *")
            telephone = st.text_input("📱 Téléphone")
            sujet = st.text_input("📋 Sujet")
            message = st.text_area("💬 Message *", height=200, placeholder="Écrivez votre message ici...")
            
            if st.form_submit_button("📨 Envoyer", use_container_width=True):
                if nom and email and message:
                    # Sauvegarder dans Supabase
                    if supabase:
                        try:
                            data = {
                                "nom": nom,
                                "email": email,
                                "telephone": telephone,
                                "sujet": sujet or "Contact général",
                                "message": message,
                                "date_creation": datetime.now().isoformat(),
                                "lu": False
                            }
                            response = supabase.table('contacts').insert(data).execute()
                            st.success("✅ Message envoyé avec succès! Nous vous répondrons rapidement.")
                            
                            # Suggestion d'utiliser WhatsApp pour une réponse rapide
                            st.info("💡 Pour une réponse immédiate, contactez-nous sur WhatsApp!")
                            whatsapp_link = f"https://wa.me/213783802712?text=Bonjour, je suis {nom}. {message[:100]}"
                            st.markdown(f"<div style='text-align: center;'><a href='{whatsapp_link}' target='_blank' style='display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #25d366 0%, #128C7E 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 600;'>💬 Ouvrir WhatsApp</a></div>", unsafe_allow_html=True)
                        except:
                            st.warning("⚠️ Impossible d'envoyer le message. Veuillez nous contacter directement.")
                    else:
                        st.warning("⚠️ Veuillez nous contacter directement par téléphone ou WhatsApp.")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

def page_admin():
    """Page d'administration"""
    st.markdown("<h1>⚙️ Administration HCM Voyages</h1>", unsafe_allow_html=True)
    
    # Authentification simple
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown("""
            <div class='destination-card' style='max-width: 500px; margin: 50px auto;'>
                <h3 style='text-align: center; margin-bottom: 30px;'>🔐 Connexion Administrateur</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Utilisateur", placeholder="admin")
            password = st.text_input("🔑 Mot de passe", type="password", placeholder="••••••••")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("🚀 Se connecter", use_container_width=True):
                    if username == "admin" and password == "admin123":  # À changer!
                        st.session_state.admin_logged = True
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
        return
    
    # Si connecté
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Réservations", "📨 Messages", "➕ Ajouter Destination", "📊 Statistiques"])
    
    with tab1:
        st.markdown("<h2 style='color: #667eea;'>Liste des réservations</h2>", unsafe_allow_html=True)
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            
            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                statut_filtre = st.selectbox("Filtrer par statut", ["Tous", "en_attente", "confirmee", "annulee"])
            with col2:
                search_reservation = st.text_input("🔍 Rechercher", placeholder="Nom, email, destination...")
            
            # Appliquer les filtres
            df_filtered = df.copy()
            if statut_filtre != "Tous":
                df_filtered = df_filtered[df_filtered['statut'] == statut_filtre]
            if search_reservation:
                df_filtered = df_filtered[
                    df_filtered.apply(lambda row: search_reservation.lower() in str(row).lower(), axis=1)
                ]
            
            st.dataframe(df_filtered, use_container_width=True, height=400)
            
            # Export CSV
            col1, col2 = st.columns(2)
            with col1:
                csv = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Télécharger en CSV",
                    csv,
                    f"reservations_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            with col2:
                st.metric("Total réservations affichées", len(df_filtered))
        else:
            st.info("📭 Aucune réservation pour le moment")
    
    with tab2:
        st.markdown("<h2 style='color: #667eea;'>Messages de contact</h2>", unsafe_allow_html=True)
        
        if supabase:
            try:
                response = supabase.table('contacts').select("*").order('date_creation', desc=True).execute()
                contacts = response.data
                
                if contacts:
                    df_contacts = pd.DataFrame(contacts)
                    st.dataframe(df_contacts, use_container_width=True, height=400)
                    
                    csv_contacts = df_contacts.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "⬇️ Télécharger les messages",
                        csv_contacts,
                        f"messages_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                else:
                    st.info("📭 Aucun message pour le moment")
            except:
                st.warning("⚠️ Table 'contacts' non disponible")
    
    with tab3:
        st.markdown("<h2 style='color: #667eea;'>Ajouter une nouvelle destination</h2>", unsafe_allow_html=True)
        
        with st.form("add_destination_form"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("🏙️ Nom de la ville *")
                pays = st.text_input("🌍 Pays *")
                prix = st.number_input("💰 Prix (€) *", min_value=0, step=50)
            with col2:
                categorie = st.selectbox("📂 Catégorie *", ["Europe", "Asie", "Afrique", "Amérique", "Océanie"])
                image_url = st.text_input("🖼️ URL de l'image", placeholder="https://...")
            
            description = st.text_area("📝 Description *", height=150, 
                                      placeholder="Décrivez la destination (attractions, climat, culture...)")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.form_submit_button("✅ Ajouter la destination", use_container_width=True):
                    if nom and pays and description and prix >= 0:
                        if add_destination(nom, pays, description, prix, categorie, image_url):
                            st.success("✅ Destination ajoutée avec succès!")
                            st.balloons()
                        else:
                            st.error("❌ Erreur lors de l'ajout")
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires")
    
    with tab4:
        st.markdown("<h2 style='color: #667eea;'>📊 Tableau de bord</h2>", unsafe_allow_html=True)
        reservations = get_reservations()
        destinations = get_destinations()
        
        if reservations:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                    <div class='destination-card' style='text-align: center;'>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>📋</div>
                        <div style='font-size: 2em; font-weight: 700; color: #667eea;'>{}</div>
                        <div style='color: #666; font-weight: 600;'>Total Réservations</div>
                    </div>
                """.format(len(reservations)), unsafe_allow_html=True)
            
            with col2:
                en_attente = len([r for r in reservations if r.get('statut') == 'en_attente'])
                st.markdown("""
                    <div class='destination-card' style='text-align: center;'>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>⏳</div>
                        <div style='font-size: 2em; font-weight: 700; color: #ff9800;'>{}</div>
                        <div style='color: #666; font-weight: 600;'>En Attente</div>
                    </div>
                """.format(en_attente), unsafe_allow_html=True)
            
            with col3:
                confirmees = len([r for r in reservations if r.get('statut') == 'confirmee'])
                st.markdown("""
                    <div class='destination-card' style='text-align: center;'>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>✅</div>
                        <div style='font-size: 2em; font-weight: 700; color: #4caf50;'>{}</div>
                        <div style='color: #666; font-weight: 600;'>Confirmées</div>
                    </div>
                """.format(confirmees), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                    <div class='destination-card' style='text-align: center;'>
                        <div style='font-size: 2.5em; margin-bottom: 10px;'>🌍</div>
                        <div style='font-size: 2em; font-weight: 700; color: #667eea;'>{}</div>
                        <div style='color: #666; font-weight: 600;'>Destinations Actives</div>
                    </div>
                """.format(len(destinations)), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Graphiques
            st.subheader("📈 Réservations par destination")
            if reservations:
                dest_counts = {}
                for r in reservations:
                    dest = r.get('destination', 'Non spécifié')
                    dest_counts[dest] = dest_counts.get(dest, 0) + 1
                
                if dest_counts:
                    df_chart = pd.DataFrame(list(dest_counts.items()), columns=['Destination', 'Nombre'])
                    st.bar_chart(df_chart.set_index('Destination'))
            
            st.markdown("---")
            st.subheader("📅 Réservations récentes")
            recent_reservations = reservations[:5]
            for r in recent_reservations:
                st.markdown(f"""
                    <div class='destination-card'>
                        <strong>{r.get('nom', 'N/A')}</strong> - {r.get('destination', 'N/A')}<br>
                        📧 {r.get('email', 'N/A')} | 📱 {r.get('telephone', 'N/A')}<br>
                        📅 Départ: {r.get('date_depart', 'N/A')} | 👥 {r.get('nb_personnes', 1)} personne(s)<br>
                        <span style='color: {'#ff9800' if r.get('statut') == 'en_attente' else '#4caf50'}; font-weight: 600;'>
                            Statut: {r.get('statut', 'N/A')}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 Pas encore de données statistiques")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Se déconnecter", use_container_width=True):
            st.session_state.admin_logged = False
            st.rerun()

# ====== NAVIGATION ======
def main():
    # Sidebar
    with st.sidebar:
        # Logo avec animation
        try:
            st.image("logo_hcm_circle.png", use_container_width=True)
        except:
            st.markdown("""
                <div style='text-align: center; padding: 20px;'>
                    <div style='width: 120px; height: 120px; margin: 0 auto; border-radius: 50%; 
                         background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
                         display: flex; align-items: center; justify-content: center;
                         box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                         backdrop-filter: blur(10px);
                         border: 2px solid rgba(255,255,255,0.3);'>
                        <h1 style='color: white; font-size: 3em; margin: 0;'>H</h1>
                    </div>
                    <h3 style='color: white; margin-top: 15px; font-weight: 600;'>HCM VOYAGES</h3>
                    <p style='color: rgba(255,255,255,0.8); font-size: 0.9em;'>L'évasion sur mesure</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='color: white; text-align: center; margin: 30px 0 20px 0;'>Navigation</h2>", unsafe_allow_html=True)
        
        if 'page' not in st.session_state:
            st.session_state.page = "accueil"
        
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state.page = "accueil"
        if st.button("🌍 Destinations", use_container_width=True):
            st.session_state.page = "destinations"
        if st.button("📝 Réservation", use_container_width=True):
            st.session_state.page = "reservation"
        if st.button("📞 Contact", use_container_width=True):
            st.session_state.page = "contact"
        
        st.markdown("---")
        if st.button("⚙️ Admin", use_container_width=True):
            st.session_state.page = "admin"
        
        st.markdown("---")
        st.markdown("""
            <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; 
                 backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);'>
                <h4 style='color: white; margin-bottom: 15px; text-align: center;'>📞 Contactez-nous</h4>
                <p style='color: rgba(255,255,255,0.9); margin: 8px 0; font-size: 0.9em;'>
                    <strong>📍</strong> EL MOHAMMADIA, Alger
                </p>
                <p style='color: rgba(255,255,255,0.9); margin: 8px 0; font-size: 0.9em;'>
                    <strong>📱</strong> +213 7 83 80 27 12
                </p>
                <p style='color: rgba(255,255,255,0.9); margin: 8px 0; font-size: 0.9em;'>
                    <strong>📧</strong> hcmvoyage1@gmail.com
                </p>
                <div style='text-align: center; margin-top: 15px;'>
                    <a href='https://wa.me/213783802712' target='_blank' 
                       style='display: inline-block; padding: 10px 20px; background: rgba(37, 211, 102, 0.9); 
                       color: white; text-decoration: none; border-radius: 20px; font-weight: 600; font-size: 0.9em;'>
                        💬 WhatsApp
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Affichage de la page sélectionnée
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "destinations":
        page_destinations()
    elif st.session_state.page == "reservation":
        page_reservation()
    elif st.session_state.page == "contact":
        page_contact()
    elif st.session_state.page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
