import streamlit as st

# Configuration de la page principale
st.set_page_config(
    page_title="Customer & Growth AI Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Définition des pages du hub multi-projets
p1 = st.Page("voc/app.py", title="1. Voix du Client IA", icon="📊", url_path="voc", default=True)
p2 = st.Page("portfolio/app.py", title="2. Segmentation Clients", icon="👥", url_path="portfolio")
p3 = st.Page("pricing/app.py", title="3. Pricing & Élasticité", icon="🏷️", url_path="pricing")
p4 = st.Page("copilot/app.py", title="4. Copilote Agentique", icon="🤖", url_path="copilot")

# Lien vers l'application Cloud Run de production dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("🚀 **Déploiement Cloud Run**")
st.sidebar.markdown("[Accéder à l'application Cloud Run](https://customer-growth-voc-tgdklsc2vq-ew.a.run.app/)")

# Hub de navigation Streamlit
pg = st.navigation({
    "Laboratoire AI & Growth": [p1, p2, p3, p4]
})

# Lancement de la page sélectionnée
pg.run()