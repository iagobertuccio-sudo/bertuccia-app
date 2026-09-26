import streamlit as st

st.set_page_config(
    page_title="BertuccIA Tips",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00FF87;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1E1E2E;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #00FF87;
        margin-bottom: 1rem;
    }
    .tip-card {
        background: #1E1E2E;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #FFD700;
        margin-bottom: 1rem;
    }
    .risk-baixo  { color: #00FF87; font-weight: bold; }
    .risk-medio  { color: #FFD700; font-weight: bold; }
    .risk-alto   { color: #FF6B6B; font-weight: bold; }
    .green { color: #00FF87; font-weight: bold; }
    .red   { color: #FF6B6B; font-weight: bold; }
    div[data-testid="stSidebar"] {
        background-color: #13131F;
    }
    .stMetric label { color: #888 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 BertuccIA Tips</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Seu mentor de apostas</div>', unsafe_allow_html=True)

# Sidebar de navegação
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/00FF87/000000?text=BertuccIA", width=150)
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        [
            "🏠 Início",
            "⚽ Jogos do Dia",
            "🎯 Tips",
            "🧠 Engine BertuccIA",
            "📈 Desempenho",
            "🏆 Ligas & Times",
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("BertuccIA Tips v1.0")
    st.caption("Coletas: 09:00 | 10:00 | 18:00")

# Roteamento de páginas
if pagina == "🏠 Início":
    from pages_app.inicio import mostrar
    mostrar()
elif pagina == "⚽ Jogos do Dia":
    from pages_app.jogos import mostrar
    mostrar()
elif pagina == "🎯 Tips":
    from pages_app.tips import mostrar
    mostrar()
elif pagina == "🧠 Engine BertuccIA":
    from pages_app.engine import mostrar
    mostrar()
elif pagina == "📈 Desempenho":
    from pages_app.desempenho import mostrar
    mostrar()
elif pagina == "🏆 Ligas & Times":
    from pages_app.ligas import mostrar
    mostrar()
