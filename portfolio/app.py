import json



from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import DATA_RAW, OUTPUTS
from common.data import load_retail
from portfolio.overview import compute_overview_metrics
from portfolio.rfm import compute_rfm, compute_rfm_summary, analyse_wholesalers
from portfolio.clustering import train_kmeans, compare_rfm_vs_kmeans
from portfolio.personas import generate_all_personas, build_next_best_action_table
from common.pdf_exporter import export_markdown_slides_to_pdf
from portfolio.product_analysis import compute_abc_analysis, identify_deletion_candidates
from portfolio.business_case import compute_business_case_a, compute_business_case_b, compute_sensitivity_tables, generate_business_case_excel

# Configuration de la page gérée par main.py


# Chargement optimisé des données
@st.cache_data
def load_all_portfolio_data():
    df_clean, audit_df = load_retail(DATA_RAW)


    df_rfm = compute_rfm(df_clean)
    rfm_summary = compute_rfm_summary(df_rfm)
    df_wholesalers_stats = analyse_wholesalers(df_rfm)

    df_kmeans, silhouette_score_val = train_kmeans(df_rfm, n_clusters=5)

    rfm_vs_kmeans = compare_rfm_vs_kmeans(df_kmeans)
    df_abc, abc_summary = compute_abc_analysis(df_clean)
    df_candidates = identify_deletion_candidates(df_clean, df_rfm, df_abc)
    excel_path = generate_business_case_excel(df_rfm, df_candidates)

    
    cache_path = OUTPUTS / "portfolio" / "personas_cache.json"
    personas_cache = generate_all_personas(rfm_summary, cache_path)

    bc_a = compute_business_case_a(df_rfm)
    bc_b = compute_business_case_b(df_candidates)
    sens_a, sens_b = compute_sensitivity_tables(df_rfm, df_candidates)
    
    return {
        "df_clean": df_clean,
        "df_rfm": df_rfm,
        "rfm_summary": rfm_summary,
        "stats_wholesalers": df_wholesalers_stats,

        "df_kmeans": df_kmeans,
        "silhouette_score": silhouette_score_val,
        "rfm_vs_kmeans": rfm_vs_kmeans,
        "df_abc": df_abc,
        "df_candidates": df_candidates,
        "personas_cache": personas_cache,
        "bc_a": bc_a,
        "bc_b": bc_b,
        "sens_a": sens_a,
        "sens_b": sens_b,
        "excel_path": excel_path
    }

data = load_all_portfolio_data()

# Header & Introduction
st.caption("CUSTOMER & GROWTH AI LAB — PROJET 2")
st.title("Segmentation Clients & Portefeuille Produits")
st.markdown("Analyse RFM, Clustérisation K-Means, Personas LLM, Analyse ABC/Longue Traîne & Business Cases Financiers.")
st.divider()

# Barre latérale
st.sidebar.header("Périmètre Analyste")
st.sidebar.markdown(f"**Données Online Retail II**\n- Transactions : **{len(data['df_clean']):,}**\n- Clients uniques : **{len(data['df_rfm']):,}**\n- Références SKUs : **{data['df_clean']['StockCode'].nunique():,}**")
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
        - **Concentration du CA** : Une faible proportion de clients VIP et de références produits génère l'essentiel de la marge.
        - **Dilution & Coût de Complexité** : Un catalogue trop large (52.8% de références C) engendre des coûts logistiques sans rentabilité.
        - **At-Risk Churn** : £1.64M de chiffre d'affaires dormant à sécuriser d'urgence via des campagnes ciblées.
        """)
    with col2:
        st.markdown("""
        ### Données & Méthodologie
        - **Source** : Jeux de données *Online Retail II* (Transactions UK & Export 2009-2011).
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
        st.markdown(f"""
        - **Champions (25.2% des clients)** : Génèrent **69.3% du CA total** (£12.08M, panier moyen £8 190.82).
        - **Clients À risque (14.1% des clients)** : **£1.64M de CA sous menace de churn** (récence moyenne de 368 jours).
        - **En sommeil (25.8% des clients)** : £633k de CA dormant (récence moyenne de 457 jours).
        - **Dépendance Grossistes (Top 1% CA)** : **59 clients** représentent à eux seuls **32.06% du CA global** (£5.59M).
        """)
        
    with st.expander("Slide 2 : Personas & Next Best Actions — Stratégie d'activation personnalisée par segment", expanded=False):
        nba_df = build_next_best_action_table(data["personas_cache"], data["rfm_summary"])
        st.dataframe(nba_df, use_container_width=True)

    with st.expander("Slide 3 : Portefeuille Produits — 52,8 % de références C ne génèrent que 5 % du CA et 1 737 produits doivent être supprimés", expanded=False):
        df_abc = data["df_abc"]
        df_cand = data["df_candidates"]
        st.markdown(f"""
        - **Classe A (80% CA)** : **1 036 références** (21.1% du catalogue, £16.10M).
        - **Classe B (15% CA)** : **1 281 références** (26.1% du catalogue, £3.02M).
        - **Classe C (5% CA)** : **2 590 références** (52.8% du catalogue, £1.01M).
        - **Déréférenciation Ciblée** : **1 737 références C** identifiées pour suppression (tendance négative et non achetées par les VIP).
        - **CA Produit à Risque** : **£639k** couverts par substitution.
        """)

    with st.expander("Slide 4 : Business Cases Financiers — Gain net combiné de £796 449 / an avec retours sur investissement élevés", expanded=False):
        bc_a = data["bc_a"]
        bc_b = data["bc_b"]
        st.markdown(f"""
        ### Business Case A : Reconquête des Clients À Risque
        - **Cible** : {bc_a['n_treatment']:,} clients ciblés ({bc_a['n_control']:,} en groupe de contrôle AB testing).
        - **Investissement** : **£{bc_a['cost']:,.2f}** (£2.00 / contact).
        - **Gain Net** : **£{bc_a['net_margin']:,.2f}** (ROI : **{bc_a['roi_pct']:.1f} %**).
        - **Seuil de rentabilité (Break-even)** : **{bc_a['break_event_rate']*100:.2f} %** de taux de réponse.
        - **Sensibilité** : De £22k à £68k selon le taux de marge (20% à 50%).

        ---
        ### Business Case B : Rationalisation du Catalogue SKUs
        - **Périmètre** : **{bc_b['nb_candidates']:,} références C** supprimées.
        - **Économies Logistiques** : **£{bc_b['saving']:,.2f}** (£500 / SKU / an).
        - **Marge Perdue** : **£{bc_b['lost_margin']:,.2f}** (Hypothèse 50% de transfert d'achat).
        - **Gain Net Total** : **£{bc_b['net_gain']:,.2f}**.
        - **Sensibilité** : Gain net de £687k même si le taux de transfert chute à 10%.

        ---
        ### Hypothèses Clés à Valider avec le Client en Atelier
        1. **Coût unitaire contact CRM** : Valider le coût de £2.00 / client.
        2. **Taux de transfert d'achat B** : Confirmer la substituabilité des 1 737 SKUs C avec le Merchandising.
        3. **Coût de complexité logistique SKU** : Confirmer l'économie fixe de £500 / SKU / an avec la Supply Chain.
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
        "recence_moy": "{:.0f} j",
        "frequence_moy": "{:.1f}",
        "monétaire_moy": "£{:,.2f}"
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
    
    fig_scatter = px.scatter_3d(
        data["df_kmeans"], 
        x="Recency", y="Frequency", z="Monetary",
        color="cluster_kmeans", log_x=True, log_y=True, log_z=True,
        title="Visualisation 3D des Clusters K-Means (Échelle Logarithmique)",
        hover_data=["CustomerID", "segment"],
        height=750,
        labels={"Recency": "Récence (jours)", "Frequency": "Fréquence", "Monetary": "Monétaire (£)", "cluster_kmeans": "Cluster K-Means"}
    )
    fig_scatter.update_traces(marker=dict(size=4, opacity=0.8))
    fig_scatter.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ----------------------------------------------------
# TAB 3 : PORTEFEUILLE PRODUITS & BUSINESS CASES
# ----------------------------------------------------
with tab3:
    st.subheader("Analyse ABC & Rationalisation du Catalogue")
    
    df_abc = data["df_abc"]
    abc_counts = df_abc.groupby("categorie_abc").agg(

        nb_skus=("StockCode", "nunique"),
        ca_total=("ca_total", "sum")
    ).reset_index()
    abc_counts["pct_skus"] = (abc_counts["nb_skus"] / len(df_abc)) * 100
    abc_counts["pct_ca"] = (abc_counts["ca_total"] / df_abc["ca_total"].sum()) * 100
    
    col_abc1, col_abc2 = st.columns(2)
    with col_abc1:
        st.metric("Total références SKUs", f"{len(df_abc):,}")
        st.metric("Candidats déréférenciation", f"{len(data['df_candidates']):,}")
    with col_abc2:
        st.dataframe(abc_counts.style.format({
            "nb_skus": "{:,}",
            "ca_total": "£{:,.2f}",
            "pct_skus": "{:.1f}%",
            "pct_ca": "{:.1f}%"
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

