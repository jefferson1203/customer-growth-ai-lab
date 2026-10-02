import json
import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

from config import OUTPUTS

# Titre Principal & Sous-titre
st.caption("CUSTOMER & GROWTH AI LAB — PROJET 3")
st.title("Optimisation du Pricing & Élasticité Prix")
st.markdown("Modélisation économétrique de l'élasticité-prix de la demande, garde-fous métier, justifications LLM anti-hallucination et validation humaine.")

# Chargement direct de la Source Unique de Vérité JSON
JSON_PATH = OUTPUTS / "pricing" / "summary_metrics.json"

if not JSON_PATH.exists():
    st.error(f"Fichier de métriques introuvable : {JSON_PATH}. Veuillez exécuter 'python pricing/export_summary.py' au préalable.")
    st.stop()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

global_m = data["global_metrics"]
diag_m = data["diagnostic_summary"]
sens_m = data["sensitivity_analysis"]
llm_m = data["llm_control_metrics"]
top_opps = data["top_opportunities"]
skus_sum = data["skus_summary"]

# Configuration des 4 Onglets Corporate (sans émojis)
tabs = st.tabs([
    "Cadrage & Recommandations",
    "Diagnostic Tarifaire Actuel",
    "Modélisation de l'Élasticité",
    "Recommandations & Validation Humaine"
])

# ==============================================================================
# TAB 0 : CADRAGE & RECOMMANDATIONS
# ==============================================================================
with tabs[0]:
    st.header("Cadrage Stratégique & Recommandations")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Problématique & Objectifs Business")
        st.markdown("""
        - **Enjeu Pricing** : Auditer la politique tarifaire actuelle pour repérer les fuites de marge et optimiser la rentabilité catalogue.
        - **Objectif Financial** : Ajuster les prix unitaires sous garde-fous pour capter du gain de marge net sans dégrader les volumes.
        - **Gouvernance IA** : Automatiser les explications commerciales via Gemini tout en imposant un **contrôle anti-hallucination par Regex** et une **validation humaine (Human-in-the-Loop)**.
        """)
        
    with col2:
        st.subheader("Méthode Économétrique & Garde-fous")
        st.markdown("""
        - **Modèle Log-Log OLS** : `ln(Q) = alpha + elasticity * ln(P) + effets_mois + e`.
        - **Effets Fixes du Mois** : Correction systématique de la saisonnalité (ex: pics de ventes de Noël).
        - **Garde-fous Métier** : Variation plafonnée à **±10%**, markup minimum de **1.2x**, arrondis psychologiques en `,49` ou `,99`.
        - **Filtrage de Sécurité** : Exclusion de toute recommandation pour les SKUs non significatifs (`p >= 0.10`) ou à demande atypique (`elasticity >= 0`).
        """)

    st.divider()

    st.subheader("Slides de Synthèse Stratégique Direction")
    
    SLIDES_PDF_PATH = Path("slides/Projet3_Pricing_Slides.pdf")
    if SLIDES_PDF_PATH.exists():
        with open(SLIDES_PDF_PATH, "rb") as f_pdf:
            st.download_button(
                label="📄 Télécharger les Slides de Synthèse Stratégique Pricing (PDF A4 Paysage)",
                data=f_pdf.read(),
                file_name="Projet3_Pricing_Slides.pdf",
                mime="application/pdf",
                help="Télécharger le support de présentation executive au format PDF A4 Paysage (3 slides)."
            )
    
    pct_dispersion = diag_m['pct_skus_high_dispersion'] * 100
    imp_discount = diag_m['discounts_summary']['implicit_discount_pct'] * 100
    modeled_n = global_m['modeled_skus']
    nb_elastic = global_m['category_breakdown'].get('Élastique', 0)
    nb_inelastic = global_m['category_breakdown'].get('Inélastique', 0)
    nb_non_sig = global_m['category_breakdown'].get('Non significatif', 0)
    gain_gbp = global_m['margin_gain_gbp']
    gain_pct = global_m['margin_gain_pct'] * 100
    gain_sens_40 = sens_m.get('40', {}).get('margin_gain_gbp', 0.0)
    gain_sens_60 = sens_m.get('60', {}).get('margin_gain_gbp', 0.0)

    st.info(f"""
    **Synthèse des Résultats Clés** :
    1. **Diagnostic Tarifaire** : {pct_dispersion:.1f} % des SKUs présentent un écart de prix ≥ 2x. La remise unitaire accordée au Top 1% des grossistes n'est que de {imp_discount:.2f} %, révélant une politique de remises informelle et non structurée.
    2. **Modélisation Économétrique** : Sur les {modeled_n} SKUs éligibles du top CA, {nb_elastic} sont à demande **Élastique** (élasticité < -1), {nb_inelastic} sont **Inélastiques** et {nb_non_sig} sont classés **Non significatifs / Exclus** par sécurité.
    3. **Impact Financier** : L'optimisation sous garde-fous génère **+£{gain_gbp:,.2f} de marge additionnelle (+{gain_pct:.2f} %)** dans le scénario central.
    """)

    st.divider()

    st.subheader("Limites & Hypothèses du Modèle")
    st.warning(f"""
    - **Hypothèse de Coût Unitaire** : En l'absence de coûts réels dans Online Retail II, le coût est estimé à 50 % du prix moyen. Une analyse de sensibilité (40 %, 50 %, 60 %) valide la robustesse des gains dans tous les scénarios (+£{gain_sens_60:,.0f} à +£{gain_sens_40:,.0f}).
    - **Biais des Remises Grossistes** : Une partie des variations de prix provient de remises sur volume et non de décisions tarifaires. La comparaison avec l'élasticité sur petites quantités prévient ce biais.
    - **Demande à Élasticité Constante** : Le modèle suppose une élasticité locale constante, d'où la nécessité stricte du garde-fou à $\\pm 10\\%$ pour éviter toute extrapolation abusive.
    """)

# ==============================================================================
# TAB 1 : DIAGNOSTIC TARIFAIRE ACTUEL
# ==============================================================================
with tabs[1]:
    st.header("Audit de la Politique Tarifaire Actuelle")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total SKUs Analysés", f"{diag_m['total_skus_analyzed']:,}")
    kpi2.metric("Ratio Médian Pmax/Pmin", f"{diag_m['median_price_ratio_max_min']}x")
    kpi3.metric("SKUs Écart Prix ≥ 2x", f"{diag_m['pct_skus_high_dispersion']*100:.1f} %")
    kpi4.metric("Remise Implicite Grossistes", f"{diag_m['discounts_summary']['implicit_discount_pct']*100:.2f} %")

    st.divider()

    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        st.subheader("Comparaison Tarifaire : Grossistes vs Autres Clients")
        df_disc = pd.DataFrame([
            {"Segment Client": "Top 1% Grossistes", "Prix Unitaire Médian (£)": diag_m['discounts_summary']['median_price_top_clients']},
            {"Segment Client": "Autres Clients", "Prix Unitaire Médian (£)": diag_m['discounts_summary']['median_price_other_clients']}
        ])
        fig_disc = px.bar(df_disc, x="Segment Client", y="Prix Unitaire Médian (£)", color="Segment Client", text_auto=".2f", title="Prix Médian Payé par Segment (£)")
        st.plotly_chart(fig_disc, use_container_width=True)

    with col_diag2:
        st.subheader("Évolution Temporelle du Prix Moyen Mensuel")
        df_trends = pd.DataFrame(diag_m["monthly_trends"])
        fig_trend = px.line(df_trends, x="YearMonth", y="mean_price", title="Prix Moyen Mensuel (£)", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

# ==============================================================================
# TAB 2 : MODÉLISATION DE L'ÉLASTICITÉ
# ==============================================================================
with tabs[2]:
    st.header("Résultats de la Modélisation de l'Élasticité Log-Log")

    col_cat1, col_cat2 = st.columns([1, 2])
    with col_cat1:
        st.subheader("Répartition des SKUs")
        cat_df = pd.DataFrame(list(global_m["category_breakdown"].items()), columns=["Catégorie", "Nombre"])
        fig_pie = px.pie(cat_df, names="Catégorie", values="Nombre", title="Distribution de l'Élasticité", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_cat2:
        st.subheader("Explorateur par Référence (SKU)")
        df_skus = pd.DataFrame(skus_sum)
        
        search = st.text_input("Rechercher par StockCode ou Description :", "")
        category_filter = st.multiselect("Filtrer par Catégorie :", options=df_skus["category"].unique(), default=df_skus["category"].unique())

        df_filtered = df_skus[
            (df_skus["category"].isin(category_filter)) &
            (df_skus["StockCode"].str.contains(search, case=False) | df_skus["Description"].str.contains(search, case=False))
        ]

        st.dataframe(
            df_filtered[["StockCode", "Description", "category", "elasticity", "r2", "p_value", "current_price", "rec_price", "price_change_pct"]],
            use_container_width=True
        )

# ==============================================================================
# TAB 3 : RECOMMANDATIONS & VALIDATION HUMAINE
# ==============================================================================
with tabs[3]:
    st.header("Moteur de Recommandation, Validation Humaine & Sensibilité")

    # Metrics Financières
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Marge Baseline Total", f"£{global_m['baseline_margin_gbp']:,.2f}")
    m2.metric("Marge Optimisée Total", f"£{global_m['optimized_margin_gbp']:,.2f}")
    m3.metric("Gain de Marge Potentiel", f"+£{global_m['margin_gain_gbp']:,.2f}", f"+{global_m['margin_gain_pct']*100:.2f} %")
    m4.metric("Contrôle LLM (1er essai)", f"{llm_m['first_try_acceptance_rate']*100:.1f} %")

    st.divider()

    st.subheader("Validation Humaine des Prix Recommandés (Human-in-the-Loop)")
    st.caption("Sélectionnez un SKU pour examiner la justification générée par le LLM et valider, modifier ou rejeter la recommandation.")

    df_top = pd.DataFrame(top_opps)
    selected_sku = st.selectbox("Sélectionner un SKU à examiner :", options=df_top["StockCode"] + " - " + df_top["Description"])

    if selected_sku:
        sku_code = selected_sku.split(" - ")[0]
        row_sku = df_top[df_top["StockCode"] == sku_code].iloc[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("Prix Actuel", f"£{row_sku['current_price']:.2f}")
        c2.metric("Prix Recommandé", f"£{row_sku['rec_price']:.2f}", f"{row_sku['price_change_pct']*100:+.2f} %")
        c3.metric("Gain Marge Attendu", f"+£{row_sku['margin_gain_gbp']:.2f}")

        st.info(f"**Justification LLM (Statut : {row_sku['control_status']})** :\n\n{row_sku['llm_justification']}")

        # Formulaire de décision humaine
        with st.form(key=f"form_{sku_code}"):
            dec_col1, dec_col2, dec_col3 = st.columns(3)
            decision = dec_col1.radio("Décision :", ["Valider", "Modifier Prix", "Rejeter"])
            final_price = dec_col2.number_input("Prix Final Retenu (£) :", value=float(row_sku["rec_price"]), step=0.10)
            comment = dec_col3.text_input("Commentaire / Rationale :", "RAS")

            submit = st.form_submit_button("Enregistrer la Décision")

            if submit:
                decisions_path = OUTPUTS / "pricing" / "decisions.csv"
                decisions_path.parent.mkdir(parents=True, exist_ok=True)

                new_decision = pd.DataFrame([{
                    "timestamp": datetime.datetime.now().isoformat(),
                    "stock_code": sku_code,
                    "description": row_sku["Description"],
                    "current_price": row_sku["current_price"],
                    "rec_price": row_sku["rec_price"],
                    "decision": decision,
                    "final_price": final_price,
                    "comment": comment
                }])

                if decisions_path.exists():
                    df_dec = pd.read_csv(decisions_path)
                    df_dec = pd.concat([df_dec, new_decision], ignore_index=True)
                else:
                    df_dec = new_decision

                df_dec.to_csv(decisions_path, index=False)
                st.success(f"✅ Décision enregistrée dans {decisions_path.name} pour le SKU {sku_code} !")

    st.divider()

    st.subheader("Analyse de Sensibilité sur la Grille des Ratios de Coût")
    sens_df = pd.DataFrame(sens_m).T
    fig_sens = px.bar(sens_df, x="cost_ratio_pct", y="margin_gain_gbp", text_auto=",.2f", title="Gain de Marge Potentiel selon le Ratio de Coût (£)", labels={"cost_ratio_pct": "Ratio de Coût (% prix moyen)", "margin_gain_gbp": "Gain de Marge (£)"})
    st.plotly_chart(fig_sens, use_container_width=True)

    # Bouton de Téléchargement du Modèle Excel
    EXCEL_PATH = OUTPUTS / "pricing" / "pricing_optimization.xlsx"
    if EXCEL_PATH.exists():
        with open(EXCEL_PATH, "rb") as f_excel:
            st.download_button(
                label="📊 Télécharger le Modèle Financier Excel Complet (.xlsx)",
                data=f_excel,
                file_name="pricing_optimization.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ==============================================================================
# FOOTER CORPORATE & GITHUB LINK
# ==============================================================================
st.divider()
st.caption("⚡ **Customer & Growth AI Lab** — Code source et documentation complets sur le dépôt GitHub : [https://github.com/jefferson1203/customer-growth-ai-lab](https://github.com/jefferson1203/customer-growth-ai-lab)")
