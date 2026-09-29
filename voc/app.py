import json
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from config import DATA_RAW, OUTPUTS
from common.data import load_olist, prepare_voc_data
from voc.analysis import calculate_nps_proxy, compute_prioritization_matrix, analyze_delay_impact
from voc.predictive import prepare_ml_dataset, train_eval_nps_model


# Navigation multi-pages déjà configurée par main.py

@st.cache_data
def _read_summary_file(mtime: float):
    summary_path = OUTPUTS / "voc" / "summary_metrics.json"
    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_summary_metrics():
    """Charge les métriques analytiques agrégées pré-calculées avec rafraîchissement automatique."""
    summary_path = OUTPUTS / "voc" / "summary_metrics.json"
    if summary_path.exists():
        return _read_summary_file(summary_path.stat().st_mtime)
    return {}

# ----------------------------------------------------
st.caption("CUSTOMER & GROWTH AI LAB")
st.title("Plateforme Voix du Client & NPS Prédictif")
st.markdown("Analyse sémantique des verbatims clients, cartographie des irritants et scoring prédictif.")
st.divider()

metrics = load_summary_metrics()
total_full_df = metrics.get("total_full_df", 40641)
total_classified_df = metrics.get("total_classified_df", 1500)

# Barre latérale claire
st.sidebar.header("Customer & Growth AI")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Périmètre analysé**\n- Avis validés : **{total_full_df:,}**\n- Avis classifiés LLM : **{total_classified_df:,}**")
st.sidebar.markdown("---")

# Navigation par Onglets
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Cadrage & Recommandations",
    "Synthèse & NPS Proxy",
    "Matrice des Irritants",
    "Analyse des Retards",
    "Modèle Prédictif ML"
])

# ----------------------------------------------------
# TAB 0 : CADRAGE & RECOMMANDATIONS STRATÉGIQUES
# ----------------------------------------------------
with tab0:
    st.subheader("Cadrage du Projet 1 : Voix du Client IA & NPS Prédictif")
    
    col_cad1, col_cad2 = st.columns(2)
    with col_cad1:
        st.markdown("""
        ### Problématique & Objectifs Business
        - **Contexte** : La satisfaction client sur la marketplace Olist subit une dégradation liée à des retards de livraison et des problèmes de conformité produit.
        - **Objectif** : Passer d'une écoute passive réactive à un système d'analyse automatisé par LLM et de prédiction proactive par Machine Learning.
        - **Enjeux Conseil** : Identifier les leviers prioritaires de réduction du taux de détracteurs et modéliser le seuil de basculement de la satisfaction.
        """)
        
    with col_cad2:
        st.markdown("""
        ### Données Utilisées (Olist E-Commerce)
        - **Périmètre** : ~100 000 commandes e-commerce réelles au Brésil (2016-2018).
        - **Verbatims analysés** : 40 641 avis contenant un message texte.
        - **Échantillonnage LLM** : 1 500 avis échantillonnés de manière stratifiée (300 par note 1-5).
        - **Validation** : 100 avis réels annotés manuellement pour évaluer la précision du LLM.
        """)
        
    st.divider()
    st.subheader("Recommandations Stratégiques (Slides Direction)")
    
    with st.expander("Slide 1 : Cartographie des Irritants & Diagnostic NPS", expanded=True):
        st.markdown("""
        * **NPS Proxy Global** : **+15.1** (35.2% de détracteurs vs 50.2% de promoteurs).
        * **Irritant Majeur #1 — Livraison non reçue (`LIV_NONRECU`)** : Représente **47.2%** des avis négatifs (redressé). Impact dévastateur sur l'image de marque.
        * **Irritant Majeur #2 — Service Client (`SAV`)** : **26.8%** des plaintes dénoncent l'absence de réponse ou l'inefficacité du support (redressé).
        * **Irritant Majeur #3 — Retard de livraison (`LIV_RETARD`)** : **20.1%** des avis négatifs soulignent un retard d'échéance (redressé).
        * **Irritant Majeur #4 — Produit non conforme (`PROD_NONCONFORME`)** : **20.0%** des insatisfactions liées à la qualité ou l'erreur d'article (redressé).
        """)
        
    with st.expander("Slide 2 : Impact des Retards — La Règle Critique des 4 Jours", expanded=False):
        st.markdown("""
        * **À l'heure (0 jour de retard)** : Seuls **27.1%** de détracteurs.
        * **1 à 3 jours de retard** : Hausse modérée à **39.5%** de détracteurs.
        * **4 à 10 jours de retard** : **Seuil de rupture à 87.3% de détracteurs**.
        * **Action Opérationnelle** : Déclencher une alerte logistique automatisée et une compensation systématique dès le **4ème jour de retard**.
        """)
        
    with st.expander("Slide 3 : NPS Prédictif — Anticipation Proactive par Machine Learning", expanded=False):
        st.markdown("""
        * **Modèle Retenu** : HistGradientBoosting Classifier (AUC-ROC = **0.713**).
        * **Efficacité Opérationnelle (Lift)** : **2.56x** par rapport au hasard.
        * **Top 10% des commandes les plus à risque** : Concentre **90.15%** de vrais détracteurs.
        * **Valeur Business** : Permet au Service Client de contacter proactivement les 10% de clients menacés *avant même qu'ils ne déposent un avis négatif*.
        """)

    with st.expander("Benchmark & Ingénierie LLM : Évaluation Empirique Prompt V1 vs Prompt V2", expanded=True):
        st.markdown("Comparaison mesurée sur l'échantillon de validation (100 avis annotés manuellement) suite à la désambiguïsation explicite du prompt v2 :")
        prompt_comp = metrics.get("prompt_eval_comparison", [])
        if prompt_comp:
            df_comp = pd.DataFrame(prompt_comp)
            st.dataframe(df_comp, use_container_width=True)

# ----------------------------------------------------
# TAB 1 : SYNTHÈSE & NPS PROXY
# ----------------------------------------------------
with tab1:
    st.subheader("Indicateurs clés de satisfaction")
    
    nps_proxy = metrics.get("nps_proxy", 15.09)
    pct_detracteurs = metrics.get("pct_detracteurs", 35.15)
    pct_promoteurs = metrics.get("pct_promoteurs", 50.24)
    pct_passifs = metrics.get("pct_passifs", 14.6)
    note_moyenne = metrics.get("note_moyenne", 3.67)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NPS Proxy Global", f"{nps_proxy:+.1f}", help="% Promoteurs (5★) - % Détracteurs (1-3★)")
    c2.metric("Promoteurs (5★)", f"{pct_promoteurs:.1f}%", f"{int(total_full_df * pct_promoteurs / 100):,} clients")
    c3.metric("Détracteurs (1-3★)", f"{pct_detracteurs:.1f}%", f"{int(total_full_df * pct_detracteurs / 100):,} clients", delta_color="inverse")
    c4.metric("Note Moyenne", f"{note_moyenne:.2f} / 5")
        
    st.markdown("---")
    st.subheader("Distribution globale des notes de satisfaction")
    score_counts = metrics.get("score_counts", {"1": 8640, "2": 2118, "3": 3528, "4": 5935, "5": 20420})
    st.bar_chart(pd.Series(score_counts))

# ----------------------------------------------------
# TAB 2 : MATRICE DE PRIORISATION
# ----------------------------------------------------
with tab2:
    st.subheader("Cartographie et priorisation des irritants clients (Matrice Redressée)")
    st.caption("Pondération appliquée selon la distribution réelle des avis Olist (60.5% 1★, 14.8% 2★, 24.7% 3★).")
    
    prio_data = metrics.get("prio_matrix", [])
    if prio_data:
        prio_df = pd.DataFrame(prio_data)
        
        col_chart, col_table = st.columns([6, 4])
        with col_chart:
            st.markdown("**Part des avis négatifs touchés par irritant (%, Redressé)**")
            chart_df = prio_df.set_index("irritant")[["frequence"]]
            st.bar_chart(chart_df)
            
        with col_table:
            st.markdown("**Tableau synthétique des irritants (Redressé vs Brut)**")
            st.dataframe(prio_df)
            
        st.markdown("---")
        st.subheader("Explorateur d'échantillons d'irritants (anonymisés)")
        verbatims = metrics.get("verbatims_sample", [])
        if verbatims:
            verb_df = pd.DataFrame(verbatims)
            selected_irr = st.selectbox("Filtrer par code irritant :", prio_df["irritant"].tolist())
            
            if selected_irr:
                filtered_reviews = verb_df[verb_df["irritants"].apply(lambda x: selected_irr in x if isinstance(x, list) else False)]
                st.write(f"**{len(filtered_reviews)}** exemples associés au motif `{selected_irr}` :")
                
                for _, r in filtered_reviews.head(5).iterrows():
                    with st.expander(f"Avis ID {r['review_id']} — Note : {int(r['review_score'])}/5"):
                        if r.get('comment'):
                            st.markdown(f"**Verbatim client original** : *\"{r['comment']}\"*")
                        st.markdown(f"**Résumé automatisé (LLM)** : {r.get('resume_fr', 'N/A')}")
                        st.caption(f"Sentiment : {r.get('sentiment', 'N/A')} | Urgence : {r.get('urgence', 'N/A')}")
    else:
        st.warning("Données d'irritants non disponibles.")

# ----------------------------------------------------
# TAB 3 : ANALYSE DES RETARDS
# ----------------------------------------------------
with tab3:
    st.subheader("Impact des retards de livraison sur le taux de détracteurs (avec Commandes Non Livrées)")
    delay_data = metrics.get("delay_impact", [])
    if delay_data:
        delay_df = pd.DataFrame(delay_data)
        
        c_d1, c_d2 = st.columns([5, 5])
        with c_d1:
            st.markdown("**Tableau par tranche de retard**")
            st.dataframe(delay_df)
        with c_d2:
            st.markdown("**Taux de détracteurs par tranche (%)**")
            st.bar_chart(delay_df.set_index("tranche_retard")[["pct_detracteurs"]])
            
        st.error("Point de rupture : Les commandes non livrées (4.5% des commandes) génèrent 91.4% de détracteurs. À partir de 4 jours de retard, 87.3% des clients deviennent détracteurs.")

# ----------------------------------------------------
# TAB 4 : MODÈLE PRÉDICTIF ML & COURBE ROC
# ----------------------------------------------------
with tab4:
    st.subheader("Évaluation du modèle prédictif du risque détracteur")
    st.caption("Modèle entraîné exclusivement sur les caractéristiques connues avant l'avis (sans fuite de données, incluant la feature non_livre).")
    
    log_m = metrics.get("model_logistic", {})
    gb_m = metrics.get("model_gb", {})
    
    if log_m and gb_m:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            st.markdown("#### Régression Logistique (Baseline)")
            st.metric("AUC-ROC", f"{log_m['auc']}")
            st.metric("Détracteurs Top 10%", f"{log_m['top_10_detractor_rate']:.2f}%")
            
        with c_m2:
            st.markdown("#### HistGradientBoosting (Modèle Retenu)")
            st.metric("AUC-ROC", f"{gb_m['auc']}")
            st.metric("Détracteurs Top 10%", f"{gb_m['top_10_detractor_rate']:.2f}%")
            
        st.markdown("---")
        st.subheader("Courbe ROC Comparative")
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(log_m.get("fpr", []), log_m.get("tpr", []), label=f"Régression Logistique (AUC = {log_m.get('auc')})", color="#64748B", linewidth=2)
        ax.plot(gb_m.get("fpr", []), gb_m.get("tpr", []), label=f"HistGradientBoosting (AUC = {gb_m.get('auc')})", color="#2563EB", linewidth=3)
        ax.plot([0, 1], [0, 1], "k--", label="Hasard (AUC = 0.50)", alpha=0.5)
        ax.set_xlabel("Taux de Faux Positifs (FPR)")
        ax.set_ylabel("Taux de Vrais Positifs (TPR)")
        ax.legend(loc="lower right")
        ax.grid(True, linestyle="--", alpha=0.3)
        
        st.pyplot(fig)
        st.info("Efficacité opérationnelle : Le ciblage du Top 10 % des commandes les plus à risque par Gradient Boosting capte 90 % de vrais détracteurs, permettant une intervention proactive du Service Client.")
