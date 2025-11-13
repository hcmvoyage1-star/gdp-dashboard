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

# Test de connexion
if supabase:
    try:
        # Test simple pour vérifier la connexion
        test = supabase.table('destinations').select("id").limit(1).execute()
        st.success("✅ Connexion à Supabase réussie!")
    except Exception as e:
        st.error(f"⚠️ Problème de connexion: {e}")

# ====== CSS PERSONNALISÉ ======
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .destination-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 10px 0;
        transition: transform 0.3s;
    }
    .destination-card:hover {
        transform: translateY(-5px);
    }
    .price-tag {
        color: #ff6b6b;
        font-size: 24px;
        font-weight: bold;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    h1, h2, h3 {
        color: #667eea;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 10px 30px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ====== AFFICHAGE DU LOGO ======
def display_logo():
    st.markdown("""
        <div class="logo-container">
            <img src="data:image/png;base64,{}" width="300">
        </div>
    """.format(get_logo_base64()), unsafe_allow_html=True)

def get_logo_base64():
    # Vous devrez encoder votre logo en base64
    # Pour l'instant, un placeholder
    return ""

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
    # Logo
    st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-bottom: 30px;'>
            <h1 style='color: white; font-size: 3em; margin: 0;'>✈️ HCM VOYAGES</h1>
            <p style='color: white; font-size: 1.5em; margin: 10px 0;'>L'évasion sur mesure, explorez, rêvez, partez</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Destinations", "50+", "🌍")
    with col2:
        st.metric("Clients Satisfaits", "1000+", "😊")
    with col3:
        st.metric("Années d'Expérience", "10+", "📅")
    with col4:
        st.metric("Partenaires", "25+", "🤝")
    
    st.markdown("---")
    
    # Nos services
    st.header("🎯 Nos Services")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='destination-card'>
                <h3>🎫 Billets d'Avion</h3>
                <p>Les meilleurs tarifs pour toutes destinations</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class='destination-card'>
                <h3>🏨 Réservation Hôtels</h3>
                <p>Hébergements de qualité sélectionnés</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class='destination-card'>
                <h3>🎒 Circuits Organisés</h3>
                <p>Voyages tout compris clés en main</p>
            </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
            <div class='destination-card'>
                <h3>🚗 Location de Voitures</h3>
                <p>Mobilité à destination garantie</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
            <div class='destination-card'>
                <h3>📋 Assistance Visa</h3>
                <p>Aide complète pour vos démarches</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col6:
        st.markdown("""
            <div class='destination-card'>
                <h3>💼 Voyages Affaires</h3>
                <p>Solutions professionnelles sur mesure</p>
            </div>
        """, unsafe_allow_html=True)

def page_destinations():
    """Page des destinations"""
    st.title("🌍 Nos Destinations")
    
    # Filtres
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher une destination", "")
    with col2:
        categorie = st.selectbox("Catégorie", ["Toutes", "Europe", "Asie", "Afrique", "Amérique", "Océanie"])
    
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
    
    # Affichage en grille
    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class='destination-card'>
                    <h3>📍 {dest['nom']}, {dest['pays']}</h3>
                    <p>{dest['description']}</p>
                    <p class='price-tag'>À partir de {dest['prix']}€</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Réserver {dest['nom']}", key=f"btn_{idx}"):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    """Page de réservation"""
    st.title("📝 Réserver Votre Voyage")
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Ex: Ahmed Benali")
            email = st.text_input("Email *", placeholder="exemple@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("Destination *", 
                                       value=st.session_state.get('destination_selectionnee', ''),
                                       placeholder="Ex: Paris, Istanbul...")
            date_depart = st.date_input("Date de départ *")
            nb_personnes = st.number_input("Nombre de personnes", min_value=1, max_value=20, value=1)
        
        message = st.text_area("Message / Demandes spéciales", 
                              placeholder="Vos préférences, questions...")
        
        submitted = st.form_submit_button("✈️ Envoyer la demande de réservation")
        
        if submitted:
            if nom and email and telephone and destination:
                if add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
                    st.success("✅ Votre demande a été envoyée avec succès! Nous vous contacterons rapidement.")
                    st.balloons()
                else:
                    st.error("❌ Erreur lors de l'envoi de la réservation.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

def page_contact():
    """Page de contact"""
    st.title("📞 Contactez-Nous")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='destination-card'>
                <h3>📍 Notre Agence</h3>
                <p><strong>Adresse:</strong><br>Aïn Benian, Alger<br>Algérie</p>
                <p><strong>📞 Téléphone:</strong><br>+213 XXX XXX XXX</p>
                <p><strong>📧 Email:</strong><br>contact@hcmvoyages.dz</p>
                <p><strong>🕐 Horaires:</strong><br>Dim - Jeu: 9h - 18h<br>Sam: 9h - 13h</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='destination-card'>
                <h3>🌐 Réseaux Sociaux</h3>
                <p>📘 Facebook: @HCMVoyages</p>
                <p>📷 Instagram: @hcm_voyages</p>
                <p>💬 WhatsApp: +213 XXX XXX XXX</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("💬 Envoyez-nous un message")
        with st.form("contact_form"):
            nom = st.text_input("Nom *")
            email = st.text_input("Email *")
            sujet = st.text_input("Sujet")
            message = st.text_area("Message *", height=200)
            
            if st.form_submit_button("📨 Envoyer"):
                if nom and email and message:
                    st.success("✅ Message envoyé avec succès!")
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")

def page_admin():
    """Page d'administration"""
    st.title("⚙️ Administration HCM Voyages")
    
    # Authentification simple
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        with st.form("login_form"):
            st.subheader("🔐 Connexion Admin")
            username = st.text_input("Utilisateur")
            password = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Se connecter"):
                if username == "admin" and password == "admin123":  # À changer!
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        return
    
    # Si connecté
    tab1, tab2, tab3 = st.tabs(["📋 Réservations", "➕ Ajouter Destination", "📊 Statistiques"])
    
    with tab1:
        st.subheader("Liste des réservations")
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            st.dataframe(df, use_container_width=True)
            
            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Télécharger en CSV",
                csv,
                "reservations.csv",
                "text/csv"
            )
        else:
            st.info("Aucune réservation pour le moment")
    
    with tab2:
        st.subheader("Ajouter une nouvelle destination")
        with st.form("add_destination_form"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom de la ville")
                pays = st.text_input("Pays")
                prix = st.number_input("Prix (€)", min_value=0)
            with col2:
                categorie = st.selectbox("Catégorie", ["Europe", "Asie", "Afrique", "Amérique", "Océanie"])
                image_url = st.text_input("URL de l'image")
            
            description = st.text_area("Description")
            
            if st.form_submit_button("✅ Ajouter la destination"):
                if add_destination(nom, pays, description, prix, categorie, image_url):
                    st.success("✅ Destination ajoutée!")
                else:
                    st.error("❌ Erreur lors de l'ajout")
    
    with tab3:
        st.subheader("📊 Statistiques")
        reservations = get_reservations()
        
        if reservations:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total réservations", len(reservations))
            with col2:
                en_attente = len([r for r in reservations if r.get('statut') == 'en_attente'])
                st.metric("En attente", en_attente)
            with col3:
                confirmees = len([r for r in reservations if r.get('statut') == 'confirmee'])
                st.metric("Confirmées", confirmees)
        else:
            st.info("Pas encore de données statistiques")
    
    if st.button("🚪 Se déconnecter"):
        st.session_state.admin_logged = False
        st.rerun()

# ====== NAVIGATION ======
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x200/667eea/ffffff?text=HCM", width=200)
        st.title("Navigation")
        
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
            **HCM Voyages**  
            📍 EL MOHAMMADIA , Alger  
            📞 +2137 83 80 27 12 
            📧 hcmvoyage1@gmail.com
        """)
    
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
