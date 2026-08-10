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
# INITIALISATION DES DATES ET DE LA BASE DE DONNÉES
# ------------------------------------------------------------------------------
if "date_debut_garde" not in st.session_state:
    st.session_state.date_debut_garde = date.today()
if "date_fin_garde" not in st.session_state:
    st.session_state.date_fin_garde = date.today() + timedelta(days=7)

if "pharmacies_db" not in st.session_state:
    st.session_state.pharmacies_db = [
        # COMMUNE I
        {"id": 1, "commune": "COMMUNE I", "nom": "7 THERAPIES", "adresse": "Koubia (face du garage L'AVENIR)", "tel": "20 73 68 58", "est_de_garde": True},
        {"id": 2, "commune": "COMMUNE I", "nom": "AMINA", "adresse": "RECASEMENT, côté du Rond-Point PNEU", "tel": "80 94 99 09", "est_de_garde": True},
        {"id": 3, "commune": "COMMUNE I", "nom": "ASKIA", "adresse": "BOUKOKI, Boulevard KAOCEN", "tel": "21 31 59 04", "est_de_garde": True},
        {"id": 4, "commune": "COMMUNE I", "nom": "CHATEAU BI", "adresse": "KALLEY-PLATEAU", "tel": "91 91 04 29", "est_de_garde": True},
        {"id": 5, "commune": "COMMUNE I", "nom": "CHATEAU I", "adresse": "Plateau, A côté de BAKLINI", "tel": "20 72 27 77", "est_de_garde": True},
        {"id": 6, "commune": "COMMUNE I", "nom": "DES CAMPS", "adresse": "Face au Camps de la Garde Nationale", "tel": "20 75 53 00", "est_de_garde": True},
        {"id": 7, "commune": "COMMUNE I", "nom": "DIASPORA", "adresse": "Quartier Diaspora à côté du château R 17", "tel": "99 36 83 83", "est_de_garde": True},
        {"id": 8, "commune": "COMMUNE I", "nom": "FASSA", "adresse": "A côté de la station PETROBA", "tel": "91 74 12 71", "est_de_garde": False},
        {"id": 9, "commune": "COMMUNE I", "nom": "GAPTCHI", "adresse": "Sur le goudron de BEDIR en face Station OLA", "tel": "90 09 66 56", "est_de_garde": True},
        {"id": 10, "commune": "COMMUNE I", "nom": "GOBI", "adresse": "Koira-Kano en face du CEG 14", "tel": "80 06 31 26", "est_de_garde": True},
        {"id": 11, "commune": "COMMUNE I", "nom": "GOROUAL", "adresse": "Bobiel, Devant la FENIFOOT", "tel": "96 33 71 76", "est_de_garde": True},
        {"id": 12, "commune": "COMMUNE I", "nom": "KARMA", "adresse": "Référence (Face Château Vert R14)", "tel": "97 36 33 08", "est_de_garde": True},
        {"id": 13, "commune": "COMMUNE I", "nom": "NIAMEY NYALA", "adresse": "Ryad, Pas loin de Plaque AVOCAT", "tel": "88 01 05 07", "est_de_garde": True},
        {"id": 14, "commune": "COMMUNE I", "nom": "PLATEAU 2", "adresse": "En face de l'HOPITAL NIGERO-TURC", "tel": "80 06 54 15", "est_de_garde": True},
        {"id": 15, "commune": "COMMUNE I", "nom": "REFERENCE", "adresse": "Non loin de l'Hôpital de Référence", "tel": "20 35 22 64", "est_de_garde": True},
        {"id": 16, "commune": "COMMUNE I", "nom": "SANTE PLUS", "adresse": "Face CSI-MATERNITE BOBIEL", "tel": "80 06 78 25", "est_de_garde": True},

        # COMMUNE II
        {"id": 17, "commune": "COMMUNE II", "nom": "AS SAMAD", "adresse": "Pas loin de l'Institut HARISSON", "tel": "95 84 00 78", "est_de_garde": True},
        {"id": 18, "commune": "COMMUNE II", "nom": "CITE CAISSE", "adresse": "Marché CITE CAISSE", "tel": "90 19 45 37", "est_de_garde": True},
        {"id": 19, "commune": "COMMUNE II", "nom": "MUTUALISE", "adresse": "En face de Sapeur-Pompier LAZARET", "tel": "92 19 13 96", "est_de_garde": True},
        {"id": 20, "commune": "COMMUNE II", "nom": "SABO", "adresse": "Face à la grande Mosquée FERAILLE", "tel": "91 24 97 96", "est_de_garde": True},

        # COMMUNE III
        {"id": 21, "commune": "COMMUNE III", "nom": "ANY KOIRA", "adresse": "Face assurance LEYMA bâtiment ANY KOIRA", "tel": "20 73 50 83", "est_de_garde": True},
        {"id": 22, "commune": "COMMUNE III", "nom": "BONKANEY", "adresse": "Pas loin de STM SIEGE", "tel": "20 36 36 70", "est_de_garde": True},
        {"id": 23, "commune": "COMMUNE III", "nom": "CITE FAYÇAL", "adresse": "Cité Fayçal, A côté du Rond-Point WAZIRI", "tel": "89 14 88 55", "est_de_garde": True},
        {"id": 24, "commune": "COMMUNE III", "nom": "DAN GAO", "adresse": "A côté de la Pâtisserie MARHABA", "tel": "20 74 03 36", "est_de_garde": True},
        {"id": 25, "commune": "COMMUNE III", "nom": "GRAND MARCHE", "adresse": "A côté de NIAMEY STORE", "tel": "75 03 98 25", "est_de_garde": True},
        {"id": 26, "commune": "COMMUNE III", "nom": "GRANDE MOSQUEE", "adresse": "Kalley-Est, Face AL IZZA SIEGE", "tel": "88 88 30 88", "est_de_garde": True},
        {"id": 27, "commune": "COMMUNE III", "nom": "KAWSAR", "adresse": "Cité DEPUTES, Face Ecole KOIREY", "tel": "99 12 49 99", "est_de_garde": True},
        {"id": 28, "commune": "COMMUNE III", "nom": "LE REMEDE", "adresse": "Banifondou 2, Rond-Point KOKORBA 1", "tel": "80 06 53 51", "est_de_garde": True},
        {"id": 29, "commune": "COMMUNE III", "nom": "NASSARA", "adresse": "Poudrière, côté Institut Africain Management", "tel": "76 27 28 17", "est_de_garde": True},
        {"id": 30, "commune": "COMMUNE III", "nom": "NOUR", "adresse": "A côté de la Station TILBA", "tel": "80 07 27 66", "est_de_garde": True},

        # COMMUNE IV
        {"id": 31, "commune": "COMMUNE IV", "nom": "AFZAL", "adresse": "Avenue des ARMEES sur le Pavé de GAMKALLEY", "tel": "87 87 57 87", "est_de_garde": True},
        {"id": 32, "commune": "COMMUNE IV", "nom": "AL FORMA", "adresse": "Niamey 2000, Rond-Point FARKEY BI", "tel": "80 06 69 22", "est_de_garde": True},
        {"id": 33, "commune": "COMMUNE IV", "nom": "BASSORA", "adresse": "En face de TALLADJE TOURAKOU", "tel": "90 45 44 46", "est_de_garde": True},
        {"id": 34, "commune": "COMMUNE IV", "nom": "CITE ASECNA", "adresse": "Aéroport, Derrière le CEG REPERE", "tel": "96 99 35 01", "est_de_garde": True},
        {"id": 35, "commune": "COMMUNE IV", "nom": "JOURIYA", "adresse": "Niamey 2000, Station PETROBA 3e Latérite", "tel": "93 88 57 69", "est_de_garde": True},
        {"id": 36, "commune": "COMMUNE IV", "nom": "MARIAM", "adresse": "Niamey 2000, Face Station OLA vers Commissariat", "tel": "90 78 59 20", "est_de_garde": True},
        {"id": 37, "commune": "COMMUNE IV", "nom": "ROUTE DOSSO", "adresse": "Aéroport, Sur la Route DOSSO avant BIENVENUE", "tel": "89 74 49 32", "est_de_garde": True},
        {"id": 38, "commune": "COMMUNE IV", "nom": "TADJEJE", "adresse": "Aéroport, A côté Alimentation ROUTE TCHANGA", "tel": "80 07 53 93", "est_de_garde": True},

        # COMMUNE V
        {"id": 39, "commune": "COMMUNE V", "nom": "LAMORDE", "adresse": "Derrière l'Ex CHU LAMORDE", "tel": "92 19 80 95", "est_de_garde": True},
        {"id": 40, "commune": "COMMUNE V", "nom": "LIPTAKO", "adresse": "Immeuble LIPTAKO face CAREN ASSURANCE", "tel": "20 31 51 20", "est_de_garde": True},
        {"id": 41, "commune": "COMMUNE V", "nom": "NORDIRE", "adresse": "A 100 mètres Station BAZAGOR NORDIRE", "tel": "80 07 27 73", "est_de_garde": True},
        {"id": 42, "commune": "COMMUNE V", "nom": "SAGUIA", "adresse": "Au niveau du Rond-Point SAGUIA", "tel": "80 96 00 93", "est_de_garde": True}
    ]

if "meds_db" not in st.session_state:
    st.session_state.meds_db = [
        {"nom": "PARACETAMOL 500MG CPR B/20", "prix_fcfa": 500, "notice": "Traitement des douleurs légères à modérées et de la fièvre."},
        {"nom": "PARACETAMOL 1000MG (EFFERVESCENT) B/8", "prix_fcfa": 1200, "notice": "Soulagement des douleurs intenses et états fiévreux."},
        {"nom": "IBUPROFENE 400MG CPR B/20", "prix_fcfa": 1100, "notice": "Anti-inflammatoire. Douleurs et maux de tête."},
        {"nom": "ARTEMETHER + LUMEFANTRINE 80/480MG", "prix_fcfa": 1800, "notice": "Traitement du paludisme simple."},
        {"nom": "COARTEM 20/120MG COMPRIMES", "prix_fcfa": 2200, "notice": "Traitement antipaludique."},
        {"nom": "AMOXICILLINE 500MG GEL B/12", "prix_fcfa": 1500, "notice": "Antibiotique pour infections respiratoires et urinaires."},
        {"nom": "AUGMENTIN 1G CPR B/14", "prix_fcfa": 5200, "notice": "Antibiotique à large spectre."},
        {"nom": "VITASCORBOL 500MG SS CPR 2T/12", "prix_fcfa": 2615, "notice": "Vitamine C. Indiqué dans la fatigue passagère."},
        {"nom": "VITATHION GLE EFFV SACH BT 20", "prix_fcfa": 4105, "notice": "Tonique général et anti-asthénique."},
        {"nom": "SPASFON CPR B/30", "prix_fcfa": 2100, "notice": "Traitement des douleurs spasmodiques intestinales."}
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

    if st.button("📄 Notice des Médicaments", use_container_width=True):
        st.session_state.page = "Notice des Médicaments"
        st.rerun()

    if st.button("⭐ Notez l'Application...", use_container_width=True):
        st.toast("Merci pour votre note 5 étoiles ! ⭐⭐⭐⭐⭐")

    if st.button("🤖 A propos de l'auteur...", use_container_width=True):
        st.session_state.page = "A propos de l'auteur..."
        st.rerun()

    st.markdown("<br><br><p style='text-align: center; color: #888; font-size: 13px;'>© Application Réalisée par Amady - Ministère de la Santé Publique</p>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE : PHARMACIES DE GARDE (ORGANISÉES PAR DATE)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Pharmacies de Garde":
    st.markdown('<div class="header-banner">PHARMACIES DE GARDE - NIAMEY</div>', unsafe_allow_html=True)
    
    # Affichage de la plage de dates
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
# PAGE : MISE À JOUR DE LA GARDE (PAR DATE + IMPORTATION DE FICHIER)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Mise à jour de la Garde":
    st.markdown('<div class="header-banner">⚙️ Mise à jour & Importation de la Garde</div>', unsafe_allow_html=True)
    
    # 1. Ajustement de la période de garde
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

    # 2. Importation d'un nouveau fichier de garde
    st.subheader("📥 2. Importer la nouvelle liste des pharmacies de garde")
    st.write("Téléversez un fichier **CSV** ou **Excel (.xlsx)** pour mettre à jour la liste complète.")
    
    uploaded_file = st.file_uploader("Choisir le nouveau fichier de la pharmacie de garde", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_new = pd.read_csv(uploaded_file)
            else:
                df_new = pd.read_excel(uploaded_file)
                
            st.write("Aperçu du fichier téléversé :")
            st.dataframe(df_new.head())
            
            if st.button("✅ Valider et appliquer ce nouveau fichier", use_container_width=True):
                st.session_state.pharmacies_db = df_new.to_dict(orient="records")
                st.success("La liste des pharmacies de garde a été mise à jour avec succès !")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

    st.markdown("---")

    # 3. Modification rapide individuelle
    st.subheader("✏️ 3. Sélection rapide des pharmacies de garde")
    df_p = pd.DataFrame(st.session_state.pharmacies_db)
    edited_df = st.data_editor(
        df_p[["id", "commune", "nom", "adresse", "tel", "est_de_garde"]],
        column_config={
            "est_de_garde": st.column_config.CheckboxColumn("De Garde ?", default=False)
        },
        disabled=["id", "commune", "nom", "adresse", "tel"],
        use_container_width=True,
        hide_index=True
    )
    if st.button("💾 Enregistrer la sélection rapide", use_container_width=True):
        st.session_state.pharmacies_db = edited_df.to_dict(orient="records")
        st.success("Modifications enregistrées !")
        st.rerun()

# ------------------------------------------------------------------------------
# PAGE : PRIX DES MÉDICAMENTS
# ------------------------------------------------------------------------------
elif st.session_state.page == "Prix des Médicaments":
    st.markdown('<div class="header-banner">Prix des Médicaments au Niger</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 Rechercher / Consulter", "➕ Ajouter un Médicament"])

    with tab1:
        q = st.text_input("Recherche rapide (ex: paracetamol, amoxicilline...)", "")
        meds = st.session_state.meds_db
        if q:
            meds = [m for m in meds if q.lower() in m['nom'].lower()]
        
        for m in meds:
            prix_eur = round(m['prix_fcfa'] / 655.957, 2)
            st.markdown(f"""
            <div class="pharma-card">
                <h4 style="color: #2b9348; margin:0;">💊 {m['nom']}</h4>
                <p class="med-price" style="margin: 4px 0;">Prix : {m['prix_fcfa']} FCFA <span style="color:#666; font-size:13px;">(~ {prix_eur} €)</span></p>
                <p style="margin:0; font-size: 13px; color: #555;"><b>Notice :</b> {m['notice']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.subheader("➕ Ajouter un nouveau médicament")
        with st.form("form_add_med"):
            nouveau_nom = st.text_input("Nom commercial & Dosage")
            nouveau_prix = st.number_input("Prix en FCFA", min_value=50, step=50, value=1000)
            nouvelle_notice = st.text_area("Notice / Indications")
            
            submit_add = st.form_submit_button("Enregistrer")
            if submit_add and nouveau_nom:
                st.session_state.meds_db.append({
                    "nom": nouveau_nom.upper(),
                    "prix_fcfa": int(nouveau_prix),
                    "notice": nouvelle_notice
                })
                st.success(f"Médicament {nouveau_nom.upper()} ajouté !")
                st.rerun()

# ------------------------------------------------------------------------------
# PAGE : TOUTES LES PHARMACIES
# ------------------------------------------------------------------------------
elif st.session_state.page == "Toutes les Pharmacies":
    st.markdown('<div class="header-banner">Toutes les Pharmacies du Niger</div>', unsafe_allow_html=True)
    
    df_pharma = pd.DataFrame(st.session_state.pharmacies_db)
    st.dataframe(
        df_pharma[["commune", "nom", "adresse", "tel", "est_de_garde"]],
        column_config={
            "commune": "Commune",
            "nom": "Nom de la Pharmacie",
            "adresse": "Adresse",
            "tel": "Téléphone",
            "est_de_garde": "De Garde ?"
        },
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------------------------------------------
# PAGE : CONSEILS MÉDICAUX
# ------------------------------------------------------------------------------
elif st.session_state.page == "Conseils Médicaux":
    st.markdown('<div class="header-banner">Conseils Médicaux & Précautions</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🩺 Recommandations Sanitaires (Niger)
    
    1. **Hydratation :** En période de forte chaleur au Niger, consommez au moins 2,5 à 3 litres d'eau potable par jour.
    2. **Prévention du Paludisme :** Utilisez des moustiquaires imprégnées d'insecticide et consultez en pharmacie dès l'apparition de fièvre.
    3. **Automédication :** Ne prenez pas d'antibiotiques sans avis médical ou ordonnance délivrée par un professionnel de santé.
    4. **Numéros d'Urgence :**
       * SAMU Niger : **15**
       * Sapeurs-Pompiers : **18**
    """)

# ------------------------------------------------------------------------------
# PAGE : NOTICE DES MÉDICAMENTS
# ------------------------------------------------------------------------------
elif st.session_state.page == "Notice des Médicaments":
    st.markdown('<div class="header-banner">Notices & Posologies des Médicaments</div>', unsafe_allow_html=True)
    
    noms_meds = [m['nom'] for m in st.session_state.meds_db]
    selected_med = st.selectbox("Choisissez un médicament :", noms_meds)
    
    med_obj = next((m for m in st.session_state.meds_db if m['nom'] == selected_med), None)
    
    if med_obj:
        st.markdown(f"""
        <div class="pharma-card">
            <h3 style="color:#2b9348;">📄 NOTICE : {med_obj['nom']}</h3>
            <hr>
            <p><b>Prix Officiel :</b> <span class="med-price">{med_obj['prix_fcfa']} FCFA</span></p>
            <p><b>Indications & Posologie :</b></p>
            <p style="background-color:#f9f9f9; padding:10px; border-radius:5px;">{med_obj['notice']}</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PAGE : A PROPOS DE L'AUTEUR (MODIFIÉE)
# ------------------------------------------------------------------------------
elif st.session_state.page == "A propos de l'auteur...":
    st.markdown('<div class="header-banner">A propos de l\'auteur</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 60px;">🇳🇪 👨‍💻</span><br><br>
        <h3 style="color:#2b9348;">Application PharmaNiger</h3>
        <p style="font-size: 16px;"><b>Auteur & Développeur :</b> Amady Pabame</p>
        <p style="font-size: 15px; color: #555;"><b>Spécialité :</b> Doctorant en Mathématiques & Intelligence Artificielle (Data Science appliquée)</p>
        <hr style="width:50%; margin: 20px auto;">
        <p style="font-size: 13px; color: #777;">Développé avec Python & Streamlit pour la santé publique au Niger</p>
    </div>
    """, unsafe_allow_html=True)