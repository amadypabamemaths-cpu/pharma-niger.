import streamlit as st
import pandas as pd
from datetime import date, timedelta
import webbrowser
import requests
from bs4 import BeautifulSoup
import re
import io
import json
import os

# ==============================================================================
# CONFIGURATION DE LA PAGE
# ==============================================================================
st.set_page_config(
    page_title="PharmaNiger Pro",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PERSISTANCE DES FAVORIS (fichier JSON)
# ==============================================================================
FAVORIS_FILE = "favoris.json"

def load_favoris():
    try:
        with open(FAVORIS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_favoris(favoris):
    with open(FAVORIS_FILE, "w") as f:
        json.dump(favoris, f)

# ==============================================================================
# INITIALISATION DES ÉTATS DE SESSION
# ==============================================================================
if "page" not in st.session_state:
    st.session_state.page = "Accueil"
if "date_debut_garde" not in st.session_state:
    st.session_state.date_debut_garde = date.today()
if "date_fin_garde" not in st.session_state:
    st.session_state.date_fin_garde = date.today() + timedelta(days=7)
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Bonjour ! Je suis **PharmaBot**. Posez-moi vos questions sur les médicaments, les posologies, les pharmacies ou la santé au Niger !"}
    ]
if "favoris" not in st.session_state:
    st.session_state.favoris = load_favoris()
if "theme" not in st.session_state:
    st.session_state.theme = "clair"
if "ville_filter" not in st.session_state:
    st.session_state.ville_filter = "Toutes les villes"
if "commune_filter" not in st.session_state:
    st.session_state.commune_filter = "Toutes les Communes"

# ==============================================================================
# DONNÉES : MÉDICAMENTS (102 entrées)
# ==============================================================================
if "meds_db" not in st.session_state:
    st.session_state.meds_db = [
        # === ANTALGIQUES & ANTIPYRÉTIQUES (9) ===
        {"nom": "PARACETAMOL 500MG CPR B/20", "categorie": "Antalgiques", "prix_fcfa": 500,
         "indications": "Douleurs d'intensité légère à modérée et fièvre.",
         "posologie_adulte": "1 à 2 comprimés (500-1000 mg) toutes les 6h, max 4g/jour.",
         "posologie_enfant": "15 mg/kg toutes les 6h (max 60 mg/kg/jour).",
         "contre_indications": "Insuffisance hépatique sévère, allergie."},
        {"nom": "DOLIPRANE 1000MG CPR B/8", "categorie": "Antalgiques", "prix_fcfa": 1500,
         "indications": "Douleurs intenses et états fébriles.",
         "posologie_adulte": "1 comprimé (1000 mg) toutes les 6-8h, max 3g/jour.",
         "posologie_enfant": "Non recommandé chez l'enfant de moins de 50 kg.",
         "contre_indications": "Insuffisance hépatique, allergie."},
        {"nom": "ASPIRINE UPSA 500MG", "categorie": "Antalgiques", "prix_fcfa": 1000,
         "indications": "Douleurs, fièvre, inflammations (rhumatismes).",
         "posologie_adulte": "1 comprimé (500 mg) 3-4 fois/jour (max 3g/jour).",
         "posologie_enfant": "À éviter chez l'enfant de moins de 12 ans (risque de syndrome de Reye).",
         "contre_indications": "Ulcère gastroduodénal, allergie aux salicylés, hémophilie."},
        {"nom": "IBUPROFENE 400MG CPR B/20", "categorie": "Antalgiques", "prix_fcfa": 1100,
         "indications": "Maux de tête, douleurs dentaires, règles douloureuses, arthrite.",
         "posologie_adulte": "1 comprimé (400 mg) 3 fois/jour (max 1200 mg/jour).",
         "posologie_enfant": "20-30 mg/kg/jour en 2-3 prises.",
         "contre_indications": "Ulcère, insuffisance rénale sévère, allergie aux AINS."},
        {"nom": "DICLOFENAC 50MG CPR", "categorie": "Antalgiques", "prix_fcfa": 1000,
         "indications": "Douleurs articulaires, rhumatismes, lombalgies.",
         "posologie_adulte": "1 comprimé (50 mg) 2-3 fois/jour.",
         "posologie_enfant": "Non recommandé chez l'enfant de moins de 14 ans.",
         "contre_indications": "Ulcère, insuffisance rénale, allergie aux AINS."},
        {"nom": "EFFERALGAN 500MG CPR", "categorie": "Antalgiques", "prix_fcfa": 1200,
         "indications": "Douleurs et fièvre.",
         "posologie_adulte": "1 comprimé 3 fois/jour.",
         "posologie_enfant": "15 mg/kg 3 fois/jour.",
         "contre_indications": "Insuffisance hépatique."},
        {"nom": "PONSTYL 500MG CPR", "categorie": "Antalgiques", "prix_fcfa": 2200,
         "indications": "Douleurs dentaires, règles douloureuses, arthralgies.",
         "posologie_adulte": "1 comprimé (500 mg) 3 fois/jour.",
         "posologie_enfant": "25 mg/kg/jour en 2-3 prises.",
         "contre_indications": "Ulcère, insuffisance rénale."},
        {"nom": "KARDEGIC 100MG CPR", "categorie": "Antalgiques", "prix_fcfa": 1200,
         "indications": "Prévention des accidents thrombotiques.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Ulcère, allergie à l'aspirine."},
        {"nom": "VOLTARENE 50MG CPR", "categorie": "Antalgiques", "prix_fcfa": 1500,
         "indications": "Douleurs inflammatoires.",
         "posologie_adulte": "1 comprimé 2-3 fois/jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Ulcère, insuffisance rénale."},
        # === ANTIPALUDÉENS (4) ===
        {"nom": "ARTEMETHER + LUMEFANTRINE 80/480MG", "categorie": "Antipaludéens", "prix_fcfa": 1800,
         "indications": "Paludisme non compliqué (adulte et enfant > 5kg).",
         "posologie_adulte": "2 comprimés en une prise, 2 fois/jour pendant 3 jours.",
         "posologie_enfant": "Selon poids (5-14kg:1; 15-24kg:2; 25-34kg:3) 2 fois/jour 3 jours.",
         "contre_indications": "Allergie aux dérivés de l'artémisinine, 1er trimestre grossesse."},
        {"nom": "COARTEM 20/120MG CPR", "categorie": "Antipaludéens", "prix_fcfa": 2200,
         "indications": "Paludisme à P. falciparum.",
         "posologie_adulte": "6 comprimés en une prise, 2 fois/jour pendant 3 jours.",
         "posologie_enfant": "Selon poids (5-14kg:1; 15-24kg:2; etc.) 2 fois/jour.",
         "contre_indications": "Allergie à l'artéméther ou à la luméfantrine."},
        {"nom": "QUININE 500MG CPR", "categorie": "Antipaludéens", "prix_fcfa": 2000,
         "indications": "Paludisme sévère ou résistant.",
         "posologie_adulte": "1 comprimé (500 mg) 3 fois/jour pendant 7 jours.",
         "posologie_enfant": "25 mg/kg/jour en 3 prises.",
         "contre_indications": "Hypersensibilité à la quinine, neuropathie optique."},
        {"nom": "ARTEMETHER INJECTION", "categorie": "Antipaludéens", "prix_fcfa": 3000,
         "indications": "Paludisme sévère (voie parentérale).",
         "posologie_adulte": "3,2 mg/kg en injection IM ou IV.",
         "posologie_enfant": "Même posologie.",
         "contre_indications": "Allergie, insuffisance rénale sévère."},
        # === ANTIBIOTIQUES (9) ===
        {"nom": "AMOXICILLINE 500MG GEL B/12", "categorie": "Antibiotiques", "prix_fcfa": 1500,
         "indications": "Infections ORL, respiratoires, urinaires, digestives.",
         "posologie_adulte": "1 gélule (500 mg) 3 fois/jour.",
         "posologie_enfant": "50 mg/kg/jour en 3 prises.",
         "contre_indications": "Allergie aux pénicillines."},
        {"nom": "CLAMOXYL 1G CPR", "categorie": "Antibiotiques", "prix_fcfa": 4500,
         "indications": "Infections sévères (pneumonies, méningites).",
         "posologie_adulte": "1 comprimé (1 g) 3 fois/jour.",
         "posologie_enfant": "80 mg/kg/jour en 3 prises.",
         "contre_indications": "Allergie aux pénicillines, mononucléose infectieuse."},
        {"nom": "CLAMOXYL 500MG CPR", "categorie": "Antibiotiques", "prix_fcfa": 2800,
         "indications": "Infections bactériennes courantes.",
         "posologie_adulte": "1 comprimé 3 fois/jour.",
         "posologie_enfant": "50 mg/kg/jour en 3 prises.",
         "contre_indications": "Allergie aux pénicillines."},
        {"nom": "AUGMENTIN 1G CPR B/14", "categorie": "Antibiotiques", "prix_fcfa": 5500,
         "indications": "Infections à germes producteurs de bêta-lactamases.",
         "posologie_adulte": "1 comprimé (1 g) 2 fois/jour.",
         "posologie_enfant": "25 mg/kg/jour en 2 prises.",
         "contre_indications": "Allergie aux pénicillines, ictère."},
        {"nom": "CIPROFLOXACINE 500MG CPR", "categorie": "Antibiotiques", "prix_fcfa": 2500,
         "indications": "Infections urinaires, intestinales, ostéo-articulaires.",
         "posologie_adulte": "1 comprimé (500 mg) 2 fois/jour.",
         "posologie_enfant": "À éviter (risque de lésions cartilagineuses).",
         "contre_indications": "Allergie aux fluoroquinolones, moins de 18 ans."},
        {"nom": "AZITHROMYCINE 500MG CPR", "categorie": "Antibiotiques", "prix_fcfa": 3500,
         "indications": "Infections ORL, bronchites, infections génitales.",
         "posologie_adulte": "1 comprimé (500 mg)/jour pendant 3 jours.",
         "posologie_enfant": "10 mg/kg en une prise/jour pendant 3 jours.",
         "contre_indications": "Allergie aux macrolides."},
        {"nom": "METRONIDAZOLE (FLAGYL) 500MG", "categorie": "Antibiotiques", "prix_fcfa": 1200,
         "indications": "Infections dentaires, intestinales (amibiase, giardiase).",
         "posologie_adulte": "1 comprimé (500 mg) 3 fois/jour.",
         "posologie_enfant": "15 mg/kg/jour en 3 prises.",
         "contre_indications": "Allergie au métronidazole, 1er trimestre grossesse."},
        {"nom": "NIFLOXANE 400MG CPR", "categorie": "Antibiotiques", "prix_fcfa": 2300,
         "indications": "Infections urinaires, digestives.",
         "posologie_adulte": "1 comprimé 2 fois/jour.",
         "posologie_enfant": "À éviter.",
         "contre_indications": "Allergie aux fluoroquinolones."},
        {"nom": "CEFPAN 500MG CPR", "categorie": "Antibiotiques", "prix_fcfa": 2500,
         "indications": "Infections ORL, respiratoires.",
         "posologie_adulte": "1 comprimé 2 fois/jour.",
         "posologie_enfant": "25 mg/kg/jour en 2 prises.",
         "contre_indications": "Allergie aux céphalosporines."},
        # === DIGESTIFS (9) ===
        {"nom": "OMEPRAZOLE 20MG GELULES", "categorie": "Digestifs", "prix_fcfa": 1500,
         "indications": "Ulcère gastroduodénal, reflux gastro-œsophagien.",
         "posologie_adulte": "1 gélule (20 mg)/jour le matin à jeun.",
         "posologie_enfant": "1 mg/kg/jour (max 20 mg) chez l'enfant > 2 ans.",
         "contre_indications": "Allergie, grossesse (précaution)."},
        {"nom": "MAALOX (SUSPENSION BUVABLE)", "categorie": "Digestifs", "prix_fcfa": 2500,
         "indications": "Brûlures d'estomac, remontées acides.",
         "posologie_adulte": "1-2 cuillères à soupe après les repas.",
         "posologie_enfant": "1 cuillère à café par 10 kg, après les repas.",
         "contre_indications": "Insuffisance rénale sévère."},
        {"nom": "GAVISCON SUSPENSION BUVABLE", "categorie": "Digestifs", "prix_fcfa": 2800,
         "indications": "Reflux gastro-œsophagien (brûlures).",
         "posologie_adulte": "10-20 ml après les repas et au coucher.",
         "posologie_enfant": "5-10 ml après les repas.",
         "contre_indications": "Insuffisance rénale (éviter sachets de sodium)."},
        {"nom": "GAVISCON CITRON SACHET", "categorie": "Digestifs", "prix_fcfa": 600,
         "indications": "Reflux gastrique.",
         "posologie_adulte": "1 sachet après les repas.",
         "posologie_enfant": "1/2 sachet après les repas.",
         "contre_indications": "Insuffisance rénale."},
        {"nom": "SPASFON CPR B/30", "categorie": "Digestifs", "prix_fcfa": 2100,
         "indications": "Spasmes digestifs, coliques, règles douloureuses.",
         "posologie_adulte": "1-2 comprimés 3 fois/jour.",
         "posologie_enfant": "1 comprimé 2-3 fois/jour.",
         "contre_indications": "Allergie, glaucome, rétention urinaire."},
        {"nom": "SPASFON LYOC", "categorie": "Digestifs", "prix_fcfa": 1500,
         "indications": "Spasmes digestifs et gynécologiques.",
         "posologie_adulte": "1 lyoc 3 fois/jour.",
         "posologie_enfant": "1 lyoc 2 fois/jour.",
         "contre_indications": "Allergie, glaucome."},
        {"nom": "SMECTA SACHETS B/30", "categorie": "Digestifs", "prix_fcfa": 2000,
         "indications": "Diarrhée aiguë chez l'adulte et l'enfant.",
         "posologie_adulte": "1 sachet 3 fois/jour.",
         "posologie_enfant": "<1 an:1/jour; 1-2 ans:2/jour; 2-3 ans:2-3/jour.",
         "contre_indications": "Subocclusion intestinale."},
        {"nom": "IMODIUM (LOPERAMIDE) 2MG", "categorie": "Digestifs", "prix_fcfa": 1500,
         "indications": "Diarrhée aiguë (symptomatique).",
         "posologie_adulte": "2 comprimés initial, puis 1 après chaque selle liquide.",
         "posologie_enfant": "À partir de 6 ans : 1 comprimé initial, puis 1 après chaque selle.",
         "contre_indications": "Enfant < 6 ans, subocclusion, diarrhée sanguinolente."},
        {"nom": "VOGALENE 15MG CPR", "categorie": "Digestifs", "prix_fcfa": 3000,
         "indications": "Nausées, vomissements.",
         "posologie_adulte": "1 comprimé (15 mg) 3 fois/jour.",
         "posologie_enfant": "0,5-1 mg/kg/jour en 2-3 prises.",
         "contre_indications": "Allergie, grossesse (précaution)."},
        # === ANTIPARASITAIRES (2) ===
        {"nom": "MEBENDAZOLE (VERMOX) 100MG", "categorie": "Antiparasitaires", "prix_fcfa": 1200,
         "indications": "Verminoses (oxyures, ascaris, ankylostomes).",
         "posologie_adulte": "1 comprimé (100 mg) 2 fois/jour pendant 3 jours.",
         "posologie_enfant": "Même posologie à partir de 2 ans.",
         "contre_indications": "Allergie au mébendazole."},
        {"nom": "ALBENDAZOLE 400MG CPR", "categorie": "Antiparasitaires", "prix_fcfa": 1000,
         "indications": "Téniasis, cysticercose, hydatidose.",
         "posologie_adulte": "1 comprimé (400 mg) en prise unique.",
         "posologie_enfant": "À partir de 2 ans : même posologie.",
         "contre_indications": "Allergie, grossesse (éviter)."},
        # === ANTIHISTAMINIQUES (4) ===
        {"nom": "CETIRIZINE 10MG CPR", "categorie": "Antihistaminiques", "prix_fcfa": 1200,
         "indications": "Allergies, urticaire, rhinite allergique.",
         "posologie_adulte": "1 comprimé (10 mg) par jour.",
         "posologie_enfant": "5 mg/jour pour les 6-12 ans.",
         "contre_indications": "Allergie, insuffisance rénale sévère."},
        {"nom": "ZYRTEC 10MG CPR", "categorie": "Antihistaminiques", "prix_fcfa": 1800,
         "indications": "Rhinite allergique, urticaire.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "5 mg/jour pour les 6-12 ans.",
         "contre_indications": "Insuffisance rénale sévère."},
        {"nom": "TAVEGYL 1MG CPR", "categorie": "Antihistaminiques", "prix_fcfa": 1000,
         "indications": "Allergies, piqûres d'insectes.",
         "posologie_adulte": "1 comprimé 2-3 fois/jour.",
         "posologie_enfant": "0,5 mg/kg/jour en 2-3 prises.",
         "contre_indications": "Glaucome, rétention urinaire."},
        {"nom": "FERVEX ADULTE SACHETS", "categorie": "Antihistaminiques", "prix_fcfa": 2500,
         "indications": "Rhumes, rhinites, états grippaux.",
         "posologie_adulte": "1 sachet 3 fois/jour, à diluer dans un verre d'eau.",
         "posologie_enfant": "À partir de 15 ans même posologie.",
         "contre_indications": "Allergie, insuffisance hépatique."},
        # === VITAMINES & COMPLÉMENTS (6) ===
        {"nom": "VITASCORBOL 500MG", "categorie": "Vitamines", "prix_fcfa": 2615,
         "indications": "Carence en vitamine C, fatigue passagère.",
         "posologie_adulte": "1 comprimé (500 mg) 2 fois/jour.",
         "posologie_enfant": "1 comprimé par jour à partir de 6 ans.",
         "contre_indications": "Intolérance au fructose, hyperoxalurie."},
        {"nom": "SUPRADYN INTENSIA", "categorie": "Vitamines", "prix_fcfa": 4000,
         "indications": "Carences vitaminiques, convalescence.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "À partir de 12 ans.",
         "contre_indications": "Allergie à un composant, hypervitaminose."},
        {"nom": "FERO-GRAD (SULFATE DE FER)", "categorie": "Vitamines", "prix_fcfa": 2500,
         "indications": "Anémie ferriprive.",
         "posologie_adulte": "1 comprimé (150 mg) par jour.",
         "posologie_enfant": "À partir de 6 ans : 50 mg/kg/jour.",
         "contre_indications": "Hémochromatose, thalassémie, allergie au fer."},
        {"nom": "MAGNESIUM 500MG CPR", "categorie": "Vitamines", "prix_fcfa": 2500,
         "indications": "Fatigue, crampes, stress.",
         "posologie_adulte": "1 comprimé 2 fois/jour.",
         "posologie_enfant": "1 comprimé par jour.",
         "contre_indications": "Insuffisance rénale sévère."},
        {"nom": "CALCIUM 500MG + VITAMINE D", "categorie": "Vitamines", "prix_fcfa": 3000,
         "indications": "Prévention de l'ostéoporose, carence calcique.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "1 comprimé par jour.",
         "contre_indications": "Hypercalcémie, lithiase rénale."},
        {"nom": "ZINC 15MG CPR", "categorie": "Vitamines", "prix_fcfa": 2000,
         "indications": "Carence en zinc, cicatrisation.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "1 comprimé par jour.",
         "contre_indications": "Allergie."},
        # === ANTISEPTIQUES (2) ===
        {"nom": "BETADINE DERMIQUE (JAUNE) 10%", "categorie": "Antiseptiques", "prix_fcfa": 1500,
         "indications": "Antiseptique des plaies, brûlures, escarres.",
         "posologie_adulte": "Appliquer sur la plaie nettoyée 2-3 fois/jour.",
         "posologie_enfant": "Même usage.",
         "contre_indications": "Allergie à l'iode, grossesse."},
        {"nom": "BACTROBAN POMMADE", "categorie": "Antiseptiques", "prix_fcfa": 3500,
         "indications": "Infections cutanées (impétigo, furoncle).",
         "posologie_adulte": "Appliquer 3 fois/jour.",
         "posologie_enfant": "Même usage.",
         "contre_indications": "Allergie à la mupirocine."},
        # === ANTIRHUMATISMAUX (4) ===
        {"nom": "ARTHROTEC 50MG CPR", "categorie": "Antirhumatismaux", "prix_fcfa": 4000,
         "indications": "Arthrose, polyarthrite rhumatoïde.",
         "posologie_adulte": "1 comprimé 2 fois/jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Ulcère, grossesse."},
        {"nom": "COLCHICINE 1MG CPR", "categorie": "Antirhumatismaux", "prix_fcfa": 2000,
         "indications": "Crise de goutte, maladie de Behçet.",
         "posologie_adulte": "1 mg initial, puis 0,5 mg toutes les 2h (max 8 mg/jour).",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Insuffisance rénale, hépatique, grossesse."},
        {"nom": "HYDROXYCHLOROQUINE 200MG CPR", "categorie": "Antirhumatismaux", "prix_fcfa": 3000,
         "indications": "Lupus, polyarthrite rhumatoïde.",
         "posologie_adulte": "1 à 2 comprimés par jour.",
         "posologie_enfant": "5 mg/kg/jour.",
         "contre_indications": "Allergie, rétinopathie."},
        {"nom": "METHOTREXATE 2.5MG CPR", "categorie": "Antirhumatismaux", "prix_fcfa": 2500,
         "indications": "Polyarthrite rhumatoïde, psoriasis.",
         "posologie_adulte": "2,5 à 15 mg une fois par semaine.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Grossesse, insuffisance rénale."},
        # === CORTICOÏDES (1) ===
        {"nom": "SOLUPRED 5MG CPR", "categorie": "Corticoïdes", "prix_fcfa": 1800,
         "indications": "Corticothérapie (asthme, allergies sévères).",
         "posologie_adulte": "Dose variable selon pathologie.",
         "posologie_enfant": "0,5 mg/kg/jour.",
         "contre_indications": "Infection systémique non contrôlée."},
        # === VÉNOTONIQUES (1) ===
        {"nom": "GINKOR FORT 30MG CPR", "categorie": "Vénotoniques", "prix_fcfa": 3800,
         "indications": "Insuffisance veineuse, jambes lourdes.",
         "posologie_adulte": "1 comprimé matin et soir.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Allergie au ginkgo."},
        # === CARDIOVASCULAIRES (8) ===
        {"nom": "CAPTOPRIL 25MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 1800,
         "indications": "Hypertension artérielle, insuffisance cardiaque.",
         "posologie_adulte": "1 comprimé (25 mg) 2-3 fois/jour.",
         "posologie_enfant": "1 mg/kg/jour en 2-3 prises.",
         "contre_indications": "Allergie, grossesse (2e-3e trimestre)."},
        {"nom": "ATENOLOL 50MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 2000,
         "indications": "Hypertension, angor, tachycardie.",
         "posologie_adulte": "1 comprimé (50 mg) par jour.",
         "posologie_enfant": "1-2 mg/kg/jour.",
         "contre_indications": "Bradycardie, insuffisance cardiaque sévère."},
        {"nom": "FUROSEMIDE 40MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 1500,
         "indications": "Œdèmes, hypertension (diurétique).",
         "posologie_adulte": "1 comprimé (40 mg) le matin.",
         "posologie_enfant": "1-2 mg/kg/jour.",
         "contre_indications": "Insuffisance rénale anurique, grossesse."},
        {"nom": "CLOPIDOGREL 75MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 3500,
         "indications": "Prévention des accidents ischémiques.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Ulcère, hémorragie."},
        {"nom": "ATORVASTATINE 20MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 4000,
         "indications": "Hypercholestérolémie, prévention cardiovasculaire.",
         "posologie_adulte": "1 comprimé le soir.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Grossesse, maladie hépatique."},
        {"nom": "RAMIPRIL 5MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 2500,
         "indications": "Hypertension, insuffisance cardiaque.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Allergie, grossesse."},
        {"nom": "AMLODIPINE 5MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 3000,
         "indications": "Hypertension, angor.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Hypotension sévère."},
        {"nom": "BISOPROLOL 5MG CPR", "categorie": "Cardiovasculaires", "prix_fcfa": 2800,
         "indications": "Insuffisance cardiaque, hypertension.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Bradycardie, asthme."},
        # === DIABÈTE (2) ===
        {"nom": "METFORMINE 500MG CPR", "categorie": "Diabète", "prix_fcfa": 2000,
         "indications": "Diabète de type 2.",
         "posologie_adulte": "1 comprimé (500 mg) 2-3 fois/jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Insuffisance rénale, alcoolisme."},
        {"nom": "GLIBENCLAMIDE 5MG CPR", "categorie": "Diabète", "prix_fcfa": 1500,
         "indications": "Diabète de type 2.",
         "posologie_adulte": "1 comprimé (5 mg) par jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Insuffisance rénale, hépatique, grossesse."},
        # === RESPIRATOIRES (2) ===
        {"nom": "SALBUTAMOL 100MCG AEROSOL", "categorie": "Respiratoires", "prix_fcfa": 3500,
         "indications": "Asthme, bronchospasme.",
         "posologie_adulte": "1-2 bouffées 3-4 fois/jour.",
         "posologie_enfant": "1 bouffée 3-4 fois/jour.",
         "contre_indications": "Allergie, tachycardie sévère."},
        {"nom": "BECLOMETASONE 50MCG AEROSOL", "categorie": "Respiratoires", "prix_fcfa": 4000,
         "indications": "Asthme (traitement de fond).",
         "posologie_adulte": "2 bouffées 2 fois/jour.",
         "posologie_enfant": "1-2 bouffées 2 fois/jour.",
         "contre_indications": "Infections respiratoires non contrôlées."},
        # === NEUROLOGIQUES (4) ===
        {"nom": "DIAZEPAM 10MG INJECTION", "categorie": "Neurologiques", "prix_fcfa": 2500,
         "indications": "Convulsions, anxiété sévère.",
         "posologie_adulte": "10-20 mg en injection IV/IM.",
         "posologie_enfant": "0,2-0,3 mg/kg en IV.",
         "contre_indications": "Allergie, glaucome, myasthénie."},
        {"nom": "CARBAMAZEPINE 200MG CPR", "categorie": "Neurologiques", "prix_fcfa": 3000,
         "indications": "Épilepsie, névralgies.",
         "posologie_adulte": "1 comprimé (200 mg) 2-3 fois/jour.",
         "posologie_enfant": "10-20 mg/kg/jour.",
         "contre_indications": "Allergie, blocage cardiaque."},
        {"nom": "DONEPEZIL 5MG CPR", "categorie": "Neurologiques", "prix_fcfa": 4500,
         "indications": "Maladie d'Alzheimer (traitement symptomatique).",
         "posologie_adulte": "1 comprimé le soir.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Allergie, grossesse."},
        {"nom": "LEVODOPA 250MG CPR", "categorie": "Neurologiques", "prix_fcfa": 5000,
         "indications": "Maladie de Parkinson.",
         "posologie_adulte": "Dose progressive selon prescription.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Glaucome, psychose."},
        # === ANTIDÉPRESSEURS (3) ===
        {"nom": "AMITRIPTYLINE 25MG CPR", "categorie": "Antidépresseurs", "prix_fcfa": 2000,
         "indications": "Dépression, anxiété, douleurs neuropathiques.",
         "posologie_adulte": "1 comprimé (25 mg) 2-3 fois/jour.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Glaucome, rétention urinaire, infarctus récent."},
        {"nom": "MIRTAZAPINE 30MG CPR", "categorie": "Antidépresseurs", "prix_fcfa": 4000,
         "indications": "Dépression sévère, anxiété.",
         "posologie_adulte": "1 comprimé le soir.",
         "posologie_enfant": "Non recommandé.",
         "contre_indications": "Allergie, grossesse."},
        {"nom": "SERTRALINE 50MG CPR", "categorie": "Antidépresseurs", "prix_fcfa": 3500,
         "indications": "Dépression, trouble obsessionnel-compulsif.",
         "posologie_adulte": "1 comprimé par jour.",
         "posologie_enfant": "25 mg/jour.",
         "contre_indications": "Allergie, grossesse."},
        # === ANTICOAGULANTS (1) ===
        {"nom": "HEPARINE SODIQUE 5000 UI/ML", "categorie": "Anticoagulants", "prix_fcfa": 4500,
         "indications": "Thrombose, embolie (anticoagulant).",
         "posologie_adulte": "5000 UI en injection IV ou SC.",
         "posologie_enfant": "50-100 UI/kg.",
         "contre_indications": "Hémorragie, allergie, thrombopénie."},
        # === AUTRES (1) ===
        {"nom": "PHLOROGLUCINOL 80MG CPR", "categorie": "Autres", "prix_fcfa": 1800,
         "indications": "Spasmes digestifs, coliques néphrétiques.",
         "posologie_adulte": "1 comprimé 2-3 fois/jour.",
         "posologie_enfant": "1 comprimé 2 fois/jour.",
         "contre_indications": "Allergie."}
    ]

# ==============================================================================
# DONNÉES : PHARMACIES (liste complète avec ville et commune)
# ==============================================================================
if "pharmacies_db" not in st.session_state:
    # Liste complète issue des images – toutes à Niamey, mais on ajoute quelques exemples pour d'autres villes
    pharmacy_data = [
        {"nom": "03 AOUT", "adresse": "Boulevard Mali-Bero", "tel": "20 35 18 18 // 90 86 83 96", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "2EME FORAGE", "adresse": "BP 219", "tel": "20 75 27 90", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "7 THERAPIES", "adresse": "Quartier Bobiel Ilôt 5069 /H", "tel": "21 66 21 58 // 98 78 16 45 // 99 08 12 87", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "AIR", "adresse": "Niamey", "tel": "20 74 01 29", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ABDOULKARIM", "adresse": "Kalley Nord", "tel": "21 76 60 79", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ADOUA", "adresse": "Niamey", "tel": "90 89 95 46", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "AEROPORT", "adresse": "Face CSI Aéroport", "tel": "96 55 95 95 // 20 34 03 49", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "AL BARAKA", "adresse": "Recasement 3ème Laterite", "tel": "20 35 06 70", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "AL-AFYA", "adresse": "Lazaret Ilôt 5032 Parcelle C", "tel": "97 11 66 20", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "ALFORMA", "adresse": "Qtier Sarey Koubou Ilôt N 6132", "tel": "84 73 40 20", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "ALIYYAH", "adresse": "Kouara Kano Ilôt 3245 1er Arr", "tel": "91 37 63 87", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "AMANA GAWEYE", "adresse": "Niamey", "tel": "21 88 96 20", "commune": "COMMUNE V", "ville": "Niamey"},
        {"nom": "AMINA", "adresse": "2ème Laterite", "tel": "20 35 08 80", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "ANY KOIRA", "adresse": "Avenue du Belafon, BP 11970", "tel": "20 73 50 82", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "AR-RAHMA", "adresse": "Qtier Sarey Koubou Ilôt N 6276, BP 13309", "tel": "91 01 01 84", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "ARENES", "adresse": "Avenue Mali Bero, BP 12635", "tel": "20 74 16 11 // 20 34 00 09 // 90 41 36 36", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "AREWA", "adresse": "58 Avenue de l’Ader (Boukoki IV), BP 12031", "tel": "20 73 35 05 // 90 44 44 22 // 90 96 25 15", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "AS SALAM", "adresse": "Place de Gadafawa, BP 611", "tel": "20 75 31 25 // 80 06 10 80 // 80 06 10 81", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ASKIA", "adresse": "Avenue Mali Bero", "tel": "21 31 68 05", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ASSAMAD", "adresse": "Qtier Francophonie Route Ouall", "tel": "88 92 00 94", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "AVENIR", "adresse": "Avenue de Zarmakoye Face SNV, BP 12011", "tel": "20 75 38 69", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "BANIFANDOU", "adresse": "Quartier Medina, BP 11460", "tel": "20 34 02 40", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "BELLEVUE", "adresse": "Qtier Foulani Koira", "tel": "93 17 21 58", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "BIOPHARM", "adresse": "718 Lotissement Niamey Bas", "tel": "91 46 22 20", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "BOBIEL", "adresse": "Rue FK-79 Porte 293 (CUN 1)", "tel": "21 76 70 62", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "BONKANEY", "adresse": "Avenue Katsina CN6", "tel": "20 36 36 70", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "BOUMI", "adresse": "Avenue Bare CSI Lazaret, BP 12477", "tel": "20 32 03 40 // 90 47 68 69", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "CARREFOUR SIXIEME", "adresse": "Rond Point des Armées, BP 13339", "tel": "20 74 18 18", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CENTRALE 2", "adresse": "Place du Petit Marché, BP 11043", "tel": "21 76 42 95 // 96 27 27 24", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "CENTRE AERE BCEAO", "adresse": "Bobiel Face Centre aéré BCEAO", "tel": "98 51 77 41", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CHATEAU 8", "adresse": "Avenue Mali Bero, BP 782", "tel": "20 75 24 02", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CHATEAU I", "adresse": "Avenue du Château d’Eau, BP 219", "tel": "20 72 27 77", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CHOUKRALLAH", "adresse": "Ouest Francophonie Ilôt 8485", "tel": "96 12 14 63", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "CITE ASECNA", "adresse": "IV Arrondissement", "tel": "96 99 35 01", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "CITE BCEAO", "adresse": "Rue BF 224 Porte 329", "tel": "21 88 79 68 // 93 23 38 17", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "CITE CAISSE", "adresse": "Cité Caisse, BP 10476", "tel": "21 76 48 37 // 96 88 88 39", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "CITE CHINOISE", "adresse": "Route Ouallam", "tel": "23 90 37 31 // 92 59 43 96 // 96 97 92 27", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "CITE FAYCAL", "adresse": "Avenue Gd Marché Rue du Sénégal, BP 2417", "tel": "20 74 13 26", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "CITE NIAMEY 2000", "adresse": "Niamey", "tel": "21 31 37 82", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "CITE RENAISSANCE", "adresse": "Quartier Cité Renaissance", "tel": "84 96 21 87", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CODIPHARM SA", "adresse": "Sonuci Petroba Villa 112", "tel": "", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "COLLEGE LAKO", "adresse": "Avenue de l’ADER", "tel": "20 73 33 77", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "COLLEGE MARIAMA", "adresse": "Avenue du Canada, BP 10030", "tel": "20 74 19 14 // 96 96 64 40", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "COMPLEXE", "adresse": "Boulevard du Mali, BP 13221", "tel": "20 74 14 14 // 20 74 14 83", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "CONCORDE", "adresse": "Blvd Mali Bero, BP 13247", "tel": "20 35 26 36 // 90 19 45 33", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "COURONNE NORD", "adresse": "BP 2943", "tel": "20 36 46 10", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "DAN-GAO", "adresse": "Rue des Amenokals, BP 825", "tel": "20 74 03 36", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "DENDI KOIRA KANO", "adresse": "Koira Kano Nord", "tel": "21 31 73 31", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "DEYZEBON", "adresse": "Quartier Dyezebon, BP 10202", "tel": "20 73 67 90", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "DINE", "adresse": "Quartier Riyad, Route Niamey", "tel": "96 99 00 19", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "DOM", "adresse": "Rue BF 142 Porte 1540", "tel": "20 36 07 09", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "ECOLE CANADA", "adresse": "Qtier Nouveau Marché Niamey, BP 10962", "tel": "20 74 33 69 // 96 99 11 71", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "EL NASR", "adresse": "Immeuble El Nasr, BP 10494", "tel": "20 73 47 72 // 93 92 61 16", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ESPOIR", "adresse": "Boulevard du Mali", "tel": "20 36 01 80", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "FASSA", "adresse": "BP 11752", "tel": "20 37 23 91 // 90 21 13 91 // 96 73 21 63", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "FRANCOPHONIE SARLU", "adresse": "Quartier Francophonie, BP 2321", "tel": "20 32 20 30", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "GAMIKALLEY", "adresse": "Avenue de l’Afrique, BP 12281", "tel": "20 33 78 86 // 96 59 85 14", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "GAPTCHI EX LAC TCHAD", "adresse": "Nouveau Marché Parcelle 7", "tel": "90 09 66 56", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "GARE", "adresse": "Niamey", "tel": "98 82 42 31", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "GAWADO", "adresse": "Aéroport Ilôt 3195 4EME Arrt", "tel": "80 62 79 59", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "GOBI", "adresse": "Koira Kano Ilôt 2242 Parcelle I", "tel": "", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "GOROUAL", "adresse": "Quartier Bobiel Ilôt 8394/A", "tel": "20 32 04 54 // 96 33 71 76 // 97 66 43 63", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "GOUDEL", "adresse": "Goudel Motaîzé-Do 1ER Arrondis", "tel": "97 10 43 23", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "GRAND MARCHE", "adresse": "Face Grand Marché, ADM Niamey", "tel": "20 73 40 78", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "GRANDE ROUTE FILINGUE", "adresse": "Niamey", "tel": "23 90 37 30", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "HAROBANDA", "adresse": "Avenue Alpha Mahamane Djobo, BP 10001", "tel": "21 88 97 02 // 21 76 62 69 // 96 55 76 76", "commune": "COMMUNE V", "ville": "Niamey"},
        {"nom": "IMANE", "adresse": "Koira Teguï Ilôt 8016 Parcel F, BP 12492", "tel": "98 57 77 10 // 90 28 09 42", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "INDEPENDANCE", "adresse": "Boulevard de l’Indépendance, BP 13433", "tel": "20 33 05 06 // 90 96 45 08", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "JANGORZO", "adresse": "Rue du Djado, BP 13622", "tel": "20 34 04 68 // 96 49 48 94", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "KA TCHOUNE", "adresse": "Qtier Satu SA, Gabou Goura", "tel": "91 14 24 14", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "KALLET EST", "adresse": "Boulevard de l’Islam, BP 10721", "tel": "20 74 29 99 // 96 90 60 50", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "KASSEY", "adresse": "Niamey", "tel": "21 64 02 02 // 20 73 60 67", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "KAWSAR", "adresse": "Lotis. Cité du Progrès", "tel": "99 12 49 99", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "KIRKISSOYE", "adresse": "Niamey", "tel": "20 31 51 40", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "KOIRA TEGUI", "adresse": "Boulevard de la Liberté", "tel": "20 73 49 90", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "LA REFERENCE", "adresse": "Qtier Sarey Koubou Ilôt N 6146", "tel": "96 18 23 59", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "LACOUROUSSE", "adresse": "Boulevard de la Liberté", "tel": "20 73 49 49", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "LAMORDE", "adresse": "Lamorde Ilôt 1305, Parc. H", "tel": "20 31 59 46 // 92 19 80 95", "commune": "COMMUNE V", "ville": "Niamey"},
        {"nom": "LAZARET", "adresse": "Avenue du Zarmaganda Qt Lazare, BP 10347", "tel": "20 75 25 09", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "MAISON ECONOMIQUE", "adresse": "BP 2305, ADM Niamey", "tel": "20 73 90 51", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "MALI-BERO", "adresse": "Boulevard Mali-Bero, BP 10898", "tel": "90 58 38 01", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "MALOU", "adresse": "Quartier Franco Porte 150", "tel": "", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "MOAGA", "adresse": "Losso Goungou 1ER Arrondiss.", "tel": "88 13 89 67", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "MOSSI EX PLATEAU", "adresse": "Avenue Mali Bero", "tel": "20 33 09 55", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "MUTUALISTE", "adresse": "Avenue du Zarmaganda Qt Lazare", "tel": "21 76 99 04", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "NASSARA", "adresse": "Nouveau Marché Parcelle 7", "tel": "91 55 99 90", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "NIAMEY NYALA", "adresse": "Foulani Kouara, Ilôt 3496 P J", "tel": "", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "NIIMA", "adresse": "4 Avenue de l’Islam Kalley Est", "tel": "20 33 00 33", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "NOAH", "adresse": "Kouara ME Boulevard Mali Bero, BP 2366", "tel": "20 73 93 10", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "NOUR", "adresse": "Quartier Abidjan KM27", "tel": "20 73 44 47", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "NOUVEAU MARCHE", "adresse": "Avenue des Sapeurs Pompiers, BP 467", "tel": "20 74 14 81", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "OU A", "adresse": "BP 11879", "tel": "20 74 31 46", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "PATIENCE", "adresse": "Boulevard de la Liberté, BP 2585", "tel": "20 73 77 27 // 96 87 22 24 // 90 81 71 85", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "de la NATION", "adresse": "Quartier Kombo 1ER Arrt Commun", "tel": "90 65 25 92", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "des CAMPS", "adresse": "Yantala Ilôt 1402 Parcelle F", "tel": "20 75 53 00", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ESCADRILLE", "adresse": "Talladje 4EME Arr. Communal", "tel": "88 43 90 43", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "LES JUMELLES", "adresse": "Qtier R Lot. IDE Gano ZAC PA", "tel": "92 02 15 15", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "NORDIRE", "adresse": "Harobanda Nordire Ilôt 7255", "tel": "", "commune": "COMMUNE V", "ville": "Niamey"},
        {"nom": "SONUCI", "adresse": "Koira Kano Nord, Ilôt 4478 P.B", "tel": "20 37 08 50", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "SOS", "adresse": "Village SOS Ilôt 5761 Parc M C1", "tel": "20 35 14 66 // 21 76 45 25", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "VIDAL", "adresse": "Ext Foulani Kouara II", "tel": "20 75 22 54", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "BASSORA", "adresse": "Talladje Est Ilôt 5171", "tel": "20 38 00 96", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "du RENOUVEAU", "adresse": "Face Station Total NY 2000", "tel": "80 06 31 28 // 96 49 66 59", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "PLATEAU 2", "adresse": "Yantala Résidentiel, Ilôt 2105", "tel": "80 90 97 60", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "POINT D", "adresse": "Face Clinique Iran, BP 13219", "tel": "20 72 41 99 // 20 72 56 96 // 96 96 72 18", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "POSTE", "adresse": "Route Fillingue Secteur CUN 4", "tel": "96 37 53 25", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "RAWDA", "adresse": "Qtier Tchangarey Ilôt 10036 PA, CC Niamey", "tel": "80 89 03 13", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "RAYAL", "adresse": "Route Ouallam", "tel": "", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "RECASEMENT", "adresse": "Avenue de Daoura YN 187, BP 11931", "tel": "20 35 03 88", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "REFERENCE EX 2È ARRONDISSEMENT", "adresse": "1, Rue de la Tunisie", "tel": "88 92 00 91", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "REMEDE", "adresse": "Banizoumbou, Ilôt N°4001, Parc", "tel": "97 11 67 25", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "RENAISSANCE II", "adresse": "Qtier Banizoumbou II Ilôt 4055", "tel": "20 36 00 99", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "REPUBLIQUE EX KAOCEN", "adresse": "3 EME Arrondissement Communal", "tel": "20 73 54 54", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "RIDWANE DU BIEN ETRE", "adresse": "Av. de Toukous", "tel": "88 53 83 41 // 20 35 06 65 // 20 35 19 97", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "ROND POINT", "adresse": "Avenue Charles de Gaulle, BP 12865", "tel": "20 73 42 83 // 20 72 27 24", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ROND POINT LIPTAKO", "adresse": "BP 962", "tel": "20 31 51 20 // 96 49 81 57", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "ROUTE NYALA TOURAKOU", "adresse": "Avenue Tanimoune, Tourakou", "tel": "80 08 54 51", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "ROUTE TILLABERY", "adresse": "KK 154 Porte N°23, BP 10080", "tel": "20 35 04 50 // 90 22 79 01", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "ROUTE TORODI", "adresse": "Karadje-Rive Droite Ilôt 1549, BP 2262", "tel": "20 31 79 07", "commune": "COMMUNE V", "ville": "Niamey"},
        {"nom": "SABO", "adresse": "Route Ouallam, BP 719", "tel": "20 35 01 99 // 97 35 72 02", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "SAGA", "adresse": "Niamey", "tel": "21 88 67 39", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "SAID SALAM", "adresse": "Niamey", "tel": "20 35 13 13", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "SALBAZ", "adresse": "Lotis. Route Ouallam, Ilôt 6487", "tel": "92 70 30 00", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "SANTE PLUS", "adresse": "Koira Kano Nord", "tel": "", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "SAYE", "adresse": "BP 10433", "tel": "20 35 22 64", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "SIRA", "adresse": "Route de Tillabery, BP 2509", "tel": "20 37 34 66 // 96 56 52 82 // 97 10 50 50", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "SOUCKO", "adresse": "Niamey", "tel": "20 73 68 58", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "TAJEJE", "adresse": "RN N°1", "tel": "80 07 53 93", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "TALLADJE EST", "adresse": "Avenue Mali Bero", "tel": "21 66 50 34", "commune": "COMMUNE IV", "ville": "Niamey"},
        {"nom": "TARAN", "adresse": "Banifandou", "tel": "20 36 30 31", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "TAWHID", "adresse": "Bobiel, Ilôt 4343 F1", "tel": "99 39 19 96", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "TEMPLE", "adresse": "1, Avenue du Niger, BP 10106", "tel": "20 73 47 90 // 96 96 20 06 // 20 75 34 45", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "TENERE", "adresse": "48, Avenue de la Liberté, BP 10233", "tel": "20 74 28 98 // 20 34 01 78", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "TERMINUS", "adresse": "Rue du Sahel, BP 13210", "tel": "20 73 58 38", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "VOGUE", "adresse": "Côté 1010 face Palais des sports, BP 13186", "tel": "20 72 58 88 // 20 72 58 58", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "VOIE EXPRESS", "adresse": "Cité Fayçal face Voie Express", "tel": "98 14 25 94", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "WADATA", "adresse": "Avenue de l’Air, BP 11086", "tel": "20 74 22 14 // 96 98 28 13", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "YANTALA", "adresse": "1, Avenue de Niamey, BP 128", "tel": "20 75 24 39 // 20 75 38 83", "commune": "COMMUNE I", "ville": "Niamey"},
        {"nom": "ZAM ZAM", "adresse": "Lazaret Ilôt 5055 Parcelle B", "tel": "", "commune": "COMMUNE II", "ville": "Niamey"},
        {"nom": "ZANA", "adresse": "Quartier ORTN Rue OR Banifando", "tel": "91 14 58 37", "commune": "COMMUNE III", "ville": "Niamey"},
        {"nom": "ZARA EX CAMPING", "adresse": "Niamey", "tel": "20 35 03 87", "commune": "COMMUNE I", "ville": "Niamey"},

        # --- Quelques pharmacies fictives dans d'autres villes pour démo ---
        {"nom": "PHARMACIE ZINDER CENTRE", "adresse": "Avenue de l'Indépendance", "tel": "80 00 11 22", "commune": "COMMUNE I", "ville": "Zinder"},
        {"nom": "PHARMACIE MARADI NORD", "adresse": "Route de Niamey", "tel": "80 00 33 44", "commune": "COMMUNE I", "ville": "Maradi"},
        {"nom": "PHARMACIE TAHOUA", "adresse": "Boulevard de la Paix", "tel": "80 00 55 66", "commune": "COMMUNE I", "ville": "Tahoua"},
        {"nom": "PHARMACIE DOSSO", "adresse": "Avenue du Niger", "tel": "80 00 77 88", "commune": "COMMUNE I", "ville": "Dosso"},
        {"nom": "PHARMACIE AGADEZ", "adresse": "Route de l'Aéroport", "tel": "80 00 99 00", "commune": "COMMUNE I", "ville": "Agadez"},
    ]

    pharmacies_db = []
    for idx, p in enumerate(pharmacy_data, start=1):
        pharmacies_db.append({
            "id": idx,
            "nom": p["nom"],
            "adresse": p["adresse"],
            "tel": p["tel"],
            "commune": p.get("commune", "COMMUNE I"),
            "ville": p.get("ville", "Niamey"),
            "est_de_garde": False
        })
    st.session_state.pharmacies_db = pharmacies_db

# ==============================================================================
# STOCK : DISPONIBILITÉ DES MÉDICAMENTS PAR PHARMACIE
# ==============================================================================
if "stock_db" not in st.session_state:
    stock_db = {}
    for med in st.session_state.meds_db:
        for pharm in st.session_state.pharmacies_db:
            stock_db[(med["nom"], pharm["id"])] = True
    st.session_state.stock_db = stock_db

# ==============================================================================
# STYLES CSS (thème clair/sombre et design amélioré)
# ==============================================================================
def apply_theme(theme):
    if theme == "sombre":
        return """
        <style>
            /* Thème sombre */
            .stApp { background: #0f0f1a !important; color: #e0e0e0; }
            .card, .stButton > button, .stTextInput > div > div > input, .stSelectbox > div > div, .chat-message-assistant {
                background: #1a1a2e !important;
                color: #e0e0e0 !important;
                border: 1px solid #2a2a4e !important;
                border-radius: 16px !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            }
            .card:hover { background: #22224a !important; transform: translateY(-2px); }
            .header-main { background: linear-gradient(135deg, #1a2a5a 0%, #0f1a2e 100%) !important; border-radius: 20px; }
            .footer { border-top-color: #2a2a4e !important; }
            .statut-garde { background: #1a4a2a !important; color: #8fdf8f !important; }
            .statut-non-garde { background: #4a1a1a !important; color: #ff8f8f !important; }
            .notice-box { background: #1a2a3e !important; border-color: #2a3a5e !important; }
            .chat-message-user { background: #2a4a3e !important; color: #e0e0e0 !important; }
            .sidebar-logo .sidebar-title { color: #7fdb9f !important; }
            .sidebar-logo .sidebar-subtitle { color: #a0b0c0 !important; }
            .stButton > button:hover { background: #2a4a6e !important; border-left-color: #7fdb9f !important; }
            .commune-tag { background: #2a5a7a !important; }
            .card-pharma .tel { color: #7fdbcf !important; }
            .card-med .price { color: #ffb347 !important; }
            .badge-count { background: #2a6a4a !important; }
            .footer a { color: #7fdb9f !important; }
            .stSelectbox label, .stTextInput label { color: #c0c0d0 !important; }
        </style>
        """
    else:
        return """
        <style>
            /* Thème clair amélioré */
            .stApp { background: linear-gradient(145deg, #f0f4f3 0%, #e6eceb 100%) !important; }
            .card, .stButton > button, .stTextInput > div > div > input, .stSelectbox > div > div, .chat-message-assistant {
                background: white !important;
                color: #1e2e2e !important;
                border-radius: 16px !important;
                border: 1px solid rgba(0,0,0,0.04) !important;
                box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
                transition: all 0.2s ease;
            }
            .card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important; transform: translateY(-2px); }
            .header-main {
                background: linear-gradient(135deg, #2b9348 0%, #007f5f 100%) !important;
                border-radius: 24px !important;
                box-shadow: 0 10px 30px -10px rgba(0,80,50,0.3) !important;
            }
            .statut-garde { background: #d4edda !important; color: #155724 !important; }
            .statut-non-garde { background: #f8d7da !important; color: #721c24 !important; }
            .notice-box { background: #f8f9fa !important; border-color: #e9ecef !important; }
            .chat-message-user { background: #eaf5ef !important; color: #1a2e2a !important; }
            .sidebar-logo .sidebar-title { color: #2b9348 !important; }
            .sidebar-logo .sidebar-subtitle { color: #6b7a7a !important; }
            .stButton > button:hover { background: #eaf5ef !important; border-left-color: #2b9348 !important; }
            .commune-tag { background: #005f73 !important; }
            .card-pharma .tel { color: #005f73 !important; }
            .card-med .price { color: #d97706 !important; }
            .badge-count { background: #2b9348 !important; }
            .footer a { color: #2b9348 !important; }
            .stSelectbox label, .stTextInput label { color: #3a4a4a !important; font-weight: 500; }
        </style>
        """

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================
def navigate(page):
    st.session_state.page = page
    st.rerun()

def actualiser_prix_medicaments():
    try:
        url = "https://www.lahiya-tech.com/les-pharmacies-de-niamey/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        pattern = r'([A-Z0-9\s]+)\s+(\d+[\s,]*\d*)\s*(FCFA|CFA|Franc)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        prix_trouves = {}
        for match in matches:
            nom = match[0].strip()
            prix_str = match[1].replace(' ', '').replace(',', '')
            try:
                prix = int(prix_str)
                prix_trouves[nom[:50]] = prix
            except ValueError:
                continue
        nb_updated = 0
        for med in st.session_state.meds_db:
            for nom_site, prix in prix_trouves.items():
                if any(mot in med['nom'].upper() for mot in nom_site.upper().split()[:3]):
                    if med['prix_fcfa'] != prix:
                        med['prix_fcfa'] = prix
                        nb_updated += 1
                    break
        return nb_updated, len(prix_trouves)
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        return 0, 0

# ==============================================================================
# APPLICATION DU THÈME
# ==============================================================================
theme_css = apply_theme(st.session_state.theme)
st.markdown(theme_css, unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR AVEC SÉLECTEUR DE VILLE
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span>🇳🇪</span>
        <h2 class="sidebar-title">PharmaNiger</h2>
        <p class="sidebar-subtitle">Santé publique </p>
    </div>
    """.format(len(st.session_state.meds_db)), unsafe_allow_html=True)
    st.markdown("<hr class='sidebar-sep'>", unsafe_allow_html=True)

    # Sélecteur de ville (global dans la sidebar)
    villes = ["Toutes les villes"] + sorted(list(set(p["ville"] for p in st.session_state.pharmacies_db)))
    st.session_state.ville_filter = st.selectbox("📍 Choisir une ville", villes, index=villes.index(st.session_state.ville_filter))

    if st.button("🏠 Accueil", key="nav_accueil"):
        navigate("Accueil")

    st.markdown("<div class='sidebar-section'>🏥 Pharmacies</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Garde", key="nav_garde"):
            navigate("Pharmacies de Garde")
    with col2:
        if st.button("🏥 Toutes", key="nav_all"):
            navigate("Toutes les Pharmacies")

    st.markdown("<div class='sidebar-section'>💊 Médicaments</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Prix & Notices", key="nav_meds"):
            navigate("Prix des Médicaments")
        if st.button("📦 Stocks", key="nav_stock"):
            navigate("Gestion Médicaments")
    with col2:
        if st.button("📊 Gestion", key="nav_gestion"):
            navigate("Gestion Médicaments")

    st.markdown("<div class='sidebar-section'>🛠️ Outils</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Chat", key="nav_chat"):
            navigate("Chatbot")
        if st.button("⚙️ Mise à jour", key="nav_maj"):
            navigate("Mise à jour de la Garde")
    with col2:
        if st.button("🆘 Conseils", key="nav_conseils"):
            navigate("Conseils Santé")
        if st.button("📤 Export", key="nav_export"):
            navigate("Export")

    st.markdown("<div class='sidebar-section'>📊 Dashboard</div>", unsafe_allow_html=True)
    if st.button("📈 Tableau de bord", key="nav_dashboard"):
        navigate("Dashboard")

    st.markdown("<div class='sidebar-section'>💬 Retour</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Feedback", key="nav_feedback"):
            navigate("Feedback")
    with col2:
        if st.button("👨‍💻 À propos", key="nav_about"):
            navigate("A propos de l'auteur...")

    st.markdown("---")
    if st.button("🌓 Changer de thème", use_container_width=True):
        st.session_state.theme = "sombre" if st.session_state.theme == "clair" else "clair"
        st.rerun()

# ==============================================================================
# PAGES
# ==============================================================================

# ------------------------------------------------------------------------------
# ACCUEIL
# ------------------------------------------------------------------------------
if st.session_state.page == "Accueil":
    st.markdown("""
    <div class="header-main">
        <h1>💊 PharmaNiger</h1>
        <p>Votre santé, notre priorité. Retrouvez toutes les pharmacies de garde et les prix des médicaments au Niger.</p>
        <span class="header-badge">🇳🇪 {} • {} pharmacies</span>
    </div>
    """.format(st.session_state.ville_filter, len(st.session_state.pharmacies_db)), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Pharmacies de garde", use_container_width=True):
            navigate("Pharmacies de Garde")
        if st.button("💊 Prix & Notices", use_container_width=True):
            navigate("Prix des Médicaments")
        if st.button("🆘 Conseils Santé", use_container_width=True):
            navigate("Conseils Santé")
    with col2:
        if st.button("📦 Gestion des stocks", use_container_width=True):
            navigate("Gestion Médicaments")
        if st.button("💬 PharmaBot", use_container_width=True):
            navigate("Chatbot")
        if st.button("📈 Dashboard", use_container_width=True):
            navigate("Dashboard")
    st.markdown("---")
    st.caption(f"Dernière mise à jour : {date.today().strftime('%d/%m/%Y')}  |  {len(st.session_state.meds_db)} médicaments référencés")

# ------------------------------------------------------------------------------
# PHARMACIES DE GARDE avec filtres (ville + commune)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Pharmacies de Garde":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #005f73 0%, #0a3a4a 100%);">
        <h2 style="margin:0;">🟢 Pharmacies de garde</h2>
        <p style="margin:4px 0 0 0;">Service de nuit et jours fériés</p>
    </div>
    """, unsafe_allow_html=True)
    # Filtrer par ville sélectionnée
    if st.session_state.ville_filter != "Toutes les villes":
        gardes_actives = [p for p in st.session_state.pharmacies_db if p.get("est_de_garde", True) and p["ville"] == st.session_state.ville_filter]
    else:
        gardes_actives = [p for p in st.session_state.pharmacies_db if p.get("est_de_garde", True)]

    communes = ["Toutes les Communes"] + sorted(list(set(p["commune"] for p in gardes_actives)))
    if "commune_filter" not in st.session_state:
        st.session_state.commune_filter = "Toutes les Communes"

    col_filtre, col_search = st.columns([1, 2])
    with col_filtre:
        filtre_commune = st.selectbox("📌 Commune", communes, index=communes.index(st.session_state.commune_filter))
        st.session_state.commune_filter = filtre_commune
    with col_search:
        search = st.text_input("🔍 Rechercher", placeholder="Nom ou adresse...")

    pharma_filtrees = gardes_actives
    if filtre_commune != "Toutes les Communes":
        pharma_filtrees = [p for p in pharma_filtrees if p["commune"] == filtre_commune]
    if search:
        pharma_filtrees = [p for p in pharma_filtrees if search.lower() in p["nom"].lower() or search.lower() in p["adresse"].lower()]

    st.markdown(f"<div class='flex-center'><span style='font-weight:600;'>Résultats :</span> <span class='badge-count'>{len(pharma_filtrees)}</span></div>", unsafe_allow_html=True)
    for p in pharma_filtrees:
        tel_aff = p['tel'] if p['tel'] else "N/A"
        est_favori = p['id'] in st.session_state.favoris
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="card card-pharma">
                <span class="commune-tag">{p['commune']} • {p['ville']}</span>
                <h4>🏥 PHARMACIE {p['nom']} {'⭐' if est_favori else ''}</h4>
                <p style="margin:4px 0;">📍 {p['adresse'] if p['adresse'] else 'Adresse non précisée'}</p>
                <p style="margin:2px 0;">📞 {f'<a href="tel:+227{str(p["tel"]).replace(" ", "")}" class="tel">+227 {p["tel"]}</a>' if p['tel'] else '📞 N/A'}</p>
                <span class="statut statut-garde">✅ De garde</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("⭐" if not est_favori else "⭐", key=f"fav_{p['id']}"):
                if p['id'] in st.session_state.favoris:
                    st.session_state.favoris.remove(p['id'])
                else:
                    st.session_state.favoris.append(p['id'])
                save_favoris(st.session_state.favoris)
                st.toast("⭐ Favoris mis à jour", icon="⭐")
                st.rerun()

# ------------------------------------------------------------------------------
# TOUTES LES PHARMACIES avec filtres (ville + commune)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Toutes les Pharmacies":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #2b9348 0%, #007f5f 100%);">
        <h2 style="margin:0;">🏥 Toutes les pharmacies</h2>
        <p style="margin:4px 0 0 0;">Liste complète des officines</p>
    </div>
    """, unsafe_allow_html=True)

    # Filtrer par ville sélectionnée
    if st.session_state.ville_filter != "Toutes les villes":
        pharma_base = [p for p in st.session_state.pharmacies_db if p["ville"] == st.session_state.ville_filter]
    else:
        pharma_base = st.session_state.pharmacies_db

    communes = ["Toutes les Communes"] + sorted(list(set(p["commune"] for p in pharma_base)))
    if "commune_filter" not in st.session_state:
        st.session_state.commune_filter = "Toutes les Communes"

    col_filtre, col_search = st.columns([1, 2])
    with col_filtre:
        filtre_commune = st.selectbox("📌 Commune", communes, index=communes.index(st.session_state.commune_filter))
        st.session_state.commune_filter = filtre_commune
    with col_search:
        search = st.text_input("🔍 Rechercher", placeholder="Nom ou adresse...")

    pharma_filtrees = pharma_base
    if filtre_commune != "Toutes les Communes":
        pharma_filtrees = [p for p in pharma_filtrees if p["commune"] == filtre_commune]
    if search:
        pharma_filtrees = [p for p in pharma_filtrees if search.lower() in p["nom"].lower() or search.lower() in p["adresse"].lower()]

    st.markdown(f"<div class='flex-center'><span style='font-weight:600;'>Résultats :</span> <span class='badge-count'>{len(pharma_filtrees)}</span></div>", unsafe_allow_html=True)
    for p in pharma_filtrees:
        statut_classe = "statut-garde" if p.get("est_de_garde", True) else "statut-non-garde"
        statut_texte = "✅ De garde" if p.get("est_de_garde", True) else "❌ Pas de garde"
        tel_link = f'<a href="tel:+227{str(p["tel"]).replace(" ", "")}" class="tel">+227 {p["tel"]}</a>' if p['tel'] else '📞 N/A'
        est_favori = p['id'] in st.session_state.favoris
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="card card-pharma">
                <span class="commune-tag">{p['commune']} • {p['ville']}</span>
                <h4>🏥 PHARMACIE {p['nom']} {'⭐' if est_favori else ''}</h4>
                <p style="margin:4px 0;">📍 {p['adresse'] if p['adresse'] else 'Adresse non précisée'}</p>
                <p style="margin:2px 0;">📞 {tel_link}</p>
                <span class="statut {statut_classe}">{statut_texte}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("⭐" if not est_favori else "⭐", key=f"fav_all_{p['id']}"):
                if p['id'] in st.session_state.favoris:
                    st.session_state.favoris.remove(p['id'])
                else:
                    st.session_state.favoris.append(p['id'])
                save_favoris(st.session_state.favoris)
                st.toast("⭐ Favoris mis à jour", icon="⭐")
                st.rerun()

# ------------------------------------------------------------------------------
# PRIX DES MÉDICAMENTS (identique)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Prix des Médicaments":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #e76f51 0%, #c85a3a 100%);">
        <h2 style="margin:0;">💊 Prix des médicaments</h2>
        <p style="margin:4px 0 0 0;">Filtrer par catégorie – cliquez sur la notice pour les détails</p>
    </div>
    """, unsafe_allow_html=True)
    categories = ["Toutes"] + sorted(list(set(m["categorie"] for m in st.session_state.meds_db)))
    col_cat, col_search = st.columns([1, 2])
    with col_cat:
        cat_choisie = st.selectbox("📂 Catégorie", categories)
    with col_search:
        q = st.text_input("🔍 Rechercher", placeholder="ex: paracetamol...")
    meds = st.session_state.meds_db
    if cat_choisie != "Toutes":
        meds = [m for m in meds if m["categorie"] == cat_choisie]
    if q:
        meds = [m for m in meds if q.lower() in m['nom'].lower() or q.lower() in m.get('indications', '').lower()]
    st.markdown(f"<div class='flex-center'><span style='font-weight:600;'>Médicaments trouvés :</span> <span class='badge-count'>{len(meds)}</span></div>", unsafe_allow_html=True)
    for m in meds:
        with st.container():
            st.markdown(f"""
            <div class="card card-med">
                <h4 style="color:#1a3a2a; margin:0;">💊 {m['nom']}</h4>
                <p class="price">{m['prix_fcfa']:,} FCFA</p>
                <p class="notice">📋 <b>Indications :</b> {m.get('indications', 'Non renseigné')}</p>
                <span style="background:#e9ecef; padding:2px 10px; border-radius:30px; font-size:0.7rem;">{m['categorie']}</span>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📖 Notice complète - {m['nom']}"):
                st.markdown(f"""
                <div class="notice-box">
                    <h5>💡 Indications</h5>
                    <p>{m.get('indications', 'Non renseigné')}</p>
                    <h5>🧑 Adulte</h5>
                    <p>{m.get('posologie_adulte', 'Non renseigné')}</p>
                    <h5>🧒 Enfant</h5>
                    <p>{m.get('posologie_enfant', 'Non renseigné')}</p>
                    <h5>⚠️ Contre-indications</h5>
                    <p>{m.get('contre_indications', 'Non renseigné')}</p>
                </div>
                """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# GESTION DES STOCKS (identique)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Gestion Médicaments":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #6f42c1 0%, #4a2d7a 100%);">
        <h2 style="margin:0;">📦 Gestion des stocks</h2>
        <p style="margin:4px 0 0 0;">Consultez et modifiez la disponibilité de chaque médicament par pharmacie</p>
    </div>
    """, unsafe_allow_html=True)

    categories = ["Toutes"] + sorted(list(set(m["categorie"] for m in st.session_state.meds_db)))
    col_cat, col_search = st.columns([1, 2])
    with col_cat:
        cat_choisie = st.selectbox("📂 Catégorie", categories)
    with col_search:
        q = st.text_input("🔍 Rechercher un médicament", placeholder="Nom...")

    communes = ["Toutes les Communes"] + sorted(list(set(p["commune"] for p in st.session_state.pharmacies_db)))
    commune_choisie = st.selectbox("📍 Filtrer les pharmacies par commune", communes)

    meds_affiches = st.session_state.meds_db
    if cat_choisie != "Toutes":
        meds_affiches = [m for m in meds_affiches if m["categorie"] == cat_choisie]
    if q:
        meds_affiches = [m for m in meds_affiches if q.lower() in m["nom"].lower()]

    pharmacies_filtrees = st.session_state.pharmacies_db
    if commune_choisie != "Toutes les Communes":
        pharmacies_filtrees = [p for p in pharmacies_filtrees if p["commune"] == commune_choisie]

    med_noms = [m["nom"] for m in meds_affiches]
    pharm_noms = [p["nom"] for p in pharmacies_filtrees]
    data = []
    for med in meds_affiches:
        row = {}
        for pharm in pharmacies_filtrees:
            key = (med["nom"], pharm["id"])
            row[pharm["nom"]] = st.session_state.stock_db.get(key, False)
        data.append(row)

    df = pd.DataFrame(data, index=med_noms).fillna(False)

    st.write("Cochez pour indiquer la disponibilité du médicament dans la pharmacie.")
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        column_config={
            col: st.column_config.CheckboxColumn(
                label=col,
                help=f"Disponible dans la pharmacie {col}",
                default=False,
            ) for col in df.columns
        },
        num_rows="fixed"
    )

    if st.button("💾 Enregistrer les modifications", use_container_width=True):
        for med_nom in edited_df.index:
            for pharm_nom in edited_df.columns:
                nouvelle_valeur = edited_df.loc[med_nom, pharm_nom]
                pharm_id = None
                for p in st.session_state.pharmacies_db:
                    if p["nom"] == pharm_nom:
                        pharm_id = p["id"]
                        break
                if pharm_id is not None:
                    key = (med_nom, pharm_id)
                    st.session_state.stock_db[key] = bool(nouvelle_valeur)
        st.toast("✅ Stocks mis à jour", icon="💊")
        st.balloons()

# ------------------------------------------------------------------------------
# CHATBOT (identique)
# ------------------------------------------------------------------------------
elif st.session_state.page == "Chatbot":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #6c4a9e 0%, #4a2d7a 100%);">
        <h2 style="margin:0;">💬 PharmaBot</h2>
        <p style="margin:4px 0 0 0;">Posez votre question ou cliquez sur un raccourci ci-dessous</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🟢 Pharmacies de garde", use_container_width=True):
            prompt = "Quelles sont les pharmacies de garde aujourd'hui ?"
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            gardes = [p for p in st.session_state.pharmacies_db if p.get("est_de_garde", True)]
            if gardes:
                noms = ", ".join([f"{p['nom']} ({p['commune']})" for p in gardes[:5]])
                reponse = f"🟢 **Pharmacies de garde actuellement :**\n\n{noms}\n\n📞 Consultez la page 'Pharmacies de garde' pour plus de détails."
            else:
                reponse = "Aucune pharmacie de garde trouvée pour le moment."
            st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
            st.rerun()
    with col2:
        if st.button("💊 Prix du paracétamol", use_container_width=True):
            prompt = "Quel est le prix du paracétamol ?"
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            for med in st.session_state.meds_db:
                if "PARACETAMOL" in med["nom"]:
                    reponse = f"💊 **{med['nom']}** : {med['prix_fcfa']:,} FCFA"
                    break
            else:
                reponse = "Médicament non trouvé."
            st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
            st.rerun()
    with col3:
        if st.button("🧑 Posologie pour enfant", use_container_width=True):
            prompt = "Posologie du paracétamol pour enfant"
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            for med in st.session_state.meds_db:
                if "PARACETAMOL" in med["nom"]:
                    reponse = f"🧒 **{med['nom']}**\n\nPosologie enfant : {med.get('posologie_enfant', 'Non renseigné')}"
                    break
            else:
                reponse = "Médicament non trouvé."
            st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
            st.rerun()

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"<div style='display:flex; justify-content:flex-end;'><div class='chat-message-user'>{msg['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='display:flex; justify-content:flex-start;'><div class='chat-message-assistant'>{msg['content']}</div></div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Écrivez votre message..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.markdown(f"<div style='display:flex; justify-content:flex-end;'><div class='chat-message-user'>{prompt}</div></div>", unsafe_allow_html=True)

        prompt_lower = prompt.lower()
        reponse = ""
        medicament_trouve = None
        for med in st.session_state.meds_db:
            if med['nom'].lower() in prompt_lower or any(mot in prompt_lower for mot in med['nom'].lower().split()):
                medicament_trouve = med
                break

        if medicament_trouve:
            med = medicament_trouve
            if "posologie" in prompt_lower or "dose" in prompt_lower or "prendre" in prompt_lower:
                reponse = f"💊 **{med['nom']}**\n\n📋 **Indications :** {med.get('indications', 'Non renseigné')}\n\n🧑 **Adulte :** {med.get('posologie_adulte', 'Non renseigné')}\n\n🧒 **Enfant :** {med.get('posologie_enfant', 'Non renseigné')}\n\n⚠️ **Contre-indications :** {med.get('contre_indications', 'Non renseigné')}"
            elif "prix" in prompt_lower or "coût" in prompt_lower or "combien" in prompt_lower:
                reponse = f"💊 **{med['nom']}** : {med['prix_fcfa']:,} FCFA"
            else:
                reponse = f"💊 **{med['nom']}**\n\n📋 **Indications :** {med.get('indications', 'Non renseigné')}\n\n💰 **Prix :** {med['prix_fcfa']:,} FCFA\n\n🧑 **Adulte :** {med.get('posologie_adulte', 'Non renseigné')}\n\n🧒 **Enfant :** {med.get('posologie_enfant', 'Non renseigné')}\n\n⚠️ **Contre-indications :** {med.get('contre_indications', 'Non renseigné')}"
        elif "pharmacie" in prompt_lower or "garde" in prompt_lower:
            gardes = [p for p in st.session_state.pharmacies_db if p.get("est_de_garde", True)]
            if gardes:
                noms = ", ".join([f"{p['nom']} ({p['commune']})" for p in gardes[:5]])
                reponse = f"🟢 **Pharmacies de garde actuellement :**\n\n{noms}\n\n📞 Consultez la page 'Pharmacies de garde' pour plus de détails."
            else:
                reponse = "Aucune pharmacie de garde trouvée pour le moment."
        elif "prix" in prompt_lower or "coût" in prompt_lower or "tarif" in prompt_lower:
            mots_cles = prompt_lower.split()
            for med in st.session_state.meds_db:
                if any(mot in med['nom'].lower() for mot in mots_cles if len(mot) > 3):
                    reponse = f"💊 **{med['nom']}** : {med['prix_fcfa']:,} FCFA"
                    break
            if not reponse:
                reponse = "🔍 Pour connaître les prix, utilisez la page 'Prix des médicaments' avec la recherche."
        elif any(mot in prompt_lower for mot in ["bonjour", "salut", "coucou"]):
            reponse = "👋 Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        elif "merci" in prompt_lower:
            reponse = "🙏 Je vous en prie !"
        else:
            reponse = "❓ Je n'ai pas bien compris votre question. Je peux vous aider sur les médicaments (posologie, prix), les pharmacies de garde, ou les contre-indications."

        st.session_state.chat_messages.append({"role": "assistant", "content": reponse})
        st.markdown(f"<div style='display:flex; justify-content:flex-start;'><div class='chat-message-assistant'>{reponse}</div></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# CONSEILS SANTÉ
# ------------------------------------------------------------------------------
elif st.session_state.page == "Conseils Santé":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #1a8c6e 0%, #0e6b4f 100%);">
        <h2 style="margin:0;">🆘 Conseils Santé</h2>
        <p style="margin:4px 0 0 0;">Premiers secours, hygiène, et bonnes pratiques</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("🚑 Premiers secours – que faire en cas d'urgence ?", expanded=False):
        st.markdown("""
        - **Hémorragie** : Appuyer fortement sur la plaie avec un linge propre, surélever le membre, appeler les secours.
        - **Brûlure** : Refroidir immédiatement sous l'eau fraîche (pas glacée) pendant 15 minutes, couvrir d'un pansement stérile, ne pas percer les cloques.
        - **Malaise / perte de connaissance** : Allonger la personne sur le côté (position latérale de sécurité), dégager les voies respiratoires, appeler les secours.
        - **Ingestion de poison** : Ne pas faire vomir, contacter un centre antipoison ou se rendre aux urgences.
        """)
    with st.expander("💧 Hydratation et alimentation", expanded=False):
        st.markdown("""
        - Boire au moins **1,5 litre d'eau par jour** (plus en cas de chaleur ou d'effort).
        - Privilégier une alimentation riche en fruits et légumes, réduire le sel et le sucre.
        - En cas de diarrhée ou vomissements, boire des solutions de réhydratation orale (SRO).
        """)
    with st.expander("🌡️ Fièvre – quand s'inquiéter ?", expanded=False):
        st.markdown("""
        - **Température > 38,5°C** : Prendre du paracétamol ou de l'ibuprofène (selon les recommandations).
        - Si la fièvre persiste plus de **48 heures** ou s'accompagne de signes graves (difficulté respiratoire, éruption cutanée, raideur de la nuque), consulter un médecin.
        - Chez le nourrisson de moins de 3 mois, toute fièvre > 38°C nécessite un avis médical urgent.
        """)
    with st.expander("💊 Bien utiliser les médicaments", expanded=False):
        st.markdown("""
        - Respecter les **posologies** indiquées sur la notice ou prescrites par le médecin.
        - Ne pas **mixer** plusieurs antalgiques sans avis médical.
        - Les antibiotiques doivent être pris **jusqu'au bout** même si les symptômes disparaissent.
        - Vérifier les **dates de péremption** avant toute prise.
        """)
    with st.expander("🧼 Hygiène et prévention", expanded=False):
        st.markdown("""
        - Se laver les mains régulièrement (eau + savon, ou gel hydroalcoolique).
        - Se brosser les dents deux fois par jour.
        - Utiliser des moustiquaires pour prévenir le paludisme.
        - Se protéger du soleil avec un chapeau et de la crème solaire.
        """)
    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ------------------------------------------------------------------------------
# MISE À JOUR DE LA GARDE
# ------------------------------------------------------------------------------
elif st.session_state.page == "Mise à jour de la Garde":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #d97706 0%, #b45309 100%);">
        <h2 style="margin:0;">⚙️ Mise à jour du planning</h2>
        <p style="margin:4px 0 0 0;">Consultez la liste officielle, modifiez les statuts ou actualisez les prix</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🌐 Consulter la source officielle")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("Ouvrez le site de référence pour voir la liste à jour des pharmacies de garde.")
    with col2:
        if st.button("🔗 Ouvrir le site", use_container_width=True):
            webbrowser.open("https://www.medic-rdv.com/rdv/pharmacidegarde")
            st.toast("✅ Page ouverte dans votre navigateur", icon="🌐")
    st.markdown("---")
    st.markdown("### ✏️ Édition manuelle des statuts")
    st.info("💡 Basculez manuellement le statut de chaque pharmacie.")
    communes = ["Toutes les Communes"] + sorted(list(set(p["commune"] for p in st.session_state.pharmacies_db)))
    col_filtre, col_search = st.columns([1, 2])
    with col_filtre:
        filtre_commune = st.selectbox("📌 Filtrer par commune", communes)
    with col_search:
        search = st.text_input("🔍 Rechercher (nom ou adresse)", placeholder="ex: 7 THERAPIES...")
    pharma_affichees = st.session_state.pharmacies_db
    if filtre_commune != "Toutes les Communes":
        pharma_affichees = [p for p in pharma_affichees if p["commune"] == filtre_commune]
    if search:
        pharma_affichees = [p for p in pharma_affichees if search.lower() in p["nom"].lower() or search.lower() in p["adresse"].lower()]
    if not pharma_affichees:
        st.warning("Aucune pharmacie ne correspond à vos critères.")
    else:
        st.write(f"**{len(pharma_affichees)}** pharmacie(s) affichée(s)")
        for p in pharma_affichees:
            col_info, col_bouton = st.columns([4, 1])
            with col_info:
                statut_actuel = p.get("est_de_garde", True)
                statut_texte = "✅ De garde" if statut_actuel else "❌ Pas de garde"
                tel_aff = p['tel'] if p['tel'] else "N/A"
                adresse_aff = p['adresse'] if p['adresse'] else "Adresse non précisée"
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px; background: white; padding: 10px 15px; border-radius: 12px; margin-bottom: 6px; border-left: 4px solid {'#2b9348' if statut_actuel else '#d9534f'};">
                    <div style="flex:1;">
                        <strong style="color:#1a3a2a;">🏥 {p['nom']}</strong><br>
                        <span style="font-size:0.85rem; color:#4b5e5e;">📍 {adresse_aff} &nbsp;|&nbsp; 📞 {tel_aff}</span><br>
                        <span style="font-size:0.8rem; background: {'#d4edda' if statut_actuel else '#f8d7da'}; padding:2px 10px; border-radius:30px; color: {'#155724' if statut_actuel else '#721c24'};">
                            {statut_texte}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_bouton:
                if st.button("✅" if statut_actuel else "❌", key=f"toggle_{p['id']}", use_container_width=True):
                    p["est_de_garde"] = not statut_actuel
                    st.toast(f"Statut de {p['nom']} mis à jour", icon="🔄")
                    st.rerun()
    st.markdown("---")
    st.markdown("### 📊 Actualisation automatique des prix")
    if st.button("🔄 Actualiser les prix des médicaments", use_container_width=True):
        with st.spinner("⏳ Récupération en cours..."):
            nb_updated, nb_trouves = actualiser_prix_medicaments()
            if nb_updated > 0:
                st.toast(f"✅ {nb_updated} médicaments mis à jour", icon="💰")
                st.balloons()
            else:
                st.warning(f"⚠️ Aucun médicament mis à jour. {nb_trouves} prix trouvés sur le site.")
    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ------------------------------------------------------------------------------
# EXPORT
# ------------------------------------------------------------------------------
elif st.session_state.page == "Export":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);">
        <h2 style="margin:0;">📤 Exporter les données</h2>
        <p style="margin:4px 0 0 0;">Téléchargez la liste des médicaments ou des pharmacies</p>
    </div>
    """, unsafe_allow_html=True)
    choix = st.radio("Choisissez les données à exporter :", ["Médicaments", "Pharmacies"])
    if choix == "Médicaments":
        df = pd.DataFrame(st.session_state.meds_db)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Télécharger les médicaments (CSV)",
            data=csv,
            file_name="medicaments_niger.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        df = pd.DataFrame(st.session_state.pharmacies_db)
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Télécharger les pharmacies (CSV)",
            data=csv,
            file_name="pharmacies_niger.csv",
            mime="text/csv",
            use_container_width=True
        )
    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ------------------------------------------------------------------------------
# FEEDBACK
# ------------------------------------------------------------------------------
elif st.session_state.page == "Feedback":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #e83e8c 0%, #c12b6e 100%);">
        <h2 style="margin:0;">💬 Retour / Suggestion</h2>
        <p style="margin:4px 0 0 0;">Signalez une erreur, proposez une amélioration</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("feedback_form"):
        nom = st.text_input("Votre nom (facultatif)")
        email = st.text_input("Votre email (facultatif)")
        categorie = st.selectbox("Type de retour", ["Signalement d'erreur", "Suggestion d'amélioration", "Question", "Autre"])
        message = st.text_area("Votre message", height=150)
        submitted = st.form_submit_button("📨 Envoyer")
        if submitted:
            st.toast("✅ Merci pour votre retour !", icon="🙏")
    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ------------------------------------------------------------------------------
# À PROPOS
# ------------------------------------------------------------------------------
elif st.session_state.page == "A propos de l'auteur...":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #1a3a2a 0%, #0f2a1e 100%);">
        <h2 style="margin:0;">👨‍💻 À propos de l'auteur</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="text-align:center; padding:2rem;">
        <div style="font-size:60px; margin-bottom:10px;">🇳🇪</div>
        <h3 style="color:#2b9348;">Amady Pabame</h3>
        <p><strong>Spécialité :</strong><br>Doctorant en Mathématiques & Ingénieur en Intelligence Artificielle (Data Science appliquée)</p>
        <hr style="width:50%; margin: 20px auto;">
        <p style="color:#6b7a7a;">Cette application a été développée pour faciliter l'accès aux informations de santé publique au Niger.</p>
        <p style="color:#6b7a7a; font-size:0.9rem;">Développé avec ❤️ et Streamlit</p>
        <p style="color:#6b7a7a; font-size:0.9rem;">Version 2.5 – 2026</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ------------------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------------------
elif st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="header-main" style="background: linear-gradient(135deg, #0b5e7c 0%, #0a3a4a 100%);">
        <h2 style="margin:0;">📈 Tableau de bord</h2>
        <p style="margin:4px 0 0 0;">Statistiques et indicateurs clés</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏥 Pharmacies", len(st.session_state.pharmacies_db))
    col2.metric("💊 Médicaments", len(st.session_state.meds_db))
    gardes = len([p for p in st.session_state.pharmacies_db if p.get("est_de_garde", False)])
    col3.metric("🟢 En garde", gardes)
    col4.metric("⭐ Favoris", len(st.session_state.favoris))

    st.markdown("---")
    st.subheader("🏷️ Répartition par catégorie de médicaments")
    cat_counts = {}
    for med in st.session_state.meds_db:
        cat = med["categorie"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Catégorie", "Nombre"])
    st.bar_chart(df_cat.set_index("Catégorie"))

    st.subheader("📍 Pharmacies par commune")
    comm_counts = {}
    for pharm in st.session_state.pharmacies_db:
        comm = pharm["commune"]
        comm_counts[comm] = comm_counts.get(comm, 0) + 1
    df_comm = pd.DataFrame(list(comm_counts.items()), columns=["Commune", "Nombre"])
    st.bar_chart(df_comm.set_index("Commune"))

    if st.button("⬅ Retour à l'accueil"):
        navigate("Accueil")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div class="footer">
    PharmaNiger Pro v2.5 — © 2026 · <a href="#">Amady Pabame</a> · Tous droits réservés 🇳🇪
</div>
""", unsafe_allow_html=True)