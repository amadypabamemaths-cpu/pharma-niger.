import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ------------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE & STYLES CSS
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="PharmaNiger - Pharmacies & Médicaments",
    page_icon="🟢",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* En-tête principal */
    .header-banner {
        background-color: #2b9348;
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: bold;
        font-size: 22px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Substituts de Logos personnalisés en CSS */
    .logo-badge-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }
    .logo-badge-flag {
        background-color: #e07a5f;
        color: white;
        font-size: 28px;
        padding: 10px 18px;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
    .logo-badge-pharma {
        background-color: #2b9348;
        color: white;
        font-size: 28px;
        padding: 10px 18px;
        border-radius: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }

    /* Cartes d'affichage */
    .pharma-card {
        background-color: #ffffff;
        border-left: 6px solid #2b9348;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        border-top: 1px solid #f0f0f0;
        border-right: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;
    }
    .commune-badge {
        background-color: #005f73;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        float: right;
    }
    .status-garde {
        background-color: #2b9348;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .date-badge {
        background-color: #e76f51;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
        display: inline-block;
        margin-bottom: 15px;
    }
    .med-price {
        color: #d97706;
        font-weight: bold;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# INITIALISATION DES DATES, BASE DE DONNÉES ET CHATBOT
# ------------------------------------------------------------------------------
if "date_debut_garde" not in st.session_state:
    st.session_state.date_debut_garde = date.today()
if "date_fin_garde" not in st.session_state:
    st.session_state.date_fin_garde = date.today() + timedelta(days=7)

# Initialisation de l'historique du chatbot
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Bonjour ! Je suis **PharmaBot**. Posez-moi vos questions sur les pharmacies de garde ou les médicaments au Niger !"}
    ]

if "pharmacies_db" not in st.session_state:
    st.session_state.pharmacies_db = [
        {"id": 1, "commune": "COMMUNE I", "nom": "7 THERAPIES", "adresse": "Koubia", "tel": "20 73 68 58", "est_de_garde": True},
        {"id": 2, "commune": "COMMUNE I", "nom": "AMINA", "adresse": "RECASEMENT", "tel": "80 94 99 09", "est_de_garde": True},
        {"id": 17, "commune": "COMMUNE II", "nom": "AS SAMAD", "adresse": "Pas loin de l'Institut HARISSON", "tel": "95 84 00 78", "est_de_garde": True},
        {"id": 21, "commune": "COMMUNE III", "nom": "ANY KOIRA", "adresse": "Face assurance LEYMA", "tel": "20 73 50 83", "est_de_garde": True},
        {"id": 31, "commune": "COMMUNE IV", "nom": "AFZAL", "adresse": "Avenue des ARMEES", "tel": "87 87 57 87", "est_de_garde": True},
        {"id": 39, "commune": "COMMUNE V", "nom": "LAMORDE", "adresse": "Derrière l'Ex CHU LAMORDE", "tel": "92 19 80 95", "est_de_garde": True}
    ]

if "meds_db" not in st.session_state:
    st.session_state.meds_db = [
        {"nom": "PARACETAMOL 500MG CPR B/20", "prix_fcfa": 500, "notice": "Traitement des douleurs légères à modérées et de la fièvre."},
        {"nom": "IBUPROFENE 400MG CPR B/20", "prix_fcfa": 1100, "notice": "Anti-inflammatoire. Douleurs et maux de tête."},
        {"nom": "ARTEMETHER + LUMEFANTRINE 80/480MG", "prix_fcfa": 1800, "notice": "Traitement du paludisme simple."}
    ]

if "page" not in st.session_state:
    st.session_state.page = "Accueil"

# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 50px;">🇳🇪 ⚕️</span>
        <h2 style="color:#2b9348; margin:0;">PharmaNiger</h2>
        <p style="font-size:12px; color:#666;">Pharmacies de Garde au Niger</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🏠 Menu d'Accueil", use_container_width=True):
        st.session_state.page = "Accueil"
        st.rerun()

    if st.button("💬 Assistant PharmaBot", use_container_width=True):
        st.session_state.page = "Chatbot"
        st.rerun()

    if st.button("⚙️ Mise à jour de la Garde", use_container_width=True):
        st.session_state.page = "Mise à jour de la Garde"
        st.rerun()

# ------------------------------------------------------------------------------
# PAGE : ACCUEIL
# ------------------------------------------------------------------------------
if st.session_state.page == "Accueil":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <div class="logo-badge-container">
            <div class="logo-badge-flag">🇳🇪</div>
            <div class="logo-badge-pharma">⚕️</div>
        </div>
        <h2 style="color: #2b9348; margin-top: 10px; font-weight: bold;">PharmaNiger</h2>
        <p style="color: #555; font-size: 15px;">Pharmacies de Garde & Guide des Médicaments au Niger</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header-banner">Menu d\'Accueil</div>', unsafe_allow_html=True)
    
    if st.button("🟢 Pharmacies de Garde", use_container_width=True):
        st.session_state.page = "Pharmacies de Garde"
        st.rerun()
        
    if st.button("💊 Prix des Médicaments", use_container_width=True):
        st.session_state.page = "Prix des Médicaments"
        st.rerun()

    if st.button("🏥 Toutes les Pharmacies", use_container_width=True):
        st.session_state.page = "Toutes les Pharmacies"
        st.rerun()

    if st.button("🩺 Conseils Médicaux", use_container_width=True):
        st.session_state.page = "Conseils Médicaux"
        st.rerun()

    if st.button("🤖 A propos de l'auteur...", use_container_width=True):
        st.session_state.page = "A propos de l'auteur..."
        st.rerun()

    st.markdown("<br><br><p style='text-align: center; color: #888; font-size: 13px;'>© Application Réalisée par Amady - Ministère de la Santé Publique</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE : CHATBOT (PHARMABOT)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Chatbot":
    st.markdown('<div class="header-banner">💬 Assistant PharmaBot</div>', unsafe_allow_html=True)
    
    # Afficher l'historique des messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Champ de saisie utilisateur
    if prompt := st.chat_input("Posez votre question (ex: 'pharmacie de garde', 'prix doliprane')..."):
        # Afficher le message de l'utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Logique de réponse basique du Chatbot
        prompt_lower = prompt.lower()
        reponse_bot = "Désolé, je n'ai pas bien compris. Vous pouvez me poser des questions sur les **pharmacies de garde**, les **prix des médicaments**, ou les **urgences**."

        if "garde" in prompt_lower or "pharmacie" in prompt_lower:
            nb_gardes = len([p for p in st.session_state.pharmacies_db if p["est_de_garde"]])
            reponse_bot = f"Il y a actuellement **{nb_gardes} pharmacies de garde**. Vous pouvez consulter la liste complète et chercher par commune dans la section **Pharmacies de Garde** depuis le Menu d'Accueil."
        
        elif "prix" in prompt_lower or "médicament" in prompt_lower or "notice" in prompt_lower:
            reponse_bot = "Pour vérifier le prix ou la notice d'un médicament, veuillez vous rendre dans la section **Prix des Médicaments** du Menu d'Accueil. Vous y trouverez une barre de recherche rapide."
            
        elif "urgence" in prompt_lower or "samu" in prompt_lower or "pompier" in prompt_lower:
            reponse_bot = "🚨 **Numéros d'urgence au Niger :**\n- SAMU : **15**\n- Sapeurs-Pompiers : **18**\n- Police Secours : **17**"
            
        elif "bonjour" in prompt_lower or "salut" in prompt_lower:
            reponse_bot = "Bonjour ! Comment puis-je vous aider aujourd'hui concernant la santé au Niger ?"

        # Afficher la réponse du bot
        with st.chat_message("assistant"):
            st.markdown(reponse_bot)
        st.session_state.chat_messages.append({"role": "assistant", "content": reponse_bot})

# ------------------------------------------------------------------------------
# PAGE : PHARMACIES DE GARDE (ORGANISÉES PAR DATE)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Pharmacies de Garde":
    st.markdown('<div class="header-banner">PHARMACIES DE GARDE - NIAMEY</div>', unsafe_allow_html=True)
    
    d_deb = st.session_state.date_debut_garde.strftime("%d/%m/%Y")
    d_fin = st.session_state.date_fin_garde.strftime("%d/%m/%Y")
    
    st.markdown(f'<div style="text-align:center;"><span class="date-badge">📅 Garde du : {d_deb} au {d_fin}</span></div>', unsafe_allow_html=True)
    
    gardes_actives = [p for p in st.session_state.pharmacies_db if p.get("est_de_garde", True)]
    
    communes = ["Toutes les Communes", "COMMUNE I", "COMMUNE II", "COMMUNE III", "COMMUNE IV", "COMMUNE V"]
    filtre_commune = st.selectbox("📌 Filtrer par Commune :", communes)
    search = st.text_input("🔍 Rechercher une pharmacie ou une adresse...", "")
    
    pharma_filtrees = gardes_actives
    if filtre_commune != "Toutes les Communes":
        pharma_filtrees = [p for p in pharma_filtrees if p["commune"] == filtre_commune]
    if search:
        pharma_filtrees = [p for p in pharma_filtrees if search.lower() in p["nom"].lower() or search.lower() in p["adresse"].lower()]

    st.write(f"<b>{len(pharma_filtrees)}</b> pharmacie(s) actuellement de garde", unsafe_allow_html=True)
    
    for p in pharma_filtrees:
        st.markdown(f"""
        <div class="pharma-card">
            <span class="commune-badge">{p['commune']}</span>
            <h4 style="color: #2b9348; margin: 0;">🏥 PHARMACIE {p['nom']} <span class="status-garde">EN GARDE</span></h4>
            <p style="margin: 4px 0;">📍 <b>Localisation :</b> {p['adresse']}</p>
            <p style="margin: 2px 0;">📞 <b>Téléphone :</b> <a href="tel:+227{str(p['tel']).replace(' ', '')}" style="color: #005f73; font-weight: bold;">+227 {p['tel']}</a></p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE : MISE À JOUR DE LA GARDE
# ------------------------------------------------------------------------------
elif st.session_state.page == "Mise à jour de la Garde":
    st.markdown('<div class="header-banner">⚙️ Mise à jour & Importation de la Garde</div>', unsafe_allow_html=True)
    
    st.subheader("📅 1. Définir la période de garde")
    col1, col2 = st.columns(2)
    with col1:
        new_d_deb = st.date_input("Date de début de garde", value=st.session_state.date_debut_garde)
    with col2:
        new_d_fin = st.date_input("Date de fin de garde", value=st.session_state.date_fin_garde)
    
    if st.button("Mettre à jour la période", use_container_width=True):
        st.session_state.date_debut_garde = new_d_deb
        st.session_state.date_fin_garde = new_d_fin
        st.success("Période de garde mise à jour !")
        st.rerun()

    st.markdown("---")

    st.subheader("📥 2. Importer la nouvelle liste des pharmacies de garde")
    uploaded_file = st.file_uploader("Choisir le nouveau fichier de la pharmacie de garde", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_new = pd.read_csv(uploaded_file)
            else:
                df_new = pd.read_excel(uploaded_file)
                
            st.dataframe(df_new.head())
            
            if st.button("✅ Valider et appliquer", use_container_width=True):
                st.session_state.pharmacies_db = df_new.to_dict(orient="records")
                st.success("La liste a été mise à jour avec succès !")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

# ------------------------------------------------------------------------------
# AUTRES PAGES : PRIX, TOUTES LES PHARMA, CONSEILS, AUTEUR
# ------------------------------------------------------------------------------
elif st.session_state.page == "Prix des Médicaments":
    st.markdown('<div class="header-banner">Prix des Médicaments au Niger</div>', unsafe_allow_html=True)
    q = st.text_input("Recherche rapide (ex: paracetamol)...", "")
    meds = st.session_state.meds_db
    if q:
        meds = [m for m in meds if q.lower() in m['nom'].lower()]
    for m in meds:
        st.markdown(f"""
        <div class="pharma-card">
            <h4 style="color: #2b9348; margin:0;">💊 {m['nom']}</h4>
            <p class="med-price" style="margin: 4px 0;">Prix : {m['prix_fcfa']} FCFA</p>
            <p style="margin:0; font-size: 13px; color: #555;"><b>Notice :</b> {m['notice']}</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Toutes les Pharmacies":
    st.markdown('<div class="header-banner">Toutes les Pharmacies du Niger</div>', unsafe_allow_html=True)
    df_pharma = pd.DataFrame(st.session_state.pharmacies_db)
    st.dataframe(df_pharma, use_container_width=True, hide_index=True)

elif st.session_state.page == "Conseils Médicaux":
    st.markdown('<div class="header-banner">Conseils Médicaux & Précautions</div>', unsafe_allow_html=True)
    st.markdown("""
    1. **Hydratation :** Consommez au moins 2,5 à 3 litres d'eau potable par jour.
    2. **Prévention du Paludisme :** Utilisez des moustiquaires imprégnées d'insecticide.
    3. **Numéros d'Urgence :** SAMU : **15** | Sapeurs-Pompiers : **18**
    """)

elif st.session_state.page == "A propos de l'auteur...":
    st.markdown('<div class="header-banner">A propos de l\'auteur</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 60px;">🇳🇪 👨‍💻</span><br><br>
        <h3 style="color:#2b9348;">Application PharmaNiger</h3>
        <p style="font-size: 16px;"><b>Auteur & Développeur :</b> Amady Pabame</p>
        <p style="font-size: 15px; color: #555;"><b>Spécialité :</b> Doctorant en Mathématiques & Intelligence Artificielle</p>
        <hr style="width:50%; margin: 20px auto;">
        <p style="font-size: 13px; color: #777;">Développé avec Python & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)