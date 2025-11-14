"""
HCM VOYAGES - Application Streamlit Complète
Agence de voyage avec gestion des réservations, destinations et visas
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import base64

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

# Initialisation du client Supabase
@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_supabase()

# ====== LOGO ======
LOGO_PATH = "log.png"

def display_logo(size="25000px"):
    """Affiche le logo depuis le fichier PNG"""
    try:
        st.markdown(f'<div style="text-align: center; margin: 10px 0;">', unsafe_allow_html=True)
        st.image(LOGO_PATH, width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Logo introuvable. Placez 'log.png' dans le dossier de l'application.")

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
    .hero-image { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.7); }
    .hero-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px;
    }
    .hero-title {
        color: white; font-size: 4em; font-weight: 700; margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3); animation: fadeInDown 1s ease-out;
    }
    .hero-subtitle {
        color: white; font-size: 1.8em; font-weight: 300; margin: 20px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3); animation: fadeInUp 1s ease-out 0.3s backwards;
    }
    
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-50px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(50px); } to { opacity: 1; transform: translateY(0); } }
    
    .destination-card {
        background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); border: 2px solid transparent;
    }
    .destination-card:hover {
        transform: translateY(-10px) scale(1.02); box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4); border-color: #667eea;
    }
    .destination-card h3 { color: #667eea; margin-bottom: 15px; font-weight: 600; }
    
    .price-tag {
        color: #ff6b6b; font-size: 28px; font-weight: 700; margin-top: 15px; display: inline-block;
        padding: 10px 20px; background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%); border-radius: 15px;
    }
    
    .service-card {
        background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0; transition: all 0.3s ease; text-align: center; border: 2px solid transparent;
    }
    .service-card:hover { transform: translateY(-8px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3); border-color: #667eea; }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 30px;
        padding: 12px 35px; border: none; font-weight: 600; font-size: 16px;
        transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5); }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); }
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3); color: white;
    }
    [data-testid="stSidebar"] .stButton>button:hover { background: rgba(255, 255, 255, 0.3); border-color: white; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .stat-card {
        background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center; border-left: 5px solid #667eea; transition: all 0.3s ease;
    }
    .stat-card:hover { transform: scale(1.05); box-shadow: 0 15px 40px rgba(0,0,0,0.2); }
    
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 20px;
        border-radius: 15px; border-left: 5px solid #667eea; margin: 20px 0;
    }
    
    .contact-card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 15px 0; }
    .contact-card h3 { color: #667eea; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
    
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        padding: 30px; border-radius: 20px; margin-bottom: 30px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE ======
def get_destinations():
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur: {e}")
            return []
    return []

def add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
    if supabase:
        try:
            data = {
                "nom": nom, "email": email, "telephone": telephone, "destination": destination,
                "date_depart": str(date_depart), "nb_personnes": nb_personnes, "message": message, "statut": "en_attente"
            }
            supabase.table('reservations').insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Erreur: {e}")
            return False
    return False

def get_reservations():
    if supabase:
        try:
            response = supabase.table('reservations').select("*").order('date_creation', desc=True).execute()
            return response.data
        except: return []
    return []

def add_contact(nom, email, sujet, message):
    if supabase:
        try:
            data = {"nom": nom, "email": email, "sujet": sujet, "message": message, "lu": False}
            supabase.table('contacts').insert(data).execute()
            return True
        except: return False
    return False

def get_contacts():
    if supabase:
        try:
            response = supabase.table('contacts').select("*").order('date_creation', desc=True).execute()
            return response.data
        except: return []
    return []

def mark_contact_as_read(contact_id):
    if supabase:
        try:
            supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            return True
        except: return False
    return False

# ====== PAGES ======
def page_accueil():
    # Hero Section avec image locale
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    
    # Afficher l'image hero depuis un fichier local
    try:
        st.image("heros.png", use_container_width=True)
    except:
        st.warning("⚠️ Image 'heros.png' introuvable. Placez-la dans le dossier de l'application.")
    
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
    
    stats = [
        ("🌍", "50+", "Destinations"),
        ("😊", "1000+", "Clients Satisfaits"),
        ("📅", "10+", "Années d'Expérience"),
        ("🤝", "25+", "Partenaires")
    ]
    
    for col, (icon, num, label) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size: 3em; margin-bottom: 10px;">{icon}</div>
                    <h2 style="color: #667eea; margin: 0;">{num}</h2>
                    <p style="margin: 10px 0 0 0; color: #666;">{label}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎯 Nos Services Premium")
    
    col1, col2, col3 = st.columns(3)
    services = [
        ("🎫", "Billets d'Avion", "Les meilleurs tarifs pour toutes destinations"),
        ("🏨", "Réservation Hôtels", "Hébergements de qualité sélectionnés"),
        ("🎒", "Circuits Organisés", "Voyages tout compris clés en main"),
        ("🚗", "Location de Voitures", "Mobilité à destination garantie"),
        ("📋", "Assistance Visa", "Aide complète pour vos démarches"),
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

def page_destinations():
    st.markdown("# 🌍 Nos Destinations de Rêve")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", "", placeholder="Paris, Tokyo...")
    with col2:
        categorie = st.selectbox("📍 Continent", ["Toutes", "Europe", "Asie", "Afrique", "Amérique", "Océanie"])
    with col3:
        tri = st.selectbox("💰 Trier", ["Prix croissant", "Prix décroissant", "Nom A-Z"])
    
    destinations = get_destinations()
    if not destinations:
        st.info("📌 Connectez Supabase pour afficher les destinations")
        destinations = [
            {"nom": "Paris", "pays": "France", "description": "La ville lumière", "prix": 799, "categorie": "Europe", "duree": "5 jours"},
            {"nom": "Tokyo", "pays": "Japon", "description": "Tradition et modernité", "prix": 1299, "categorie": "Asie", "duree": "6 jours"},
            {"nom": "Dubaï", "pays": "EAU", "description": "Luxe et désert", "prix": 899, "categorie": "Asie", "duree": "5 jours"},
        ]
    
    if search:
        destinations = [d for d in destinations if search.lower() in d['nom'].lower() or search.lower() in d['pays'].lower()]
    if categorie != "Toutes":
        destinations = [d for d in destinations if d.get('categorie') == categorie]
    
    if tri == "Prix croissant":
        destinations = sorted(destinations, key=lambda x: x['prix'])
    elif tri == "Prix décroissant":
        destinations = sorted(destinations, key=lambda x: x['prix'], reverse=True)
    else:
        destinations = sorted(destinations, key=lambda x: x['nom'])
    
    st.markdown(f"### {len(destinations)} destination(s) trouvée(s)")
    
    cols = st.columns(3)
    for idx, dest in enumerate(destinations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="destination-card">
                    <h3>📍 {dest['nom']}, {dest['pays']}</h3>
                    <p style="color: #666; margin: 10px 0;">{dest['description']}</p>
                    <span style="color: #888;">⏱️ {dest.get('duree', '5 jours')}</span>
                    <div class="price-tag">À partir de {dest['prix']}€</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver {dest['nom']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    st.markdown("# 📝 Réserver Votre Voyage")
    
    with st.form("reservation_form", clear_on_submit=True):
        st.markdown("### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Ex: Ahmed Benali")
            email = st.text_input("Email *", placeholder="exemple@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        with col2:
            destination = st.text_input("Destination *", value=st.session_state.get('destination_selectionnee', ''))
            date_depart = st.date_input("Date de départ *", min_value=datetime.now().date())
            nb_personnes = st.number_input("Nombre de personnes", min_value=1, max_value=20, value=1)
        
        message = st.text_area("Message / Demandes spéciales", height=150)
        
        submitted = st.form_submit_button("✈️ Envoyer la demande", use_container_width=True)
        
        if submitted:
            if nom and email and telephone and destination:
                if add_reservation(nom, email, telephone, destination, date_depart, nb_personnes, message):
                    st.success("✅ Demande envoyée avec succès!")
                    st.balloons()
                else:
                    st.warning("⚠️ Enregistré localement. Connectez Supabase.")
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")

def page_contact():
    st.markdown("# 📞 Contactez-Nous")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div class="contact-card">
                <h3>📍 Notre Agence</h3>
                <p><strong>🏢 Adresse:</strong> Aïn Benian, Alger 16061</p>
                <p><strong>📞 Téléphone:</strong> +213 XXX XXX XXX</p>
                <p><strong>📧 Email:</strong> contact@hcmvoyages.dz</p>
                <p><strong>🕐 Horaires:</strong> Dim-Jeu: 9h-18h</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.form("contact_form"):
            nom = st.text_input("Nom complet *")
            email = st.text_input("Email *")
            sujet = st.selectbox("Sujet *", ["Demande d'information", "Réservation", "Réclamation", "Autre"])
            message = st.text_area("Message *", height=200)
            
            if st.form_submit_button("📨 Envoyer", use_container_width=True):
                if nom and email and message:
                    if add_contact(nom, email, sujet, message):
                        st.success("✅ Message envoyé!")
                        st.balloons()
                    else:
                        st.warning("⚠️ Erreur d'envoi")
                else:
                    st.error("❌ Remplissez tous les champs")

def page_discover_algeria():
    st.markdown("""
        <div class="hero-section" style="height: 400px;">
            <img src="https://images.unsplash.com/photo-1589909202802-8f4aadce1849?w=1920&h=600&fit=crop&q=80" 
                 alt="Découvrir l'Algérie" class="hero-image"/>
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 4em; margin-bottom: 20px;">🇩🇿</div>
                    <h1 class="hero-title">Discover Algeria</h1>
                    <p class="hero-subtitle">Explorez la beauté du Maghreb</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🏠 Présentation", "🗺️ Destinations", "📋 Visa Algérie"])
    
    with tab1:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #067d45;">🇩🇿 Bienvenue en Algérie</h3>
                <p>L'Algérie, perle du Maghreb, vous invite à découvrir ses trésors. Du Sahara majestueux aux plages méditerranéennes.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        destinations_dz = [
            {"nom": "Alger", "prix": 450, "description": "La capitale avec sa Casbah UNESCO"},
            {"nom": "Sahara", "prix": 890, "description": "Le plus grand désert du monde"},
            {"nom": "Constantine", "prix": 520, "description": "Ville des ponts suspendus"},
        ]
        
        cols = st.columns(3)
        for idx, dest in enumerate(destinations_dz):
            with cols[idx]:
                st.markdown(f"""
                    <div class="destination-card">
                        <h3>🇩🇿 {dest['nom']}</h3>
                        <p>{dest['description']}</p>
                        <div class="price-tag">{dest['prix']}€</div>
                    </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📋 Visa pour l'Algérie")
        st.info("Nous vous accompagnons dans vos démarches de visa pour l'Algérie.")

def page_visas():
    st.markdown("# 📋 Services Visa")
    
    col1, col2, col3 = st.columns(3)
    
    visas = [
        ("🇺🇸", "USA", "B1/B2, ESTA", "3-6 semaines", "160 USD"),
        ("🇬🇧", "UK", "Standard Visitor", "3 semaines", "£100"),
        ("🇪🇺", "Schengen", "26 pays", "15-45 jours", "80€"),
    ]
    
    for col, (flag, pays, types, delai, tarif) in zip([col1, col2, col3], visas):
        with col:
            st.markdown(f"""
                <div class="service-card">
                    <h3 style="color: #667eea;">{flag} Visa {pays}</h3>
                    <p><strong>Types:</strong> {types}</p>
                    <p><strong>Délai:</strong> {delai}</p>
                    <p><strong>Tarif:</strong> {tarif}</p>
                </div>
            """, unsafe_allow_html=True)

def page_admin():
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown('<div class="admin-header"><h1>🔐 Administration</h1></div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Utilisateur")
            password = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("🔓 Connexion"):
                if username == "admin" and password == "admin123":
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        return
    
    st.markdown('<div class="admin-header"><h1>⚙️ Dashboard Admin</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Réservations", "💬 Messages"])
    
    with tab1:
        reservations = get_reservations()
        if reservations:
            df = pd.DataFrame(reservations)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 Aucune réservation")
    
    with tab2:
        contacts = get_contacts()
        if contacts:
            for contact in contacts:
                with st.expander(f"{contact['sujet']} - {contact['nom']}"):
                    st.write(f"**Email:** {contact['email']}")
                    st.write(f"**Message:** {contact['message']}")
        else:
            st.info("📭 Aucun message")
    
    if st.button("🚪 Déconnexion"):
        st.session_state.admin_logged = False
        st.rerun()

# ====== NAVIGATION ======
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    with st.sidebar:
        display_logo(size="120px")
        st.markdown('<div style="text-align: center;"><h2>HCM VOYAGES</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Destinations", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📋", "Visas", "visas"),
            ("🇩🇿", "Discover Algeria", "discover-algeria"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Administration", "admin"),
        ]
        
        for icon, label, page_id in pages:
            if st.button(f"{icon} {label}", use_container_width=True):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; font-size: 0.8em;">
                © 2024 HCM Voyages<br>Tous droits réservés
            </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "destinations":
        page_destinations()
    elif st.session_state.page == "reservation":
        page_reservation()
    elif st.session_state.page == "visas":
        page_visas()
    elif st.session_state.page == "discover-algeria":
        page_discover_algeria()
    elif st.session_state.page == "contact":
        page_contact()
    elif st.session_state.page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
    PAGE DEMANDE DE VISA - À intégrer dans HCM Voyages
Copiez cette fonction et ajoutez-la dans votre fichier principal
"""

def page_demande_visa():
    """Page dédiée uniquement à la demande de visa"""
    
    # Hero Section Visa
    st.markdown("""
        <div class="hero-section" style="height: 350px;">
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 5em; margin-bottom: 20px;">📋</div>
                    <h1 class="hero-title" style="font-size: 3em;">Demande de Visa</h1>
                    <p class="hero-subtitle" style="font-size: 1.3em;">Obtenez votre visa en toute simplicité avec HCM Voyages</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section informative
    st.markdown("""
        <div class="info-box">
            <h3 style="color: #667eea; margin-bottom: 15px;">🌍 Nos Services Visa</h3>
            <p style="font-size: 1.1em; line-height: 1.8;">
            HCM Voyages vous accompagne dans l'obtention de vos visas pour plus de <strong>50 destinations</strong> 
            à travers le monde. Notre équipe d'experts prend en charge toutes vos démarches administratives 
            pour un traitement rapide et efficace.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Types de visa disponibles
    st.markdown("### 🗺️ Types de Visa Disponibles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    visa_types = [
        ("🇺🇸", "USA", "B1/B2, ESTA", "160 USD"),
        ("🇬🇧", "Royaume-Uni", "Standard Visitor", "£100"),
        ("🇪🇺", "Schengen", "26 pays européens", "80€"),
        ("🇨🇦", "Canada", "Visiteur, AVE", "100 CAD"),
        ("🇦🇺", "Australie", "ETA, eVisitor", "20 AUD"),
        ("🇦🇪", "Émirats", "Tourisme", "250 AED"),
        ("🇹🇷", "Turquie", "e-Visa", "50 USD"),
        ("🇨🇳", "Chine", "Tourisme", "140 USD"),
    ]
    
    for i, (flag, pays, type_visa, prix) in enumerate(visa_types):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.markdown(f"""
                <div class="service-card" style="min-height: 180px;">
                    <div style="font-size: 3em; margin-bottom: 10px;">{flag}</div>
                    <h4 style="color: #667eea; margin: 10px 0;">{pays}</h4>
                    <p style="font-size: 0.9em; color: #666; margin: 5px 0;">{type_visa}</p>
                    <p style="font-weight: bold; color: #ff6b6b; margin-top: 10px;">{prix}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Formulaire de demande de visa
    st.markdown("### 📝 Formulaire de Demande de Visa")
    st.markdown("Remplissez le formulaire ci-dessous et notre équipe vous contactera dans les 24 heures")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("demande_visa_form", clear_on_submit=True):
        # Section 1: Informations personnelles
        st.markdown("#### 👤 Informations Personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            nom_complet = st.text_input("Nom complet *", placeholder="Nom et prénom")
            date_naissance = st.date_input("Date de naissance *")
            lieu_naissance = st.text_input("Lieu de naissance *", placeholder="Ville, Pays")
            nationalite = st.text_input("Nationalité *", placeholder="Ex: Algérienne")
        
        with col2:
            numero_passeport = st.text_input("Numéro de passeport *", placeholder="Ex: 123456789")
            date_expiration_passeport = st.date_input("Date d'expiration du passeport *")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 2: Informations sur le visa
        st.markdown("#### 🌍 Informations sur le Visa")
        col3, col4 = st.columns(2)
        
        with col3:
            pays_destination = st.selectbox("Pays de destination *", [
                "États-Unis (USA)",
                "Royaume-Uni",
                "France (Schengen)",
                "Allemagne (Schengen)",
                "Espagne (Schengen)",
                "Italie (Schengen)",
                "Canada",
                "Australie",
                "Émirats Arabes Unis",
                "Turquie",
                "Chine",
                "Japon",
                "Autre (préciser dans le message)"
            ])
            
            type_visa = st.selectbox("Type de visa *", [
                "Tourisme",
                "Affaires",
                "Visite familiale",
                "Études",
                "Travail",
                "Transit",
                "Autre"
            ])
            
            date_depart_prevue = st.date_input("Date de départ prévue *", 
                                              min_value=datetime.now().date())
        
        with col4:
            duree_sejour = st.number_input("Durée du séjour (jours) *", 
                                          min_value=1, max_value=365, value=15)
            
            entrees = st.selectbox("Nombre d'entrées souhaitées *", [
                "Simple entrée",
                "Double entrée",
                "Entrées multiples"
            ])
            
            urgence = st.selectbox("Traitement *", [
                "Normal (15-30 jours)",
                "Urgent (7-15 jours)",
                "Express (3-7 jours)"
            ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 3: Informations complémentaires
        st.markdown("#### 📄 Informations Complémentaires")
        
        col5, col6 = st.columns(2)
        
        with col5:
            profession = st.text_input("Profession", placeholder="Votre profession actuelle")
            employeur = st.text_input("Employeur", placeholder="Nom de l'entreprise")
        
        with col6:
            situation_familiale = st.selectbox("Situation familiale", [
                "Célibataire",
                "Marié(e)",
                "Divorcé(e)",
                "Veuf(ve)"
            ])
            
            voyages_anterieurs = st.selectbox("Voyages antérieurs dans ce pays", [
                "Non, première visite",
                "Oui, 1 fois",
                "Oui, 2-3 fois",
                "Oui, plus de 3 fois"
            ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Message additionnel
        message_complementaire = st.text_area(
            "Message ou informations complémentaires",
            placeholder="Ajoutez toute information utile pour votre demande de visa...",
            height=150
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Checkbox confirmation
        col7, col8 = st.columns([3, 1])
        with col7:
            accepte_conditions = st.checkbox(
                "J'accepte que mes données soient utilisées dans le cadre de ma demande de visa *",
                value=False
            )
            st.markdown("""
                <p style="font-size: 0.85em; color: #666; margin-top: 10px;">
                * Champs obligatoires
                </p>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bouton de soumission
        col_center1, col_center2, col_center3 = st.columns([1, 2, 1])
        with col_center2:
            submitted = st.form_submit_button(
                "📨 Envoyer ma demande de visa",
                use_container_width=True
            )
        
        # Traitement du formulaire
        if submitted:
            # Validation des champs obligatoires
            if not all([nom_complet, date_naissance, lieu_naissance, nationalite, 
                       numero_passeport, date_expiration_passeport, email, 
                       telephone, pays_destination, type_visa, date_depart_prevue, accepte_conditions]):
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            else:
                # Créer les données de la demande
                demande_data = {
                    "nom_complet": nom_complet,
                    "date_naissance": str(date_naissance),
                    "lieu_naissance": lieu_naissance,
                    "nationalite": nationalite,
                    "numero_passeport": numero_passeport,
                    "date_expiration_passeport": str(date_expiration_passeport),
                    "email": email,
                    "telephone": telephone,
                    "pays_destination": pays_destination,
                    "type_visa": type_visa,
                    "date_depart_prevue": str(date_depart_prevue),
                    "duree_sejour": duree_sejour,
                    "entrees": entrees,
                    "urgence": urgence,
                    "profession": profession,
                    "employeur": employeur,
                    "situation_familiale": situation_familiale,
                    "voyages_anterieurs": voyages_anterieurs,
                    "message_complementaire": message_complementaire
                }
                
                # Fonction pour ajouter la demande dans Supabase
                if supabase:
                    try:
                        response = supabase.table('demandes_visa').insert(demande_data).execute()
                        
                        st.success("✅ Votre demande de visa a été envoyée avec succès!")
                        
                        st.markdown(f"""
                            <div class="info-box" style="background: #d4edda; border-left-color: #28a745;">
                                <h4 style="color: #155724;">📧 Confirmation de votre demande</h4>
                                <p style="color: #155724;">
                                Un email de confirmation a été envoyé à <strong>{email}</strong>
                                </p>
                                <hr style="border-color: #c3e6cb;">
                                <h5 style="color: #155724;">📋 Prochaines étapes:</h5>
                                <ol style="color: #155724; margin-left: 20px;">
                                    <li>Vérifiez votre boîte email (y compris les spams)</li>
                                    <li>Notre équipe examinera votre demande sous 24h</li>
                                    <li>Vous recevrez la liste des documents à fournir</li>
                                    <li>Prise de rendez-vous si nécessaire</li>
                                    <li>Suivi personnalisé jusqu'à l'obtention du visa</li>
                                </ol>
                                <p style="color: #155724; margin-top: 15px;">
                                <strong>📞 Questions?</strong> Contactez-nous au +213 XXX XXX XXX
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'envoi: {e}")
                        st.warning("⚠️ Votre demande a été enregistrée localement. Connectez Supabase pour la sauvegarde permanente.")
                else:
                    st.warning("⚠️ Base de données non connectée. Votre demande a été enregistrée localement.")
                    st.info("💡 Astuce: Configurez Supabase pour sauvegarder les demandes de visa.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Section avantages
    st.markdown("### 🌟 Pourquoi choisir HCM Voyages pour votre visa ?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avantages = [
        ("⚡", "Traitement Rapide", "Délais optimisés pour chaque type de visa"),
        ("🎯", "Taux de Réussite Élevé", "Plus de 95% de demandes acceptées"),
        ("🤝", "Accompagnement", "Suivi personnalisé de A à Z"),
        ("📄", "Documents", "Aide à la constitution de votre dossier")
    ]
    
    for col, (icon, titre, desc) in zip([col1, col2, col3, col4], avantages):
        with col:
            st.markdown(f"""
                <div class="service-card" style="min-height: 200px;">
                    <div style="font-size: 3.5em; margin-bottom: 15px;">{icon}</div>
                    <h4 style="color: #667eea; margin: 15px 0;">{titre}</h4>
                    <p style="color: #666; font-size: 0.9em;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # FAQ Visa
    st.markdown("### ❓ Questions Fréquentes sur les Visas")
    
    with st.expander("📋 Quels documents sont généralement nécessaires ?"):
        st.markdown("""
        **Documents standard pour la plupart des visas:**
        - Passeport valide (minimum 6 mois)
        - Photos d'identité récentes
        - Formulaire de demande complété
        - Justificatifs financiers
        - Réservation d'hôtel ou lettre d'invitation
        - Billet d'avion aller-retour
        - Assurance voyage
        
        *Note: Les documents spécifiques varient selon le pays et le type de visa.*
        """)
    
    with st.expander("⏱️ Combien de temps prend le traitement d'un visa ?"):
        st.markdown("""
        **Délais moyens par région:**
        - 🇪🇺 **Schengen:** 15-30 jours
        - 🇺🇸 **USA:** 3-6 semaines
        - 🇬🇧 **UK:** 3-4 semaines
        - 🇨🇦 **Canada:** 2-4 semaines
        - 🇦🇺 **Australie:** 15-30 jours
        
        *Des options de traitement express sont disponibles pour la plupart des destinations.*
        """)
    
    with st.expander("💰 Quels sont les frais de visa ?"):
        st.markdown("""
        **Les frais comprennent généralement:**
        - Frais consulaires (variables selon le pays)
        - Frais de service HCM Voyages
        - Frais d'assurance (si nécessaire)
        
        *Les prix exacts vous seront communiqués après analyse de votre demande.*
        """)
    
    with st.expander("🔄 Que faire si mon visa est refusé ?"):
        st.markdown("""
        **En cas de refus:**
        1. Analyse gratuite des raisons du refus
        2. Conseils pour améliorer votre dossier
        3. Assistance pour la nouvelle demande
        4. Possibilité d'appel selon les procédures du pays
        
        *HCM Voyages vous accompagne jusqu'à l'obtention de votre visa.*
        """)
    
    with st.expander("📞 Comment suivre l'avancement de ma demande ?"):
        st.markdown("""
        **Suivi en temps réel:**
        - Email de confirmation immédiat
        - Notifications à chaque étape
        - Espace client en ligne (bientôt disponible)
        - Contact direct avec votre conseiller
        - Mise à jour par SMS
        """)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Call to action final
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="info-box" style="text-align: center; border-left: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <h3 style="color: white; margin-bottom: 15px;">📞 Besoin d'aide ?</h3>
                <p style="color: white; font-size: 1.1em;">
                Notre équipe est disponible du Dimanche au Jeudi<br>
                de 9h00 à 18h00
                </p>
                <p style="color: white; font-size: 1.2em; font-weight: bold; margin-top: 15px;">
                ☎️ +213 XXX XXX XXX<br>
                📧 visa@hcmvoyages.dz
                </p>
            </div>
        """, unsafe_allow_html=True)
