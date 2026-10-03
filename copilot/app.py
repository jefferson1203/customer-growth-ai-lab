"""
copilot/app.py - Interface Streamlit interactive pour le Copilote Commercial Multi-Modèle.
- Choix du LLM Provider (Gemini, Claude, ChatGPT, DeepSeek) + Saisie de la clé API personnelle.
- Consultation du profil client, historique et opportunités.
- Validation d'offre commerciale avec garde-fous déterministes et Escalade Humaine.
- Historique de décisions enregistré dans outputs/copilot/decisions.csv.
"""

import os
import csv
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

from copilot.agent import CommercialAgentEngine

st.set_page_config(
    page_title="Copilote Commercial AI - Customer Growth Lab",
    layout="wide"
)

# Initialisation du fichier de log des décisions
DECISIONS_FILE = Path(__file__).parent.parent / "outputs" / "copilot" / "decisions.csv"
DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

if not DECISIONS_FILE.exists():
    with open(DECISIONS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "customer_id", "stock_code", "proposed_discount_pct", "status", "approved_by", "llm_provider"])


def log_decision(customer_id: str, stock_code: str, proposed_discount_pct: float, status: str, approved_by: str, provider: str):
    """Enregistre une décision d'offre commerciale dans le journal d'audit."""
    with open(DECISIONS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_id,
            stock_code,
            proposed_discount_pct,
            status,
            approved_by,
            provider
        ])


# --- SIDEBAR : CONFIGURATION MULTI-PROVIDER LLM ---
st.sidebar.title("Configuration du Copilote")
st.sidebar.markdown("---")

provider = st.sidebar.selectbox(
    "Fournisseur LLM",
    ["Gemini (Google)", "Claude (Anthropic)", "ChatGPT (OpenAI)", "DeepSeek"],
    index=0,
    help="Choisissez le fournisseur du modèle de langage."
)

# Détermination de la valeur par défaut selon le provider choisi avec les modèles les plus récents (2026)
default_models = {
    "Gemini (Google)": "gemini-3.8-flash",
    "Claude (Anthropic)": "claude-sonnet-5.5",
    "ChatGPT (OpenAI)": "gpt-6.1-sol",
    "DeepSeek": "deepseek-v4.1-flash"
}

default_model_val = default_models.get(provider, "gemini-3.8-flash")

model_name = st.sidebar.text_input(
    "Nom du modèle LLM (Saisie libre)",
    value=default_model_val,
    help="Saisissez le nom exact du modèle (ex: gemini-3.8-flash, claude-sonnet-5.5, gpt-6.1-sol...)"
)

api_key = st.sidebar.text_input(
    "Votre clé d'API LLM",
    type="password",
    help="Saisissez votre clé d'API personnelle (Google Gemini, Anthropic, OpenAI ou DeepSeek)."
)

api_base_url = st.sidebar.text_input(
    "URL de l'API REST",
    value="http://127.0.0.1:8000",
    disabled=True,
    help="Adresse de l'API FastAPI backend déterministe (lecture seule)."
)

st.sidebar.link_button("Accéder à la Doc Swagger (OpenAPI)", "http://127.0.0.1:8000/docs#/")

st.sidebar.markdown("---")
st.sidebar.info(
    "Garde-Fou Déterministe : Les calculs financiers, prix recommandés et plafonds de remises "
    "proviennent directement de l'API FastAPI pour éradiquer toute hallucination."
)

# --- CORPS PRINCIPAL ---
st.title("Copilote Agentique & Assistant Décisionnel Commercial")
st.caption("Customer & Growth AI Lab - Système Multi-Agents pour la Négociation et l'Optimisation Tarifaire")

tab0, tab1, tab2, tab3 = st.tabs([
    "Cadrage & Recommandations",
    "Assistant & Négociation",
    "Garde-fou & Escalade",
    "Journal des Décisions"
])

with tab0:
    st.header("Cadrage Stratégique & Recommandations Copilote Agentique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Problématique & Objectifs Business")
        st.markdown("""
        - **Enjeu Commercial** : Accélérer la préparation des rendez-vous B2B (réduction de 25 min à 10 min par appel, soit **-60% de temps de préparation**).
        - **Éradication des Risques** : Sécuriser les propositions tarifaires et empêcher les sur-remises non autorisées.
        - **Gouvernance & AI Act** : Supervision humaine obligatoire (*Human-in-the-Loop*) sur tout dépassement de plafond avec journal d'audit complet.
        """)
        
    with col2:
        st.subheader("Architecture & Sécurité Déterministe")
        st.markdown("""
        - **Séparation des Responsabilités** : Le LLM assure le dialogue naturel et la synthèse, l'API FastAPI déterministe impose les règles financières à 100%.
        - **RAG Vector Store (ChromaDB)** : Interrogation de la politique commerciale de l'entreprise (`politique_commerciale.md`).
        - **Moteur Multi-LLM & Automation n8n** : Compatibilité transparente Gemini, Claude, ChatGPT, DeepSeek et workflows n8n.
        """)

    st.divider()

    st.subheader("Slides de Synthèse Stratégique Direction")
    
    SLIDES_PDF_PATH = Path("slides/Projet4_Copilote_Agentique_Slides.pdf")
    if SLIDES_PDF_PATH.exists():
        with open(SLIDES_PDF_PATH, "rb") as f_pdf:
            st.download_button(
                label="📄 Télécharger les Slides de Synthèse Stratégique Copilote Agentique (PDF A4 Paysage)",
                data=f_pdf.read(),
                file_name="Projet4_Copilote_Agentique_Slides.pdf",
                mime="application/pdf",
                help="Télécharger le support de présentation executive au format PDF A4 Paysage (3 slides)."
            )
    else:
        st.warning("Support PDF introuvable : slides/Projet4_Copilote_Agentique_Slides.pdf")

    st.divider()

    st.subheader("Plan de Déploiement Pilote & Indicateurs de Performance")
    st.info("""
    **Prochaines Étapes Opérationnelles** :
    1. **Déploiement Pilote (4 semaines)** : Test auprès d'une équipe référente de 5 commerciaux B2B.
    2. **Indicateurs de Performance (KPIs)** : Taux d'acceptation sans modification (> 80%), réduction du temps de préparation, baisse des dérogations hors plafond.
    3. **Industrialisation GCP** : Hébergement du conteneur Uvicorn + Streamlit sur Google Cloud Run avec intégration n8n.
    """)

with tab1:
    st.subheader("Discussion et Recommandations Stratégiques")
    
    col_c, col_p = st.columns(2)
    with col_c:
        cust_input = st.text_input("Identifiant Client (Customer ID)", value="10005")
    with col_p:
        prod_input = st.text_input("Code Produit (Stock Code - Optionnel)", value="22423")

    user_query = st.text_area("Votre question commerciale ou proposition de négociation :", height=100, value="Quel est le profil de ce client et quelle remise maximale puis-je lui proposer sur cet article ?")

    if st.button("Interroger le Copilote", type="primary"):
        if not api_key:
            st.error("Veuillez d'abord saisir votre clé API LLM dans la barre latérale.")
        else:
            with st.spinner("Analyse du profil, interrogation des API déterministes et RAG en cours..."):
                engine = CommercialAgentEngine(provider=provider, api_key=api_key, api_base_url=api_base_url, model_name=model_name)
                result = engine.run_query(user_query, customer_id=cust_input, stock_code=prod_input)
                
                st.markdown("### Réponse du Copilote")
                st.info(result.get("answer", "Aucune réponse générée."))

with tab2:
    st.subheader("Vérification Déterministe de Conformité & Escalade")
    st.write("Testez directement une remise commerciale contre les règles déterministes de gestion de l'entreprise.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        c_id = st.text_input("ID Client", value="10005", key="v_cid")
    with col2:
        s_code = st.text_input("StockCode Produit", value="22423", key="v_scode")
    with col3:
        disc_pct = st.number_input("Remise proposée (%)", min_value=0.0, max_value=50.0, value=12.0, step=0.5)

    if st.button("Vérifier la conformité de l'offre"):
        engine = CommercialAgentEngine(provider=provider, api_key=api_key or "demo", api_base_url=api_base_url, model_name=model_name)
        res = engine._call_api_endpoint(
            "/offres/verifier",
            method="POST",
            payload={"customer_id": c_id, "stock_code": s_code, "proposed_discount_pct": disc_pct}
        )
        if "error" in res:
            st.error(res["error"])
        else:
            st.session_state["verified_offer"] = {
                "c_id": c_id,
                "s_code": s_code,
                "disc_pct": disc_pct,
                "res": res
            }

    if "verified_offer" in st.session_state:
        vo = st.session_state["verified_offer"]
        res = vo["res"]
        c_id = vo["c_id"]
        s_code = vo["s_code"]
        disc_pct = vo["disc_pct"]
        
        is_comp = res.get("is_compliant", False)
        status_text = res.get("status", "")
        explanation = res.get("explanation", "")
        max_allowed = res.get("max_allowed_discount_pct", 0.0)

        if is_comp:
            st.success(f"OFFRE APPROUVÉE AUTOMATIQUEMENT\n\n{explanation}")
            log_decision(c_id, s_code, disc_pct, status_text, "Système Déterministe", provider)
            del st.session_state["verified_offer"]
        else:
            st.warning(f"{status_text.upper()}\n\n{explanation}")
            
            if "Escalade" in status_text:
                st.markdown("---")
                st.markdown("### Validation Humaine requise (Human-In-The-Loop)")
                st.write(f"La remise de {disc_pct}% dépasse le plafond autorisé de {max_allowed}%.")
                
                col_app, col_rej = st.columns(2)
                with col_app:
                    if st.button("Approuver par dérogation (Manager Sales)", key="btn_app"):
                        log_decision(c_id, s_code, disc_pct, "Approuvé par dérogation Manager", "Manager Sales", provider)
                        st.success("Offre approuvée par dérogation et enregistrée dans le journal d'audit !")
                        del st.session_state["verified_offer"]
                        st.rerun()
                with col_rej:
                    if st.button("Refuser l'escalade", key="btn_rej"):
                        log_decision(c_id, s_code, disc_pct, "Refusé par Manager", "Manager Sales", provider)
                        st.error("Offre refusée et enregistrée dans le journal d'audit !")
                        del st.session_state["verified_offer"]
                        st.rerun()

with tab3:
    st.subheader("Journal des Décisions et Négociations Commerciales")
    if DECISIONS_FILE.exists():
        df_dec = pd.read_csv(DECISIONS_FILE)
        if len(df_dec) > 0:
            st.dataframe(df_dec, width="stretch")
        else:
            st.info("Aucune décision enregistrée pour le moment.")
    else:
        st.info("Fichier de journalisation introuvable.")
