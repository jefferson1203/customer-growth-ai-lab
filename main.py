import streamlit as st

# Configuration de la page principale
st.set_page_config(
    page_title="Customer & Growth AI Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Définition des pages du hub multi-projets
p1 = st.Page("voc/app.py", title="1. Voix du Client IA", icon="📊", default=True)
p2 = st.Page("portfolio/app.py", title="2. Segmentation Clients", icon="👥")
p3 = st.Page("pricing/app.py", title="3. Pricing & Élasticité", icon="🏷️")
p4 = st.Page("copilot/app.py", title="4. Copilote Agentique", icon="🤖")

# Hub de navigation Streamlit
pg = st.navigation({
    "Laboratoire AI & Growth": [p1, p2, p3, p4]
})

# Lancement de la page sélectionnée
pg.run()