"""
HCM VOYAGES - Application Streamlit Améliorée
Agence de voyage avec gestion complète des réservations, destinations et visas
"""

import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
import re

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
    except Exception as e:
        st.error(f"Erreur de connexion Supabase: {e}")
        return None

supabase = init_supabase()

# ====== FONCTIONS UTILITAIRES ======
def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valide le format d'un numéro de téléphone algérien"""
    pattern = r'^\+?213[0-9]{9}$|^0[0-9]{9}$'
    return re.match(pattern, phone.replace(' ', '')) is not None

def format_currency(amount):
    """Formate un montant en devise"""
    return f"{amount:,.0f}".replace(',', ' ') + " €"

# ====== LOGO ======
def display_logo(size="300px"):
    """Affiche le logo"""
    try:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
        st.image("log.png", width=int(size.replace("px", "")))
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <div style="font-size: {size}; color: #667eea;">✈️</div>
            </div>
        """, unsafe_allow_html=True)

# ====== CSS AMÉLIORÉ ======
st.markdown("""
    <style>
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
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
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
        from { opacity: 0; transform: translateY(-50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Cards */
    .destination-card, .service-card, .stat-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 15px 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
    }
    
    .destination-card:hover, .service-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        border-color: #667eea;
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
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 20px 0;
    }
    
    .success-box {
        background: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    /* Tables */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ====== FONCTIONS SUPABASE AMÉLIORÉES ======
def get_destinations():
    """Récupère toutes les destinations actives"""
    if supabase:
        try:
            response = supabase.table('destinations').select("*").eq('actif', True).order('nom').execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Erreur lors de la récupération des destinations: {e}")
            return []
    return []

def add_reservation(data):
    """Ajoute une réservation avec validation"""
    if supabase:
        try:
            data['statut'] = 'en_attente'
            data['date_creation'] = datetime.now().isoformat()
            response = supabase.table('reservations').insert(data).execute()
            return True, "Réservation enregistrée avec succès"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    return False, "Base de données non connectée"

def get_reservations(limit=None):
    """Récupère les réservations"""
    if supabase:
        try:
            query = supabase.table('reservations').select("*").order('date_creation', desc=True)
            if limit:
                query = query.limit(limit)
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    return []

def update_reservation_status(reservation_id, new_status):
    """Met à jour le statut d'une réservation"""
    if supabase:
        try:
            supabase.table('reservations').update({"statut": new_status}).eq('id', reservation_id).execute()
            return True
        except:
            return False
    return False

def add_contact(data):
    """Ajoute un message de contact"""
    if supabase:
        try:
            data['lu'] = False
            data['date_creation'] = datetime.now().isoformat()
            supabase.table('contacts').insert(data).execute()
            return True, "Message envoyé avec succès"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    return False, "Base de données non connectée"

def get_contacts(unread_only=False):
    """Récupère les messages de contact"""
    if supabase:
        try:
            query = supabase.table('contacts').select("*").order('date_creation', desc=True)
            if unread_only:
                query = query.eq('lu', False)
            response = query.execute()
            return response.data if response.data else []
        except:
            return []
    return []

def mark_contact_as_read(contact_id):
    """Marque un message comme lu"""
    if supabase:
        try:
            supabase.table('contacts').update({"lu": True}).eq('id', contact_id).execute()
            return True
        except:
            return False
    return False

# ====== STATISTIQUES ======
def get_statistics():
    """Calcule les statistiques de l'application"""
    stats = {
        'total_reservations': 0,
        'reservations_en_attente': 0,
        'reservations_confirmees': 0,
        'messages_non_lus': 0,
        'destinations_actives': 0
    }
    
    if supabase:
        try:
            # Réservations
            reservations = get_reservations()
            stats['total_reservations'] = len(reservations)
            stats['reservations_en_attente'] = len([r for r in reservations if r.get('statut') == 'en_attente'])
            stats['reservations_confirmees'] = len([r for r in reservations if r.get('statut') == 'confirme'])
            
            # Messages
            contacts = get_contacts(unread_only=True)
            stats['messages_non_lus'] = len(contacts)
            
            # Destinations
            destinations = get_destinations()
            stats['destinations_actives'] = len(destinations)
        except:
            pass
    
    return stats

# ====== PAGES ======
def page_accueil():
    """Page d'accueil améliorée"""
    
    # Hero Section
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
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
    
    # Statistiques
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
    
    # Services
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
    
    # Call to action
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌍 Découvrir nos destinations", use_container_width=True, type="primary"):
            st.session_state.page = "destinations"
            st.rerun()

def page_destinations():
    """Page destinations avec recherche avancée"""
    st.markdown("# 🌍 Nos Destinations de Rêve")
    
    # Filtres
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", "", placeholder="Paris, Tokyo, Dubaï...")
    with col2:
        categorie = st.selectbox("📍 Continent", ["Toutes", "Europe", "Asie", "Afrique", "Amérique", "Océanie"])
    with col3:
        tri = st.selectbox("💰 Trier par", ["Prix croissant", "Prix décroissant", "Nom A-Z", "Nom Z-A"])
    
    # Récupération des destinations
    destinations = get_destinations()
    
    # Destinations par défaut si Supabase n'est pas connecté
    if not destinations:
        st.info("📌 Données de démonstration (connectez Supabase pour les vraies données)")
        destinations = [
            {"nom": "Paris", "pays": "France", "description": "La ville lumière avec ses monuments emblématiques", "prix": 799, "categorie": "Europe", "duree": "5 jours"},
            {"nom": "Tokyo", "pays": "Japon", "description": "Tradition et modernité fusionnent", "prix": 1299, "categorie": "Asie", "duree": "6 jours"},
            {"nom": "Dubaï", "pays": "EAU", "description": "Luxe et désert, une destination unique", "prix": 899, "categorie": "Asie", "duree": "5 jours"},
            {"nom": "Rome", "pays": "Italie", "description": "Histoire antique et cuisine divine", "prix": 699, "categorie": "Europe", "duree": "4 jours"},
            {"nom": "New York", "pays": "USA", "description": "La ville qui ne dort jamais", "prix": 1499, "categorie": "Amérique", "duree": "7 jours"},
            {"nom": "Marrakech", "pays": "Maroc", "description": "Magie des souks et des riads", "prix": 499, "categorie": "Afrique", "duree": "4 jours"},
        ]
    
    # Filtrage
    filtered_destinations = destinations
    
    if search:
        filtered_destinations = [
            d for d in filtered_destinations 
            if search.lower() in d['nom'].lower() or search.lower() in d['pays'].lower()
        ]
    
    if categorie != "Toutes":
        filtered_destinations = [d for d in filtered_destinations if d.get('categorie') == categorie]
    
    # Tri
    if tri == "Prix croissant":
        filtered_destinations = sorted(filtered_destinations, key=lambda x: x['prix'])
    elif tri == "Prix décroissant":
        filtered_destinations = sorted(filtered_destinations, key=lambda x: x['prix'], reverse=True)
    elif tri == "Nom A-Z":
        filtered_destinations = sorted(filtered_destinations, key=lambda x: x['nom'])
    else:  # Z-A
        filtered_destinations = sorted(filtered_destinations, key=lambda x: x['nom'], reverse=True)
    
    # Affichage
    st.markdown(f"### ✈️ {len(filtered_destinations)} destination(s) trouvée(s)")
    
    if not filtered_destinations:
        st.warning("Aucune destination ne correspond à vos critères de recherche")
        return
    
    # Grille de destinations
    cols = st.columns(3)
    for idx, dest in enumerate(filtered_destinations):
        with cols[idx % 3]:
            st.markdown(f"""
                <div class="destination-card">
                    <h3>📍 {dest['nom']}, {dest['pays']}</h3>
                    <p style="color: #666; margin: 10px 0; min-height: 60px;">{dest['description']}</p>
                    <span style="color: #888;">⏱️ {dest.get('duree', '5 jours')}</span>
                    <div class="price-tag">À partir de {format_currency(dest['prix'])}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✈️ Réserver", key=f"btn_{idx}", use_container_width=True):
                st.session_state.destination_selectionnee = dest['nom']
                st.session_state.page = "reservation"
                st.rerun()

def page_reservation():
    """Page de réservation avec validation améliorée"""
    st.markdown("# 📝 Réserver Votre Voyage")
    
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
                destination = st.text_input(
                    "Destination *", 
                    value=st.session_state.get('destination_selectionnee', ''),
                    placeholder="Ex: Paris"
                )
                date_depart = st.date_input(
                    "Date de départ *", 
                    min_value=datetime.now().date()
                
                )
                
                nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
                nb_de jours = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            message = st.text_area(
                "Message / Demandes spéciales", 
                height=150,
                placeholder="Préférences, besoins particuliers..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("✈️ Envoyer la demande de réservation", use_container_width=True)
            
            if submitted:
                # Validation
                errors = []
                
                if not nom or len(nom) < 3:
                    errors.append("Le nom doit contenir au moins 3 caractères")
                
                if not email or not validate_email(email):
                    errors.append("Email invalide")
                
                if not telephone or not validate_phone(telephone):
                    errors.append("Numéro de téléphone invalide (format: +213XXXXXXXXX)")
                
                if not destination:
                    errors.append("Veuillez sélectionner une destination")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    # Enregistrement
                    data = {
                        "nom": nom,
                        "email": email,
                        "telephone": telephone,
                        "destination": destination,
                        "date_depart": str(date_depart),
                        "nb_personnes": nb_personnes,
                        "message": message
                    }
                    
                    success, message_result = add_reservation(data)
                    
                    if success:
                        st.success(f"✅ {message_result}")
                        st.markdown(f"""
                            <div class="info-box success-box">
                                <h4>🎉 Réservation enregistrée !</h4>
                                <p>Nous avons bien reçu votre demande pour <strong>{destination}</strong></p>
                                <p>Date de départ : <strong>{date_depart.strftime('%d/%m/%Y')}</strong></p>
                                <p>Nombre de personnes : <strong>{nb_personnes}</strong></p>
                                <hr>
                                <p>📧 Un email de confirmation a été envoyé à <strong>{email}</strong></p>
                                <p>📞 Notre équipe vous contactera sous 24h</p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.error(f"❌ {message_result}")
    
    with tab2:
        st.markdown("### 💰 Demande de Devis Personnalisé")
        st.markdown("""
            <div class="info-box">
                <p style="font-size: 1.05em;">
                Recevez un devis détaillé et personnalisé pour votre voyage. 
                Indiquez vos dates, destination et préférences.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("devis_form", clear_on_submit=True):
            st.markdown("#### 👤 Vos Coordonnées")
            col1, col2 = st.columns(2)
            
            with col1:
                devis_nom = st.text_input("Nom complet *", placeholder="Votre nom")
                devis_email = st.text_input("Email *", placeholder="votre@email.com")
                devis_telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            
            with col2:
                devis_destination = st.selectbox("Destination *", [
                    "-- Sélectionnez --", "Paris", "Istanbul", "Dubaï", "Londres", 
                    "Rome", "Barcelone", "Marrakech", "Le Caire", "New York", "Tokyo"
                ])
                devis_nb_personnes = st.number_input("Nombre de personnes *", min_value=1, max_value=20, value=1)
                devis_budget = st.select_slider("Budget approximatif", [
                    "Moins de 500€", "500€ - 1000€", "1000€ - 2000€", "Plus de 2000€"
                ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            devis_message = st.text_area("Commentaires / Demandes spéciales", height=120)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted_devis = st.form_submit_button("📨 Recevoir mon devis gratuit", use_container_width=True)
            
            if submitted_devis:
                if not all([devis_nom, devis_email, devis_telephone]) or devis_destination == "-- Sélectionnez --":
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
                else:
                    st.success("✅ Demande de devis envoyée avec succès!")
                    st.balloons()

def page_contact():
    """Page de contact améliorée"""
    st.markdown("# 📞 Contactez-Nous")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
            <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <h3 style="color: #667eea; margin-bottom: 25px;">📍 Notre Agence</h3>
                <p style="font-size: 1.1em; margin: 15px 0;">
                    <strong>🏢 Adresse:</strong><br>
                    Aïn Benian, Alger 16061<br>
                    Algérie
                </p>
                <p style="font-size: 1.1em; margin: 15px 0;">
                    <strong>📞 Téléphone:</strong><br>
                    +213 XXX XXX XXX
                </p>
                <p style="font-size: 1.1em; margin: 15px 0;">
                    <strong>📧 Email:</strong><br>
                    contact@hcmvoyages.dz
                </p>
                <p style="font-size: 1.1em; margin: 15px 0;">
                    <strong>🕐 Horaires:</strong><br>
                    Dimanche - Jeudi: 9h - 18h<br>
                    Vendredi - Samedi: Fermé
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💬 Envoyez-nous un message")
        
        with st.form("contact_form", clear_on_submit=True):
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            sujet = st.selectbox("Sujet *", [
                "Demande d'information",
                "Réservation",
                "Réclamation",
                "Partenariat",
                "Autre"
            ])
            message = st.text_area("Message *", height=200, placeholder="Votre message...")
            
            submitted = st.form_submit_button("📨 Envoyer le message", use_container_width=True)
            
            if submitted:
                if not nom or not email or not message:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")
                elif not validate_email(email):
                    st.error("❌ Email invalide")
                else:
                    data = {
                        "nom": nom,
                        "email": email,
                        "sujet": sujet,
                        "message": message
                    }
                    
                    success, result = add_contact(data)
                    
                    if success:
                        st.success(f"✅ {result}")
                        st.balloons()
                    else:
                        st.error(f"❌ {result}")

def page_admin():
    """Dashboard administrateur amélioré"""
    
    # Authentification
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    
    if not st.session_state.admin_logged:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px;">
                <h1>🔐 Administration HCM Voyages</h1>
                <p>Connectez-vous pour accéder au tableau de bord</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username = st.text_input("👤 Utilisateur", placeholder="admin")
                password = st.text_input("🔒 Mot de passe", type="password")
                
                if st.form_submit_button("🔓 Connexion", use_container_width=True):
                    if username == "admin" and password == "admin123":
                        st.session_state.admin_logged = True
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
        return
    
    # Dashboard principal
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;">
            <h1>⚙️ Dashboard Administrateur</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistiques
    stats = get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #667eea;">{stats['total_reservations']}</h2>
                <p>Réservations totales</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #ffa502;">{stats['reservations_en_attente']}</h2>
                <p>En attente</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #28a745;">{stats['reservations_confirmees']}</h2>
                <p>Confirmées</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <h2 style="color: #ff6348;">{stats['messages_non_lus']}</h2>
                <p>Messages non lus</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs pour les différentes sections
    tab1, tab2, tab3 = st.tabs(["📋 Réservations", "💬 Messages", "🌍 Destinations"])
    
    with tab1:
        st.markdown("### Gestion des Réservations")
        reservations = get_reservations()
        
        if reservations:
            df = pd.DataFrame(reservations)
            
            # Sélection des colonnes à afficher
            columns_to_display = ['nom', 'email', 'destination', 'date_depart', 'nb_personnes', 'statut']
            available_columns = [col for col in columns_to_display if col in df.columns]
            
            if available_columns:
                st.dataframe(
                    df[available_columns],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Actions
            st.markdown("#### Actions rapides")
            col1, col2 = st.columns(2)
            
            with col1:
                reservation_id = st.number_input("ID de la réservation", min_value=1, step=1)
            
            with col2:
                new_status = st.selectbox("Nouveau statut", ["en_attente", "confirme", "annule"])
            
            if st.button("✅ Mettre à jour le statut"):
                if update_reservation_status(reservation_id, new_status):
                    st.success(f"✅ Statut mis à jour pour la réservation #{reservation_id}")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la mise à jour")
        else:
            st.info("📭 Aucune réservation pour le moment")
    
    with tab2:
        st.markdown("### Messages de Contact")
        contacts = get_contacts()
        
        if contacts:
            for contact in contacts:
                status_icon = "✉️" if not contact.get('lu', False) else "📧"
                status_color = "#ff6348" if not contact.get('lu', False) else "#95a5a6"
                
                with st.expander(f"{status_icon} {contact.get('sujet', 'Sans sujet')} - {contact.get('nom', 'Anonyme')}"):
                    st.markdown(f"**Email:** {contact.get('email', 'N/A')}")
                    st.markdown(f"**Date:** {contact.get('date_creation', 'N/A')}")
                    st.markdown(f"**Message:**")
                    st.info(contact.get('message', 'Pas de message'))
                    
                    if not contact.get('lu', False):
                        if st.button(f"✅ Marquer comme lu", key=f"read_{contact.get('id')}"):
                            if mark_contact_as_read(contact.get('id')):
                                st.success("Message marqué comme lu")
                                st.rerun()
        else:
            st.info("📭 Aucun message")
    
    with tab3:
        st.markdown("### Destinations Actives")
        destinations = get_destinations()
        
        if destinations:
            df_dest = pd.DataFrame(destinations)
            st.dataframe(df_dest, use_container_width=True, hide_index=True)
            st.info(f"📍 {len(destinations)} destination(s) active(s)")
        else:
            st.info("🌍 Aucune destination configurée")
    
    # Déconnexion
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.admin_logged = False
        st.rerun()


def page_visas():
    """Page d'informations sur les visas"""
    st.markdown("# 📋 Services Visa")
    
    st.markdown("""
        <div class="info-box">
            <h3 style="color: #667eea;">🌍 Obtenez votre visa facilement</h3>
            <p style="font-size: 1.1em;">
            HCM Voyages vous accompagne dans toutes vos démarches de visa. 
            Notre équipe d'experts prend en charge votre dossier de A à Z.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🌍 Nos Services Visa Populaires")
    
    col1, col2, col3 = st.columns(3)
    
    visas_info = [
        ("🇺🇸", "USA", "B1/B2, ESTA", "3-6 semaines", "160 USD"),
        ("🇬🇧", "Royaume-Uni", "Standard Visitor", "3 semaines", "£100"),
        ("🇪🇺", "Schengen", "26 pays européens", "15-45 jours", "80€"),
        ("🇨🇦", "Canada", "Visiteur, AVE", "2-4 semaines", "100 CAD"),
        ("🇦🇺", "Australie", "ETA, eVisitor", "1-2 semaines", "20 AUD"),
        ("🇦🇪", "Émirats", "Tourisme", "5-7 jours", "250 AED"),
    ]
    
    for i, (flag, pays, types, delai, tarif) in enumerate(visas_info):
        col = [col1, col2, col3][i % 3]
        with col:
            st.markdown(f"""
                <div class="service-card" style="min-height: 220px;">
                    <div style="font-size: 3.5em; margin-bottom: 15px;">{flag}</div>
                    <h3 style="color: #667eea; margin: 15px 0;">Visa {pays}</h3>
                    <p style="margin: 8px 0;"><strong>Types:</strong> {types}</p>
                    <p style="margin: 8px 0;"><strong>Délai:</strong> {delai}</p>
                    <p style="margin: 8px 0; color: #ff6b6b; font-weight: bold; font-size: 1.2em;">{tarif}</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Faire une demande de visa", use_container_width=True, type="primary"):
            st.session_state.page = "demande-visa"
            st.rerun()


def page_demande_visa():
    """Page de demande de visa simplifiée"""
    st.markdown("# 📋 Demande de Visa")
    
    st.markdown("""
        <div class="hero-section" style="height: 300px;">
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 4em; margin-bottom: 15px;">📋</div>
                    <h1 class="hero-title" style="font-size: 2.5em;">Demande de Visa</h1>
                    <p class="hero-subtitle" style="font-size: 1.2em;">Obtenez votre visa rapidement</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 📝 Formulaire de Demande")
    
    with st.form("visa_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet *", placeholder="Votre nom")
            email = st.text_input("Email *", placeholder="votre@email.com")
            telephone = st.text_input("Téléphone *", placeholder="+213 XXX XXX XXX")
            numero_passeport = st.text_input("Numéro de passeport *")
        
        with col2:
            pays_destination = st.selectbox("Pays de destination *", [
                "-- Sélectionnez --", "États-Unis", "Royaume-Uni", "France", 
                "Allemagne", "Canada", "Australie", "Émirats", "Turquie"
            ])
            type_visa = st.selectbox("Type de visa *", [
                "Tourisme", "Affaires", "Visite familiale", "Études", "Travail"
            ])
            date_depart = st.date_input("Date de départ prévue *", min_value=datetime.now().date())
            urgence = st.selectbox("Traitement *", [
                "Normal (15-30 jours)", "Urgent (7-15 jours)", "Express (3-7 jours)"
            ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        message = st.text_area("Informations complémentaires", height=120)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📨 Envoyer ma demande", use_container_width=True)
        
        if submitted:
            if not all([nom, email, telephone, numero_passeport]) or pays_destination == "-- Sélectionnez --":
                st.error("❌ Veuillez remplir tous les champs obligatoires")
            else:
                st.success("✅ Demande de visa envoyée avec succès!")
                st.balloons()


def page_discover_algeria():
    """Page Discover Algeria"""
    st.markdown("""
        <div class="hero-section" style="height: 350px;">
            <div class="hero-overlay">
                <div style="text-align: center;">
                    <div style="font-size: 4em; margin-bottom: 15px;">🇩🇿</div>
                    <h1 class="hero-title">Discover Algeria</h1>
                    <p class="hero-subtitle">Explorez la beauté du Maghreb</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏠 Présentation", "🗺️ Destinations"])
    
    with tab1:
        st.markdown("""
            <div class="info-box">
                <h3 style="color: #067d45;">🇩🇿 Bienvenue en Algérie</h3>
                <p style="font-size: 1.1em; line-height: 1.8;">
                L'Algérie, perle du Maghreb, vous invite à découvrir ses trésors. 
                Du Sahara majestueux aux plages méditerranéennes, en passant par les villes historiques,
                l'Algérie offre une diversité exceptionnelle.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ✨ Pourquoi visiter l'Algérie ?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - 🏜️ **Le Sahara** : Le plus grand désert du monde
            - 🏛️ **Patrimoine UNESCO** : Sites historiques exceptionnels
            - 🏖️ **Côtes méditerranéennes** : Plages magnifiques
            """)
        
        with col2:
            st.markdown("""
            - 🍲 **Gastronomie riche** : Saveurs authentiques
            - 🎭 **Culture vivante** : Traditions millénaires
            - 🤝 **Hospitalité** : Accueil chaleureux
            """)
    
    with tab2:
        st.markdown("### 🗺️ Destinations Phares")
        
        destinations_dz = [
            {"nom": "Alger", "description": "La capitale avec sa Casbah UNESCO", "prix": 450},
            {"nom": "Sahara", "description": "Le plus grand désert du monde", "prix": 890},
            {"nom": "Constantine", "description": "Ville des ponts suspendus", "prix": 520},
            {"nom": "Oran", "description": "Perle de la Méditerranée", "prix": 480},
            {"nom": "Tlemcen", "description": "Ville d'art et d'histoire", "prix": 510},
            {"nom": "Annaba", "description": "Hippone l'antique", "prix": 470},
        ]
        
        cols = st.columns(3)
        for idx, dest in enumerate(destinations_dz):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div class="destination-card">
                        <h3>🇩🇿 {dest['nom']}</h3>
                        <p style="min-height: 50px;">{dest['description']}</p>
                        <div class="price-tag">{format_currency(dest['prix'])}</div>
                    </div>
                """, unsafe_allow_html=True)


# ====== NAVIGATION PRINCIPALE ======
def main():
    """Fonction principale de navigation"""
    
    # Initialisation de la session
    if 'page' not in st.session_state:
        st.session_state.page = "accueil"
    
    # Sidebar
    with st.sidebar:
        display_logo(size="120px")
        st.markdown('<div style="text-align: center;"><h2>HCM VOYAGES</h2></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Menu de navigation
        pages = [
            ("🏠", "Accueil", "accueil"),
            ("🌍", "Destinations", "destinations"),
            ("📝", "Réservation", "reservation"),
            ("📋", "Visas", "visas"),
            ("📋", "Demande de Visa", "demande-visa"),
            ("🇩🇿", "Discover Algeria", "discover-algeria"),
            ("📞", "Contact", "contact"),
            ("⚙️", "Administration", "admin"),
        ]
        
        for icon, label, page_id in pages:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page_id}"):
                st.session_state.page = page_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; font-size: 0.8em; color: white;">
                © 2024 HCM Voyages<br>
                Tous droits réservés
            </div>
        """, unsafe_allow_html=True)
    
    # Routage des pages
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "destinations":
        page_destinations()
    elif st.session_state.page == "reservation":
        page_reservation()
    elif st.session_state.page == "visas":
        page_visas()
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
