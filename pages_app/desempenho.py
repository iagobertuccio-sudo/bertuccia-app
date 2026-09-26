import streamlit as st
import pandas as pd
from pages_app.db import query, scalar


def mostrar():
    st.header("📈 Desempenho")

    # Métricas gerais
    col1, col2, col3, col4, col5 = st.columns(5)

    total  = scalar("SELECT COUNT(*) FROM tips WHERE resultado IS NOT NULL")
    greens = scalar("SELECT COUNT(*) FROM tips WHERE resultado = 'green'")
    reds   = scalar("SELECT COUNT(*) FROM tips WHERE resultado = 'red'")
    taxa   = round(greens / total * 100, 1) if total > 0 else 0

    # ROI simplificado
    df_roi = query("""
        SELECT odd_sugerida, stake_unidades, resultado
        FROM tips
        WHERE resultado IN ('green', 'red')
    """)

    lucro_total = 0
    investido   = 0
    if not df_roi.empty:
        for _, r in df_roi.iterrows():
            investido += r["stake_unidades"]
            if r["resultado"] == "green":
                lucro_total += r["stake_unidades"] * (r["odd_sugerida"] - 1)
            else:
                lucro_total -= r["stake_unidades"]
    roi = round((lucro_total / investido * 100), 1) if investido > 0 else 0

    with col1:
        st.metric("📊 Total Analisadas", total)
    with col2:
        st.metric("✅ Greens", greens)
    with col3:
        st.metric("❌ Reds", reds)
    with col4:
        st.metric("🎯 Taxa de Acerto", f"{taxa}%")
    with col5:
        st.metric("💰 ROI Geral", f"{roi}%", delta=f"{lucro_total:+.1f}U")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Desempenho por Liga")
        df_liga = query("""
            SELECT
                competicao AS liga,
                COUNT(*) AS total,
                SUM(CASE WHEN resultado = 'green' THEN 1 ELSE 0 END) AS greens,
                SUM(CASE WHEN resultado = 'red'   THEN 1 ELSE 0 END) AS reds,
                ROUND(
                    SUM(CASE WHEN resultado = 'green' THEN 1 ELSE 0 END)::numeric
                    / NULLIF(COUNT(*), 0) * 100, 1
                ) AS taxa_pct
            FROM tips
            WHERE resultado IS NOT NULL
            GROUP BY competicao
            ORDER BY taxa_pct DESC
        """)
        if df_liga.empty:
            st.info("Nenhum resultado registrado ainda.")
        else:
            st.dataframe(df_liga, use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("📊 Desempenho por Nível de Risco")
        df_risco = query("""
            SELECT
                nivel_risco,
                COUNT(*) AS total,
                SUM(CASE WHEN resultado = 'green' THEN 1 ELSE 0 END) AS greens,
                SUM(CASE WHEN resultado = 'red'   THEN 1 ELSE 0 END) AS reds,
                ROUND(
                    SUM(CASE WHEN resultado = 'green' THEN 1 ELSE 0 END)::numeric
                    / NULLIF(COUNT(*), 0) * 100, 1
                ) AS taxa_pct
            FROM tips
            WHERE resultado IS NOT NULL
            GROUP BY nivel_risco
            ORDER BY taxa_pct DESC
        """)
        if df_risco.empty:
            st.info("Nenhum resultado registrado ainda.")
        else:
            st.dataframe(df_risco, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📅 Histórico de Tips")

    df_hist = query("""
        SELECT
            data_analise,
            partida,
            competicao,
            mercado_sugerido,
            odd_sugerida,
            stake_unidades,
            nivel_risco,
            ev_percentual,
            resultado
        FROM tips
        WHERE resultado IS NOT NULL
        ORDER BY data_analise DESC, ev_percentual DESC
    """)

    if df_hist.empty:
        st.info("Nenhum resultado registrado ainda. Atualize os resultados na página de Tips.")
    else:
        def colorir(val):
            if val == "green": return "background-color:#004d00;color:#00FF87"
            if val == "red":   return "background-color:#4d0000;color:#FF6B6B"
            return ""
        styled = df_hist.style.applymap(colorir, subset=["resultado"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📈 Evolução da Banca")

    df_banca = query("""
        SELECT data_analise, odd_sugerida, stake_unidades, resultado
        FROM tips
        WHERE resultado IN ('green','red')
        ORDER BY data_analise ASC
    """)

    if df_banca.empty:
        st.info("Aguardando resultados para gerar o gráfico de banca.")
    else:
        banca  = 100.0
        pontos = [{"data": "Início", "banca": banca}]
        for _, r in df_banca.iterrows():
            if r["resultado"] == "green":
                banca += r["stake_unidades"] * (r["odd_sugerida"] - 1)
            else:
                banca -= r["stake_unidades"]
            pontos.append({
                "data":  str(r["data_analise"]),
                "banca": round(banca, 2)
            })

        if len(pontos) > 1:
            df_grafico = pd.DataFrame(pontos).set_index("data")
            st.line_chart(df_grafico)
            st.caption("Banca inicial simulada: 100U")