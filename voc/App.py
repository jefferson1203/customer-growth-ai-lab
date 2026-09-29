import json
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from config import DATA_RAW, OUTPUTS
from common.data import load_olist, prepare_voc_data
from voc.analysis import calculate_nps_proxy, compute_prioritization_matrix, analyze_delay_impact
from voc.predictive import prepare_ml_dataset, train_eval_nps_model


# Configuration de la page Streamlit
st.set_page_config(
    page_title="Voix du Client IA | Customer & Growth AI Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé CSS
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E293B; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #64748B; margin-bottom: 25px; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_data():
    """Charge et prépare les données Olist et les classifications LLM."""
    data = load_olist(DATA_RAW)
    full_df = prepare_voc_data(data)
    
    # Chargement du cache des classifications LLM
    cache_path = OUTPUTS / "voc" / "classifications.jsonl"
    classified_df = pd.DataFrame()
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        classified_df = pd.DataFrame([{"review_id": k, **v} for k, v in cache_data.items()])
        classified_df = classified_df.merge(full_df[["review_id", "review_score", "review_comment_message"]], on="review_id", how="inner")
        
    return full_df, classified_df


# Header de l'application
st.markdown('<div class="main-title">📊 Voix du Client augmentée par l\'IA (VoC)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyse sémantique des verbatims, priorisation des irritants & NPS prédictif — Olist E-Commerce</div>', unsafe_allow_html=True)

# Chargement des données avec indicateur
with st.spinner("Chargement et traitement des données Olist..."):
    full_df, classified_df = load_all_data()

# Barre latérale (Sidebar)
st.sidebar.image("https://img.icons8.com/color/96/000000/brain-mind.png", width=60)
st.sidebar.title("Configuration")
st.sidebar.markdown("**Projet 1 : Customer & Growth AI Lab**")
st.sidebar.info(f"• Avis bruts nettoyés : {len(full_df):,}\n• Avis classifiés LLM : {len(classified_df):,}")

# Navigation par Onglets
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Vue d'ensemble & NPS Proxy",
    "🎯 Matrice des Irritants",
    "🚚 Impact des Retards",
    "🔮 NPS Prédictif & Courbe ROC"
])

# ----------------------------------------------------
# TAB 1 : VUE D'ENSEMBLE & NPS PROXY
# ----------------------------------------------------
with tab1:
    st.subheader("Indicateurs Clés de Satisfaction")
    
    nps_proxy = calculate_nps_proxy(full_df)
    pct_detracteurs = (full_df["review_score"] <= 3).mean() * 100
    pct_promoteurs = (full_df["review_score"] == 5).mean() * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("NPS Proxy Global", f"{nps_proxy:.2f}", delta="Approximation (1-5★)")
    col2.metric("% Promoteurs (5★)", f"{pct_promoteurs:.1f}%")
    col3.metric("% Détracteurs (1-3★)", f"{pct_detracteurs:.1f}%", delta="-Critique", delta_color="inverse")
    col4.metric("Note Moyenne Globale", f"{full_df['review_score'].mean():.2f} / 5")
    
    st.markdown("---")
    st.subheader("Répartition des Notes de Satisfaction (1 à 5 Étoiles)")
    score_counts = full_df["review_score"].value_counts().sort_index()
    st.bar_chart(score_counts)

# ----------------------------------------------------
# TAB 2 : MATRICE DE PRIORISATION DES IRRITANTS
# ----------------------------------------------------
with tab2:
    st.subheader("Matrice Fréquence × Note Moyenne des Irritants")
    
    if not classified_df.empty:
        prio_df = compute_prioritization_matrix(classified_df, full_df)
        
        col_chart, col_table = st.columns([6, 4])
        
        with col_chart:
            st.markdown("**Fréquence d'apparition dans les avis négatifs (Notes 1 à 3)**")
            chart_df = prio_df.set_index("irritant")[["frequence"]]
            st.bar_chart(chart_df)
            
        with col_table:
            st.markdown("**Détail des métriques par irritant**")
            st.dataframe(prio_df)
            
        st.markdown("---")
        st.subheader("🔍 Explorateur de Verbatims & Résumés LLM")
        selected_irr = st.selectbox("Filtrer par irritant :", prio_df["irritant"].tolist())
        
        if selected_irr:
            filtered_reviews = classified_df[classified_df["irritants"].apply(lambda x: selected_irr in x if isinstance(x, list) else False)]
            st.write(f"Affichage de **{len(filtered_reviews)}** avis contenant l'irritant `{selected_irr}` :")
            
            for _, r in filtered_reviews.head(5).iterrows():
                with st.expander(f"Avis {r['review_id']} — Note : {'⭐' * int(r['review_score'])}"):
                    st.markdown(f"**Résumé FR (LLM)** : {r.get('resume_fr', 'N/A')}")
                    st.markdown(f"**Verbatim d'origine (PT)** : *{r['review_comment_message']}*")
                    st.caption(f"Sentiment : {r.get('sentiment', 'N/A')} | Urgence : {r.get('urgence', 'N/A')}")
    else:
        st.warning("Aucune classification LLM trouvée dans outputs/voc/classifications.jsonl.")

# ----------------------------------------------------
# TAB 3 : IMPACT DES RETARDS DE LIVRAISON
# ----------------------------------------------------
with tab3:
    st.subheader("Dégradation de la Satisfaction selon le Retard")
    
    delay_df = analyze_delay_impact(full_df)
    
    col_d1, col_d2 = st.columns([5, 5])
    
    with col_d1:
        st.markdown("**Tableau récapitulatif par tranche de retard**")
        st.dataframe(delay_df)
        
    with col_d2:
        st.markdown("**Taux de Détracteurs par Tranche de Retard (%)**")
        st.bar_chart(delay_df.set_index("tranche_retard")[["pct_detracteurs"]])
        
    st.error("🚨 **Seuil critique identifié** : À partir de 4 jours de retard, le taux de détracteurs dépasse **87 %**. Une alerte automatique et une action de rétention doivent être déclenchées dès le 3ème jour de retard.")

# ----------------------------------------------------
# TAB 4 : NPS PRÉDICTIF & COURBE ROC
# ----------------------------------------------------
with tab4:
    st.subheader("Modèle de Prédiction du Risque Détracteur (à la Livraison)")
    st.markdown("Prédiction réalisée **au moment de la livraison** (sans data leakage) pour déclencher des actions proactives.")
    
    if st.button("🚀 Entraîner et Comparer les Modèles ML"):
        with st.spinner("Entraînement de la Régression Logistique et du Gradient Boosting..."):
            X, y = prepare_ml_dataset(full_df)
            log_metrics = train_eval_nps_model(X, y, model_type="logistic")
            gb_metrics = train_eval_nps_model(X, y, model_type="gb")
            
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                st.markdown("### 🔹 Baseline : Régression Logistique")
                st.metric("AUC-ROC", f"{log_metrics['auc']}")
                st.metric("Détracteurs Top 10%", f"{log_metrics['top_10_detractor_rate']}%")
                st.metric("Lift", f"{round(log_metrics['top_10_detractor_rate'] / log_metrics['baseline_detractor_rate'], 2)}x")
                
            with col_m2:
                st.markdown("### 🌲 Modèle Avancé : HistGradientBoosting")
                st.metric("AUC-ROC", f"{gb_metrics['auc']}")
                st.metric("Détracteurs Top 10%", f"{gb_metrics['top_10_detractor_rate']}%")
                st.metric("Lift", f"{round(gb_metrics['top_10_detractor_rate'] / gb_metrics['baseline_detractor_rate'], 2)}x")
                
            st.markdown("---")
            st.subheader("📈 Courbe ROC Comparative")
            
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(log_metrics["fpr"], log_metrics["tpr"], label=f"Régression Logistique (AUC = {log_metrics['auc']})", color="#2563EB")
            ax.plot(gb_metrics["fpr"], gb_metrics["tpr"], label=f"HistGradientBoosting (AUC = {gb_metrics['auc']})", color="#059669", linewidth=2)
            ax.plot([0, 1], [0, 1], "k--", label="Hasard (AUC = 0.50)")
            ax.set_xlabel("Taux de Faux Positifs (FPR)")
            ax.set_ylabel("Taux de Vrais Positifs (TPR)")
            ax.set_title("Courbe ROC des Modèles de NPS Prédictif")
            ax.legend(loc="lower right")
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            
            st.success(f"🎯 **Gain opérationnel** : En ciblant les 10 % de commandes les plus à risque via le Gradient Boosting, **{gb_metrics['top_10_detractor_rate']}%** des interventions ciblent de vrais détracteurs (Lift de **{round(gb_metrics['top_10_detractor_rate'] / gb_metrics['baseline_detractor_rate'], 2)}x** par rapport au hasard).")
