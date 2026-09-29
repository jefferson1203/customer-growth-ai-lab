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
def load_all_data():
    """Charge et prépare les données Olist et les classifications LLM."""
    processed_path = OUTPUTS / "voc" / "processed_voc.csv.gz"
    if processed_path.exists():
        full_df = pd.read_csv(processed_path)
    else:
        data = load_olist(DATA_RAW)
        full_df = prepare_voc_data(data)
    
    cache_path = OUTPUTS / "voc" / "classifications.jsonl"
    classified_df = pd.DataFrame()
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        classified_df = pd.DataFrame([{"review_id": k, **v} for k, v in cache_data.items()])
        classified_df = classified_df.merge(full_df[["review_id", "review_score", "review_comment_message"]], on="review_id", how="inner")
        
    return full_df, classified_df


@st.cache_data
def get_cached_prio_matrix(classified_df, full_df):
    return compute_prioritization_matrix(classified_df, full_df)


@st.cache_data
def get_cached_delay_analysis(full_df):
    return analyze_delay_impact(full_df)


# En-tête clair
st.caption("CUSTOMER & GROWTH AI LAB")
st.title("Plateforme Voix du Client & NPS Prédictif")
st.markdown("Analyse sémantique des verbatims clients, cartographie des irritants et scoring prédictif.")
st.divider()

with st.spinner("Chargement des données analytiques..."):
    full_df, classified_df = load_all_data()

# Barre latérale claire
st.sidebar.header("Customer & Growth AI")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Périmètre analysé**\n- Avis validés : **{len(full_df):,}**\n- Avis classifiés LLM : **{len(classified_df):,}**")
st.sidebar.markdown("---")

# Navigation par Onglets
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Cadrage & Recommandations",
    "📊 Synthèse & NPS Proxy",
    "🗺️ Matrice des Irritants",
    "⏱️ Analyse des Retards",
    "🤖 Modèle Prédictif ML"
])

# ----------------------------------------------------
# TAB 0 : CADRAGE & RECOMMANDATIONS STRATÉGIQUES
# ----------------------------------------------------
with tab0:
    st.subheader("🎯 Cadrage du Projet 1 : Voix du Client IA & NPS Prédictif")
    
    col_cad1, col_cad2 = st.columns(2)
    with col_cad1:
        st.markdown("""
        ### 📋 Problématique & Objectifs Business
        - **Contexte** : La satisfaction client sur la marketplace Olist subit une dégradation liée à des retards de livraison et des problèmes de conformité produit.
        - **Objectif** : Passer d'une écoute passive réactive à un système d'analyse automatisé par LLM et de préduction proactive par Machine Learning.
        - **Enjeux Conseil** : Identifier les leviers prioritaires de réduction du taux de détracteurs et modéliser le seuil de basculement de la satisfaction.
        """)
        
    with col_cad2:
        st.markdown("""
        ### 📦 Données Utilisées (Olist E-Commerce)
        - **Périmètre** : ~100 000 commandes e-commerce réelles au Brésil (2016-2018).
        - **Verbatims analysés** : 40 641 avis contenant un message texte.
        - **Échantillonnage LLM** : 1 500 avis échantillonnés de manière stratifiée (300 par note 1-5).
        - **Validation** : 100 avis réels annotés manuellement pour évaluer la précision du LLM.
        """)
        
    st.divider()
    st.subheader("💡 Recommandations Stratégiques (Slides Direction)")
    
    with st.expander("Slide 1 : Cartographie des Irritants & Diagnostic NPS", expanded=True):
        st.markdown("""
        * **NPS Proxy Global** : **+15.1** (35.2% de détracteurs vs 50.2% de promoteurs).
        * **Irrritant Majeur #1 — Livraison non reçue (`LIV_NONRECU`)** : Représente **39.7%** des avis négatifs. Impact dévastateur sur l'image de marque.
        * **Irrritant Majeur #2 — Service Client (`SAV`)** : **21.8%** des plaintes dénoncent l'absence de réponse ou l'inefficacité du support.
        * **Irrritant Majeur #3 — Produit non conforme (`PROD_NONCONFORME`)** : **19.3%** des insatisfactions liées à la qualité vendeur.
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
        * **Modèle Retenu** : HistGradientBoosting Classifier (AUC-ROC = **0.711**).
        * **Efficacité Opérationnelle (Lift)** : **2.56x** par rapport au hasard.
        * **Top 10% des commandes les plus à risque** : Concentre **90.0%** de vrais détracteurs.
        * **Valeur Business** : Permet au Service Client de contacter proactivement les 10% de clients menacés *avant même qu'ils ne déposent un avis négatif*.
        """)

# ----------------------------------------------------
# TAB 1 : SYNTHÈSE & NPS PROXY
# ----------------------------------------------------
with tab1:
    st.subheader("Indicateurs clés de satisfaction")
    
    nps_proxy = calculate_nps_proxy(full_df)
    pct_detracteurs = (full_df["review_score"] <= 3).mean() * 100
    pct_promoteurs = (full_df["review_score"] == 5).mean() * 100
    note_moyenne = full_df['review_score'].mean()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NPS Proxy Global", f"{nps_proxy:+.1f}", help="% Promoteurs - % Détracteurs")
    c2.metric("Promoteurs (5★)", f"{pct_promoteurs:.1f}%", f"{int(len(full_df) * pct_promoteurs / 100):,} clients")
    c3.metric("Détracteurs (1-3★)", f"{pct_detracteurs:.1f}%", f"{int(len(full_df) * pct_detracteurs / 100):,} clients", delta_color="inverse")
    c4.metric("Note Moyenne", f"{note_moyenne:.2f} / 5")
        
    st.markdown("---")
    st.subheader("Distribution globale des notes de satisfaction")
    score_counts = full_df["review_score"].value_counts().sort_index()
    st.bar_chart(score_counts)

# ----------------------------------------------------
# TAB 2 : MATRICE DE PRIORISATION
# ----------------------------------------------------
with tab2:
    st.subheader("Cartographie et priorisation des irritants clients")
    
    if not classified_df.empty:
        prio_df = get_cached_prio_matrix(classified_df, full_df)
        
        col_chart, col_table = st.columns([6, 4])
        with col_chart:
            st.markdown("**Part des avis négatifs touchés par irritant (%)**")
            chart_df = prio_df.set_index("irritant")[["frequence"]]
            st.bar_chart(chart_df)
            
        with col_table:
            st.markdown("**Tableau synthétique des irritants**")
            st.dataframe(prio_df)
            
        st.markdown("---")
        st.subheader("Explorateur de verbatims clients")
        selected_irr = st.selectbox("Filtrer par code irritant :", prio_df["irritant"].tolist())
        
        if selected_irr:
            filtered_reviews = classified_df[classified_df["irritants"].apply(lambda x: selected_irr in x if isinstance(x, list) else False)]
            st.write(f"**{len(filtered_reviews)}** avis associés au motif `{selected_irr}` :")
            
            for _, r in filtered_reviews.head(4).iterrows():
                with st.expander(f"Avis ID {r['review_id']} — Note : {int(r['review_score'])}/5"):
                    st.markdown(f"**Résumé automatisé (LLM)** : {r.get('resume_fr', 'N/A')}")
                    st.markdown(f"**Texte original (PT)** : *{r['review_comment_message']}*")
                    st.caption(f"Sentiment : {r.get('sentiment', 'N/A')} | Urgence : {r.get('urgence', 'N/A')}")
    else:
        st.warning("Fichier de cache des classifications non disponible.")

# ----------------------------------------------------
# TAB 3 : ANALYSE DES RETARDS
# ----------------------------------------------------
with tab3:
    st.subheader("Impact des retards de livraison sur le taux de détracteurs")
    delay_df = analyze_delay_impact(full_df)
    
    c_d1, c_d2 = st.columns([5, 5])
    with c_d1:
        st.markdown("**Tableau par tranche de retard**")
        st.dataframe(delay_df)
    with c_d2:
        st.markdown("**Taux de détracteurs par tranche (%)**")
        st.bar_chart(delay_df.set_index("tranche_retard")[["pct_detracteurs"]])
        
    st.error("Seuil d'alerte critique : À partir de 4 jours de retard, 87.3 % des clients deviennent détracteurs. Une action de rétention doit intervenir au 3ème jour de retard.")

# ----------------------------------------------------
# TAB 4 : MODÈLE PRÉDICTIF ML & COURBE ROC
@st.cache_data
def get_cached_ml_results(full_df):
    X, y = prepare_ml_dataset(full_df)
    log_m = train_eval_nps_model(X, y, model_type="logistic")
    gb_m = train_eval_nps_model(X, y, model_type="gb")
    return log_m, gb_m

# ----------------------------------------------------
with tab4:
    st.subheader("Évaluation du modèle prédictif du risque détracteur")
    st.caption("Modèle entraîné exclusivement sur les caractéristiques connues avant l'avis (sans fuite de données).")
    
    if st.button("Lancer l'évaluation comparative des modèles"):
        with st.spinner("Entraînement des modèles Scikit-Learn en cours..."):
            log_m, gb_m = get_cached_ml_results(full_df)
            
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                st.markdown("#### Régression Logistique (Baseline)")
                st.metric("AUC-ROC", f"{log_m['auc']}")
                st.metric("Détracteurs Top 10%", f"{log_m['top_10_detractor_rate']}%")
                st.metric("Lift", f"{round(log_m['top_10_detractor_rate'] / log_m['baseline_detractor_rate'], 2)}x")
                
            with c_m2:
                st.markdown("#### HistGradientBoosting (Modèle Retenu)")
                st.metric("AUC-ROC", f"{gb_m['auc']}")
                st.metric("Détracteurs Top 10%", f"{gb_m['top_10_detractor_rate']}%")
                st.metric("Lift", f"{round(gb_m['top_10_detractor_rate'] / gb_m['baseline_detractor_rate'], 2)}x")
                
            st.markdown("---")
            st.subheader("Courbe ROC Comparative")
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(log_m["fpr"], log_m["tpr"], label=f"Régression Logistique (AUC = {log_m['auc']})", color="#64748B", linewidth=2)
            ax.plot(gb_m["fpr"], gb_m["tpr"], label=f"HistGradientBoosting (AUC = {gb_m['auc']})", color="#2563EB", linewidth=3)
            ax.plot([0, 1], [0, 1], "k--", label="Hasard (AUC = 0.50)", alpha=0.5)
            ax.set_xlabel("Taux de Faux Positifs (FPR)")
            ax.set_ylabel("Taux de Vrais Positifs (TPR)")
            ax.legend(loc="lower right")
            ax.grid(True, linestyle="--", alpha=0.3)
            
            st.pyplot(fig)
            
            lift_val = round(gb_m['top_10_detractor_rate'] / gb_m['baseline_detractor_rate'], 2)
            st.info(f"Efficacité opérationnelle : Le ciblage des 10 % de commandes les plus à risque par Gradient Boosting capte {gb_m['top_10_detractor_rate']}% de vrais détracteurs, soit une efficacité {lift_val}x supérieure à un ciblage aléatoire.")
