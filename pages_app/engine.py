import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages_app.db import query


def mostrar():
    st.header("🧠 Engine BertuccIA")
    st.caption("Analise qualquer jogo manualmente e identifique oportunidades +EV em tempo real")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚙️ Parâmetros do Modelo")

        st.markdown("**Time da Casa**")
        gols_marcados_casa = st.number_input("Média de gols marcados (casa)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
        gols_sofridos_casa = st.number_input("Média de gols sofridos (casa)", min_value=0.1, max_value=5.0, value=1.2, step=0.1)

        st.markdown("**Time Visitante**")
        gols_marcados_fora = st.number_input("Média de gols marcados (fora)", min_value=0.1, max_value=5.0, value=1.2, step=0.1)
        gols_sofridos_fora = st.number_input("Média de gols sofridos (fora)", min_value=0.1, max_value=5.0, value=1.4, step=0.1)

        st.markdown("**Odds do Mercado**")
        odd_casa   = st.number_input("Odd Casa",   min_value=1.01, max_value=50.0, value=2.10, step=0.05)
        odd_empate = st.number_input("Odd Empate", min_value=1.01, max_value=50.0, value=3.40, step=0.05)
        odd_fora   = st.number_input("Odd Fora",   min_value=1.01, max_value=50.0, value=3.60, step=0.05)
        odd_over25 = st.number_input("Odd Over 2.5", min_value=1.01, max_value=50.0, value=1.90, step=0.05)
        odd_btts   = st.number_input("Odd BTTS Sim", min_value=1.01, max_value=50.0, value=1.75, step=0.05)

        analisar = st.button("🔍 Analisar Agora", use_container_width=True, type="primary")

    with col2:
        st.subheader("📊 Resultado da Análise")

        if analisar:
            import math

            def poisson(lam, k):
                return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

            media_liga = 1.35
            lam_casa = (gols_marcados_casa / media_liga) * (gols_sofridos_fora / media_liga) * media_liga
            lam_fora = (gols_marcados_fora / media_liga) * (gols_sofridos_casa / media_liga) * media_liga

            prob_casa = prob_empate = prob_fora = 0
            prob_over25 = prob_btts = 0

            for i in range(7):
                for j in range(7):
                    p = poisson(lam_casa, i) * poisson(lam_fora, j)
                    if i > j:   prob_casa   += p
                    elif i == j: prob_empate += p
                    else:        prob_fora   += p
                    if i + j > 2: prob_over25 += p
                    if i > 0 and j > 0: prob_btts += p

            total = prob_casa + prob_empate + prob_fora
            prob_casa   /= total
            prob_empate /= total
            prob_fora   /= total

            # Odds justas
            oj_casa   = round(1 / prob_casa,   2)
            oj_empate = round(1 / prob_empate, 2)
            oj_fora   = round(1 / prob_fora,   2)
            oj_over25 = round(1 / prob_over25, 2) if prob_over25 > 0 else 99
            oj_btts   = round(1 / prob_btts,   2) if prob_btts   > 0 else 99

            # EV
            ev_casa   = round(((prob_casa   * odd_casa)   - 1) * 100, 2)
            ev_empate = round(((prob_empate * odd_empate) - 1) * 100, 2)
            ev_fora   = round(((prob_fora   * odd_fora)   - 1) * 100, 2)
            ev_over25 = round(((prob_over25 * odd_over25) - 1) * 100, 2)
            ev_btts   = round(((prob_btts   * odd_btts)   - 1) * 100, 2)

            # Probabilidades
            st.markdown("**📐 Probabilidades (Modelo Poisson)**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("🏠 Casa",   f"{prob_casa*100:.1f}%",   f"Odd justa: {oj_casa}")
            with c2:
                st.metric("🤝 Empate", f"{prob_empate*100:.1f}%", f"Odd justa: {oj_empate}")
            with c3:
                st.metric("✈️ Fora",   f"{prob_fora*100:.1f}%",   f"Odd justa: {oj_fora}")

            c4, c5 = st.columns(2)
            with c4:
                st.metric("⚽ Over 2.5", f"{prob_over25*100:.1f}%", f"Odd justa: {oj_over25}")
            with c5:
                st.metric("🎯 BTTS",     f"{prob_btts*100:.1f}%",   f"Odd justa: {oj_btts}")

            st.markdown("---")
            st.markdown("**📈 Valor Esperado (+EV) por Mercado**")

            mercados = [
                ("🏠 Vitória Casa",  ev_casa,   odd_casa,   oj_casa),
                ("🤝 Empate",        ev_empate, odd_empate, oj_empate),
                ("✈️ Vitória Fora",  ev_fora,   odd_fora,   oj_fora),
                ("⚽ Over 2.5",      ev_over25, odd_over25, oj_over25),
                ("🎯 BTTS Sim",      ev_btts,   odd_btts,   oj_btts),
            ]

            tem_valor = False
            for nome, ev, odd_mkt, odd_justa in mercados:
                if ev >= 3:
                    tem_valor = True
                    cor = "#00FF87" if ev >= 10 else "#FFD700" if ev >= 5 else "#FF6B6B"
                    nivel = "🟢 Baixo" if ev >= 10 else "🟡 Médio" if ev >= 5 else "🔴 Alto"
                    st.markdown(f"""
                    <div style="background:#1E1E2E;border-radius:8px;padding:0.8rem;
                                border-left:3px solid {cor};margin-bottom:0.5rem">
                        <b>{nome}</b> &nbsp;|&nbsp;
                        Mercado: <b>{odd_mkt}</b> &nbsp;|&nbsp;
                        Justa: <b>{odd_justa}</b> &nbsp;|&nbsp;
                        EV: <b style="color:{cor}">+{ev}%</b> &nbsp;|&nbsp;
                        Risco: {nivel}
                    </div>
                    """, unsafe_allow_html=True)

            if not tem_valor:
                st.warning("Nenhum mercado com valor positivo (+EV ≥ 3%) identificado neste jogo.")
        else:
            st.info("Configure os parâmetros ao lado e clique em **Analisar Agora** para ver os resultados.")
            st.markdown("""
            **Como usar:**
            1. Insira a média de gols marcados e sofridos de cada time
            2. Coloque as odds atuais do mercado
            3. Clique em Analisar
            4. O modelo calcula a probabilidade real via Poisson
            5. Compara com as odds do mercado e identifica +EV
            """)
