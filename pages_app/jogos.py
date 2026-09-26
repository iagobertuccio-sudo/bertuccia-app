import streamlit as st
from datetime import date
from pages_app.db import query

CASAS_REFERENCIA = ["Pinnacle", "Betano", "BetMGM", "1xBet", "William Hill", "Unibet"]


def mostrar():
    st.header("⚽ Jogos do Dia")

    hoje = date.today().isoformat()

    # Filtro de liga
    ligas = ["Todas"] + [
        "Brasileirão Série A", "Brasileirão Série B",
        "Premier League", "Champions League", "Bundesliga"
    ]
    liga_sel = st.selectbox("Filtrar por liga", ligas)

    # Busca jogos
    if liga_sel == "Todas":
        df_jogos = query("""
            SELECT fixture_id, liga, time_casa, time_fora, data_jogo, status
            FROM jogos
            WHERE DATE(data_jogo) = :hoje
            ORDER BY liga, data_jogo
        """, {"hoje": hoje})
    else:
        df_jogos = query("""
            SELECT fixture_id, liga, time_casa, time_fora, data_jogo, status
            FROM jogos
            WHERE DATE(data_jogo) = :hoje AND liga = :liga
            ORDER BY data_jogo
        """, {"hoje": hoje, "liga": liga_sel})

    if df_jogos.empty:
        st.info(f"Nenhum jogo encontrado para hoje ({hoje}). O sistema coleta automaticamente às 09:00 e 18:00.")
        st.markdown("### 📊 Odds disponíveis no banco")
        df_odds_geral = query("""
            SELECT
                o.fixture_id,
                o.bookmaker,
                o.mercado,
                o.odd_casa,
                o.odd_empate,
                o.odd_fora,
                o.coletado_em
            FROM odds o
            ORDER BY o.coletado_em DESC
            LIMIT 50
        """)
        if not df_odds_geral.empty:
            st.dataframe(df_odds_geral, use_container_width=True, hide_index=True)
        return

    st.success(f"✅ {len(df_jogos)} jogo(s) encontrado(s) para hoje")

    # Exibe cada jogo com suas odds
    for _, jogo in df_jogos.iterrows():
        with st.expander(
            f"**{jogo['time_casa']} vs {jogo['time_fora']}** "
            f"| {jogo['liga']} "
            f"| {str(jogo['data_jogo'])[11:16]}h "
            f"| {jogo['status']}"
        ):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"**🏠 {jogo['time_casa']}**")
                st.markdown("vs")
                st.markdown(f"**✈️ {jogo['time_fora']}**")
                st.caption(f"Liga: {jogo['liga']}")
                st.caption(f"Horário: {str(jogo['data_jogo'])[11:16]}h")
                st.caption(f"Status: {jogo['status']}")

                # Verifica se tem tip
                df_tip = query("""
                    SELECT mercado_sugerido, odd_sugerida, ev_percentual, nivel_risco
                    FROM tips
                    WHERE fixture_id = :fid
                    ORDER BY ev_percentual DESC
                    LIMIT 1
                """, {"fid": int(jogo["fixture_id"])})

                if not df_tip.empty:
                    t = df_tip.iloc[0]
                    st.markdown("---")
                    st.markdown("🎯 **Tip BertuccIA:**")
                    st.success(
                        f"{t['mercado_sugerido']}\n\n"
                        f"Odd: {t['odd_sugerida']} | EV: +{t['ev_percentual']}%"
                    )

            with col2:
                st.markdown("**📊 Odds por Bookmaker**")
                df_odds = query("""
                    SELECT bookmaker, odd_casa, odd_empate, odd_fora
                    FROM odds
                    WHERE fixture_id = :fid AND mercado = '1X2'
                    ORDER BY odd_casa DESC
                """, {"fid": int(jogo["fixture_id"])})

                if df_odds.empty:
                    st.info("Odds ainda não coletadas para este jogo.")
                else:
                    # Destaca Pinnacle como referência
                    def highlight_pinnacle(row):
                        if row["bookmaker"] == "Pinnacle":
                            return ["background-color: #1a3a1a"] * len(row)
                        return [""] * len(row)

                    styled = df_odds.style.apply(highlight_pinnacle, axis=1)
                    st.dataframe(styled, use_container_width=True, hide_index=True)

                    # Melhor odd de cada coluna
                    st.markdown("**🏆 Melhores odds disponíveis:**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Casa", df_odds["odd_casa"].max())
                    with c2:
                        st.metric("Empate", df_odds["odd_empate"].max())
                    with c3:
                        st.metric("Fora", df_odds["odd_fora"].max())
