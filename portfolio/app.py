import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import DATA_RAW, OUTPUTS
from portfolio.personas import SegmentPersona, build_next_best_action_table
from common.pdf_exporter import export_markdown_slides_to_pdf

# Configuration de la page gérée par main.py


@st.cache_data
def load_all_portfolio_data():
    summary_path = OUTPUTS / "portfolio" / "summary_metrics.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Fichier {summary_path} introuvable. Exécutez 'python portfolio/export_summary.py' pour le générer.")

    with open(summary_path, "r", encoding="utf-8") as f:
        s = json.load(f)

    sens_a_df = pd.DataFrame(s["sens_a"])
    sens_b_df = pd.DataFrame(s["sens_b"])

    personas_dict = {}
    for seg_name, pdata in s["personas_cache"].items():
        if isinstance(pdata, dict):
            personas_dict[seg_name] = SegmentPersona(**pdata)
        else:
            personas_dict[seg_name] = pdata

    return {
        "overview_metrics": s["overview_metrics"],
        "rfm_summary": pd.DataFrame(s["rfm_summary"]),
        "stats_wholesalers": s["stats_wholesalers"],
        "silhouette_score": s["silhouette_score"],
        "rfm_vs_kmeans": pd.DataFrame(s["rfm_vs_kmeans"]),
        "abc_summary": pd.DataFrame(s["abc_summary"]),
        "candidates_summary": s["candidates_summary"],
        "candidates_top20": pd.DataFrame(s["candidates_top20"]),
        "personas_cache": personas_dict,
        "bc_a": s["bc_a"],
        "bc_b": s["bc_b"],
        "sens_a": sens_a_df,
        "sens_b": sens_b_df,
        "excel_path": s["excel_path"]
    }


data = load_all_portfolio_data()

# Header & Introduction
st.caption("CUSTOMER & GROWTH AI LAB — PROJET 2")
st.title("Segmentation Clients & Portefeuille Produits")
st.markdown("Analyse RFM, Clustérisation K-Means, Personas LLM, Analyse ABC/Longue Traîne & Business Cases Financiers.")
st.divider()

# Barre latérale
overview = data["overview_metrics"]
st.sidebar.header("Périmètre Analyste")
st.sidebar.markdown(
    f"**Données Online Retail II**\n"
    f"- Transactions : **{overview.get('nb_transactions', 1037098):,}**\n"
    f"- Clients uniques : **{overview.get('nb_clients', 5852):,}**\n"
    f"- Références SKUs : **{overview.get('total_skus', 4907):,}**"
)
st.sidebar.markdown("---")

# Structure en 4 Onglets
tab0, tab1, tab2, tab3 = st.tabs([
    "Cadrage & Recommandations",
    "Segmentation RFM & Cohortes",
    "Clusters K-Means vs Règles",
    "Portefeuille Produits & Business Cases"
])

# ----------------------------------------------------
# TAB 0 : CADRAGE & RECOMMANDATIONS STRATÉGIQUES
# ----------------------------------------------------
with tab0:
    st.subheader("Cadrage du Projet 2 : Segmentation & Portefeuille")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Problématique Business & Enjeux
        - **Concentration du CA** : Une faible proportion de clients VIP (Champions 25.2%) génère 69.3% du chiffre d'affaires total.
        - **Dilution & Coût de Complexité** : Un catalogue trop large (52.8% de références C) engendre des coûts logistiques sans contribution à la marge.
        - **At-Risk Churn** : £1.64M de chiffre d'affaires dormant à sécuriser d'urgence via des campagnes de reconquête ciblées.
        """)
    with col2:
        st.markdown("""
        ### Données & Méthodologie
        - **Source** : Jeu de données *Online Retail II* (Transactions UK & Export 2009-2011).
        - **Segmentation RFM** : Quintiles & 6 règles métiers déterministes.
        - **Clustérisation** : K-Means sur $\log(1+x)$ standardisé (5 clusters, Silhouette = 0.342).
        - **LLM Personas** : Génération de personas avec contrainte stricte de confidentialité RGPD.
        """)
    
    st.divider()
    
    # Bouton de téléchargement du support de présentation PDF
    slides_path = Path("slides/Projet2_Segmentation_Portefeuille_Slides.md")
    if slides_path.exists():
        pdf_bytes = export_markdown_slides_to_pdf(slides_path)
        st.download_button(
            label="Télécharger la Présentation Stratégique (PDF)",
            data=pdf_bytes,
            file_name="Projet2_Segmentation_Portefeuille_Slides.pdf",
            mime="application/pdf",
            help="Télécharger les 4 slides au format PDF pour présentation direction."
        )

    st.subheader("Recommandations Stratégiques Direction (Executive Slides)")

    with st.expander("Slide 1 : Portefeuille Clients — Les 25,2 % de Champions génèrent 69,3 % du CA et 59 grossistes 32,1 %", expanded=True):
        st.markdown("""
        - **Champions (25.2% des clients)** : Génèrent **69.3% du CA total** (£12.08M, CA moyen par client sur la période £8 190.82).
        - **Clients À risque (14.1% des clients)** : **£1.64M de CA sous menace de churn** (récence moyenne de 368 jours).
        - **En sommeil (25.8% des clients)** : £633k de CA dormant (récence moyenne de 457 jours).
        - **Dépendance Grossistes (Top 1% CA)** : **59 clients** représentent à eux seuls **32.06% du CA global** (£5.59M).
        """)
        
    with st.expander("Slide 2 : Personas & Next Best Actions — Stratégie d'activation personnalisée par segment", expanded=False):
        nba_df = build_next_best_action_table(data["personas_cache"], data["rfm_summary"])
        st.dataframe(nba_df, use_container_width=True)

    with st.expander("Slide 3 : Portefeuille Produits — 52,8 % de références C ne génèrent que 5 % du CA et 176 produits doivent être supprimés", expanded=False):
        cand_summary = data["candidates_summary"]
        st.markdown(f"""
        - **Classe A (80% CA)** : **1 036 références** (21.1% du catalogue, £16.10M).
        - **Classe B (15% CA)** : **1 281 références** (26.1% du catalogue, £3.02M).
        - **Classe C (5% CA)** : **2 590 références** (52.8% du catalogue, £1.01M).
        - **Déréférenciation Ciblée** : **{cand_summary.get('nb_candidates', 176):,} références C** identifiées pour suppression (tendance négative et non achetées par les VIP).
        - **CA Produit à Risque** : **£{cand_summary.get('ca_at_risk', 14020.87):,.2f}** couverts par des produits de substitution.
        """)

    with st.expander("Slide 4 : Business Cases Financiers — La réactivation est rentable dès 1,58 % de réponse incrémentale et la déréférenciation est rentable dès £13,94 de coût logistique / SKU", expanded=False):
        bc_a = data["bc_a"]
        bc_b = data["bc_b"]
        st.markdown(f"""
        ### Business Case A : Reconquête des Clients À Risque (Seuil de Rentabilité)
        - **Cible** : {bc_a.get('n_treatment', 745):,} clients ciblés ({bc_a.get('n_control', 83):,} en groupe de contrôle AB testing).
        - **Investissement** : **£{bc_a.get('cost', 1490.0):,.2f}** (£2.00 / contact).
        - **Valeur Moyenne d'une Commande** : **£{bc_a.get('valeur_commande', 362.01):,.2f}** / commande.
        - **Seuil de rentabilité (Break-even)** : **{bc_a.get('break_event_rate', 0.0158)*100:.2f} %** de taux de réponse incrémentale minimum.
        - **Gain Net Financier (Scénario 8%)** : **£{bc_a.get('net_margin', 6061.53):,.2f}** (ROI : **{bc_a.get('roi_pct', 406.8):.1f} %**).
        - **Sensibilité** : Gain net de £1.5k à £15.2k selon le taux de marge et la conversion.

        ---
        ### Business Case B : Rationalisation du Catalogue SKUs (Seuil de Rentabilité)
        - **Périmètre** : **{bc_b.get('nb_candidates', 176):,} références C** supprimées.
        - **Seuil de Rentabilité Logistique (Break-even SKU Cost)** : Rentable dès **£{bc_b.get('break_even_sku_cost', 13.94):,.2f} / SKU / an** de coût de complexité fixe (vs £500 retenus dans le scénario central, dégageant **£{bc_b.get('net_gain', 85546.35):,.2f}** net).
        - **Taux de Transfert Minimum (Break-even Transfer Rate)** : Rentable dès **0 % de report d'achat** (marge perdue de £{bc_b.get('lost_margin', 2453.65):,.2f} très inférieure aux £{bc_b.get('saving', 88000.0):,.2f} d'économies logistiques).
        - **Sensibilité** : Gain net de £83k même si le taux de transfert tombe à 10%.

        ---
        ### Limites & Périmètre d'Interprétation (Projet 2)
        1. **Données transactionnelles historiques** : Absence d'informations sociodémographiques clients; périmètre restreint aux transactions enregistrées sans mesure directe de la satisfaction.
        2. **Hypothèses des Business Cases** : Les taux de réengagement (8 %) et de transfert d'achat (50 %) sont des hypothèses de travail à valider par A/B Testing in vivo avec groupe témoin.
        3. **Coûts de complexité logistique** : Le coût fixe de £500 / SKU / an est une moyenne forfaitaire; la déréférenciation exige de vérifier les contraintes contractuelles fournisseurs (MOQ) et la gestion des stocks résiduels.
        4. **Périmètres temporels des Business Cases** : Le CA à risque des SKUs candidates (£14 020.87) est un chiffre d'affaires cumulé sur deux ans, alors que les économies logistiques (£88 000/an) sont calculées sur une base annuelle.
        5. **Présence de références de test / ajustements (TEST, GIFT, etc.)** : Le dataset conserve des références de test ou d'ajustement opérationnel non éliminées par le filtrage initial des StockCodes. Un nettoyage complémentaire du master données est recommandé.
        """)


# ----------------------------------------------------
# TAB 1 : SEGMENTATION RFM & COHORTES
# ----------------------------------------------------
with tab1:
    st.subheader("Distribution et Métriques des Segments RFM")
    
    summary = data["rfm_summary"]
    st.dataframe(summary.style.format({
        "nb_clients": "{:,}",
        "pct_clients": "{:.1f}%",
        "ca_total": "£{:,.2f}",
        "pct_ca": "{:.1f}%",
        "recence_moyenne": "{:.0f} j",
        "frequence_moyenne": "{:.1f}",
        "ca_moyen_client": "£{:,.2f}"
    }), use_container_width=True)
    
    col_rfm1, col_rfm2 = st.columns(2)
    with col_rfm1:
        fig_pie = px.pie(summary, values="pct_ca", names="segment", title="Part du Chiffre d'Affaires par Segment RFM", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_rfm2:
        fig_bar = px.bar(summary, x="segment", y="pct_clients", title="Part des Clients par Segment (%)", text_auto=".1f%")
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------------------------------
# TAB 2 : CLUSTERS K-MEANS VS RÈGLES
# ----------------------------------------------------
with tab2:
    st.subheader("Comparaison Clustering Non-Supervisé (K-Means) vs Règles Métiers")
    st.info(f" Score de Silhouette K-Means (k=5) : **{data['silhouette_score']:.4f}**")
    
    st.dataframe(data["rfm_vs_kmeans"], use_container_width=True)
    st.caption("Matrice de contingence entre les 5 segments déterministes RFM et les 5 clusters découverts par K-Means.")


# ----------------------------------------------------
# TAB 3 : PORTEFEUILLE PRODUITS & BUSINESS CASES
# ----------------------------------------------------
with tab3:
    st.subheader("Analyse ABC & Rationalisation du Catalogue")
    
    abc_df = data["abc_summary"]
    cand_summary = data["candidates_summary"]
    
    col_abc1, col_abc2 = st.columns(2)
    with col_abc1:
        st.metric("Total références SKUs", f"{overview.get('total_skus', 4907):,}")
        st.metric("Candidats déréférenciation", f"{cand_summary.get('nb_candidates', 176):,}")
        st.metric("CA à risque déréférenciation", f"£{cand_summary.get('ca_at_risk', 14020.87):,.2f}")
    with col_abc2:
        st.dataframe(abc_df.style.format({
            "nb_references": "{:,}",
            "ca_total": "£{:,.2f}",
            "pct_references": "{:.1f}%",
            "pct_ca": "{:.1f}%"
        }), use_container_width=True)
        
    st.divider()
    st.subheader("Top 20 des Références Candidates à la Déréférenciation")
    cand_top20 = data["candidates_top20"]
    st.dataframe(cand_top20.style.format({
        "ca_total": "£{:,.2f}",
        "quantity_total": "{:,}"
    }), use_container_width=True)

    st.divider()
    st.subheader("Tables de Sensibilité des Business Cases")
    
    col_sens1, col_sens2 = st.columns(2)
    with col_sens1:
        st.markdown("#### Sensibilité Case A : Response Rate vs Margin Rate (£ Net)")
        st.dataframe(data["sens_a"], use_container_width=True)
    with col_sens2:
        st.markdown("#### Sensibilité Case B : Transfer Rate vs Cost per SKU (£ Net)")
        st.dataframe(data["sens_b"], use_container_width=True)

    st.divider()
    excel_path = Path(data["excel_path"])
    if excel_path.exists():
        excel_bytes = excel_path.read_bytes()
        st.download_button(
            label="Télécharger le Modèle Financier Dynamique (Excel .xlsx)",
            data=excel_bytes,
            file_name="Business_Cases_Portfolio_Rationalization.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Télécharger le fichier Excel interactif avec formules de recalcul dynamique."
        )

st.divider()
st.caption("⚡ **Customer & Growth AI Lab** — Code source et documentation complets sur le dépôt GitHub : [https://github.com/jefferson1203/customer-growth-ai-lab](https://github.com/jefferson1203/customer-growth-ai-lab)")

