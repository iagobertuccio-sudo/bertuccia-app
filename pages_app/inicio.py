import streamlit as st
import pandas as pd
from datetime import date
from pages_app.db import query, scalar


def mostrar():
    st.header("🏠 Visão Geral")

    hoje = date.today().isoformat()

    # Métricas do dia
    col1, col2, col3, col4 = st.columns(4)

    total_jogos = scalar(
        "SELECT COUNT(*) FROM jogos WHERE DATE(data_jogo) = :hoje",
        {"hoje": hoje}
    )
    total_odds = scalar(
        "SELECT COUNT(*) FROM odds WHERE DATE(coletado_em) = :hoje",
        {"hoje": hoje}
    )
    total_tips = scalar(
        "SELECT COUNT(*) FROM tips WHERE data_analise = :hoje",
        {"hoje": hoje}
    )
    total_tips_green = scalar(
        "SELECT COUNT(*) FROM tips WHERE resultado = 'green'",
        {}
    )
    total_tips_all = scalar("SELECT COUNT(*) FROM tips WHERE resultado IS NOT NULL", {})
    taxa_acerto = round((total_tips_green / total_tips_all * 100), 1) if total_tips_all > 0 else 0

    with col1:
        st.metric("⚽ Jogos Hoje", total_jogos)
    with col2:
        st.metric("📊 Odds Coletadas Hoje", total_odds)
    with col3:
        st.metric("🎯 Tips Geradas Hoje", total_tips)
    with col4:
        st.metric("✅ Taxa de Acerto Geral", f"{taxa_acerto}%")

    st.markdown("---")

    # Últimas tips geradas
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader("🎯 Últimas Tips Geradas")
        df_tips = query("""
            SELECT
                data_analise,
                partida,
                competicao,
                mercado_sugerido,
                odd_sugerida,
                odd_justa,
                ev_percentual,
                stake_unidades,
                nivel_risco,
                resultado
            FROM tips
            ORDER BY criado_em DESC
            LIMIT 10
        """)

        if df_tips.empty:
            st.info("Nenhuma tip gerada ainda. Aguardando próximos jogos.")
        else:
            def colorir_resultado(val):
                if val == "green":
                    return "background-color: #004d00; color: #00FF87"
                elif val == "red":
                    return "background-color: #4d0000; color: #FF6B6B"
                return ""

            def colorir_risco(val):
                if val == "Baixo":
                    return "color: #00FF87"
                elif val == "Medio":
                    return "color: #FFD700"
                elif val == "Alto":
                    return "color: #FF6B6B"
                return ""

            styled = df_tips.style\
                .applymap(colorir_resultado, subset=["resultado"])\
                .applymap(colorir_risco, subset=["nivel_risco"])
            st.dataframe(styled, use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("📡 Status do Sistema")
        ultima_coleta = query("""
            SELECT MAX(coletado_em) as ultima FROM odds
        """)
        if not ultima_coleta.empty and ultima_coleta["ultima"][0]:
            st.success(f"✅ Online")
            st.caption(f"Última coleta: {ultima_coleta['ultima'][0]}")
        else:
            st.error("❌ Sem dados recentes")

        st.markdown("**Próximas coletas:**")
        st.info("🕘 09:00 — Coleta completa")
        st.info("🕙 10:00 — Resumo Telegram")
        st.info("🕕 18:00 — Atualização noturna")

        st.markdown("**Ligas monitoradas:**")
        ligas = query("SELECT DISTINCT liga FROM jogos ORDER BY liga")
        if ligas.empty:
            ligas_lista = [
                "Brasileirão Série A",
                "Brasileirão Série B",
                "Premier League",
                "Champions League",
                "Bundesliga",
            ]
            for l in ligas_lista:
                st.caption(f"• {l}")
        else:
            for _, row in ligas.iterrows():
                st.caption(f"• {row['liga']}")
