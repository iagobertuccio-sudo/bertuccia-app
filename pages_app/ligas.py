import streamlit as st
from pages_app.db import query


def mostrar():
    st.header("🏆 Ligas & Times")

    liga_sel = st.selectbox("Selecione a liga", [
        "Brasileirão Série A",
        "Brasileirão Série B",
        "Premier League",
        "Champions League",
        "Bundesliga",
    ])

    st.markdown("---")

    df_times = query("""
        SELECT
            team_name        AS time,
            jogos,
            vitorias,
            empates,
            derrotas,
            gols_marcados    AS gols_marc,
            gols_sofridos    AS gols_sof,
            btts_pct,
            over25_pct,
            atualizado_em
        FROM stats_times
        WHERE liga = :liga
        ORDER BY vitorias DESC, gols_marcados DESC
    """, {"liga": liga_sel})

    if df_times.empty:
        st.info(
            f"Ainda não há estatísticas coletadas para {liga_sel}. "
            "Os dados são coletados automaticamente às 09:00 e 18:00 "
            "nos dias em que houver jogos."
        )
        st.markdown("### 📊 Odds disponíveis para esta liga")
        df_odds = query("""
            SELECT
                o.fixture_id,
                o.bookmaker,
                o.odd_casa,
                o.odd_empate,
                o.odd_fora,
                o.coletado_em
            FROM odds o
            JOIN jogos j ON j.fixture_id = o.fixture_id
            WHERE j.liga = :liga
              AND o.mercado = '1X2'
            ORDER BY o.coletado_em DESC
            LIMIT 30
        """, {"liga": liga_sel})

        if df_odds.empty:
            st.info("Nenhuma odd encontrada para esta liga.")
        else:
            st.dataframe(df_odds, use_container_width=True, hide_index=True)
        return

    # Tabela de times
    st.subheader(f"📋 Times — {liga_sel}")
    st.dataframe(df_times, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Análise individual de time
    st.subheader("🔍 Análise de Time")
    times_lista = df_times["time"].tolist()
    time_sel = st.selectbox("Selecione o time", times_lista)

    df_time = df_times[df_times["time"] == time_sel].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚽ Gols Marcados/jogo", df_time["gols_marc"])
    with col2:
        st.metric("🛡️ Gols Sofridos/jogo", df_time["gols_sof"])
    with col3:
        st.metric("🎯 BTTS %", f"{df_time['btts_pct']}%")
    with col4:
        st.metric("📈 Over 2.5 %", f"{df_time['over25_pct']}%")

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("✅ Vitórias", df_time["vitorias"])
    with col6:
        st.metric("🤝 Empates", df_time["empates"])
    with col7:
        st.metric("❌ Derrotas", df_time["derrotas"])

    st.markdown("---")

    # H2H
    st.subheader("⚔️ H2H — Confrontos Diretos")
    outros_times = [t for t in times_lista if t != time_sel]

    if outros_times:
        adversario = st.selectbox("Contra qual time?", outros_times)

        df_h2h = query("""
            SELECT
                data_jogo,
                gols_home,
                gols_away,
                vencedor
            FROM h2h h
            JOIN stats_times s1 ON s1.team_id = h.team_home_id AND s1.team_name ILIKE :time1
            JOIN stats_times s2 ON s2.team_id = h.team_away_id AND s2.team_name ILIKE :time2
            ORDER BY data_jogo DESC
            LIMIT 10
        """, {"time1": f"%{time_sel}%", "time2": f"%{adversario}%"})

        if df_h2h.empty:
            st.info(f"Sem histórico de H2H entre {time_sel} e {adversario} no banco ainda.")
        else:
            home_wins = len(df_h2h[df_h2h["vencedor"] == "home"])
            draws     = len(df_h2h[df_h2h["vencedor"] == "draw"])
            away_wins = len(df_h2h[df_h2h["vencedor"] == "away"])

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"✅ {time_sel}", home_wins)
            with c2:
                st.metric("🤝 Empates", draws)
            with c3:
                st.metric(f"✅ {adversario}", away_wins)

            st.dataframe(df_h2h, use_container_width=True, hide_index=True)
