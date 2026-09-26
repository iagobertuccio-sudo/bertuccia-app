import streamlit as st
import pandas as pd
from datetime import date
from pages_app.db import query


def mostrar():
    st.header("🎯 Tips")

    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

    with col_filtro1:
        data_sel = st.date_input("Data", value=date.today())
    with col_filtro2:
        liga_sel = st.selectbox("Liga", ["Todas", "Brasileirão Série A", "Brasileirão Série B",
                                          "Premier League", "Champions League", "Bundesliga"])
    with col_filtro3:
        risco_sel = st.selectbox("Nível de Risco", ["Todos", "Baixo", "Medio", "Alto"])

    # Monta query dinâmica
    filtros = ["data_analise = :data"]
    params  = {"data": data_sel.isoformat()}

    if liga_sel != "Todas":
        filtros.append("competicao = :liga")
        params["liga"] = liga_sel

    if risco_sel != "Todos":
        filtros.append("nivel_risco = :risco")
        params["risco"] = risco_sel

    where = " AND ".join(filtros)

    df_tips = query(f"""
        SELECT
            partida,
            competicao,
            mercado_sugerido,
            odd_sugerida,
            odd_justa,
            ev_percentual,
            stake_unidades,
            nivel_risco,
            resultado,
            enviado_telegram,
            criado_em
        FROM tips
        WHERE {where}
        ORDER BY ev_percentual DESC
    """, params)

    st.markdown("---")

    if df_tips.empty:
        st.info("Nenhuma tip encontrada para os filtros selecionados.")
        return

    # Resumo rápido
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Tips", len(df_tips))
    with col2:
        greens = len(df_tips[df_tips["resultado"] == "green"])
        st.metric("✅ Green", greens)
    with col3:
        reds = len(df_tips[df_tips["resultado"] == "red"])
        st.metric("❌ Red", reds)
    with col4:
        ev_medio = df_tips["ev_percentual"].mean()
        st.metric("📈 EV Médio", f"+{ev_medio:.1f}%")

    st.markdown("---")

    # Cards de tips
    for _, tip in df_tips.iterrows():
        cor_risco = {
            "Baixo": "#00FF87",
            "Medio": "#FFD700",
            "Alto":  "#FF6B6B",
        }.get(tip["nivel_risco"], "#888")

        resultado_html = ""
        if tip["resultado"] == "green":
            resultado_html = '<span style="color:#00FF87;font-weight:bold">✅ GREEN</span>'
        elif tip["resultado"] == "red":
            resultado_html = '<span style="color:#FF6B6B;font-weight:bold">❌ RED</span>'
        else:
            resultado_html = '<span style="color:#888">⏳ Aguardando</span>'

        telegram_icon = "✅" if tip["enviado_telegram"] else "⏳"

        st.markdown(f"""
        <div style="
            background:#1E1E2E;
            border-radius:12px;
            padding:1.2rem;
            border-left:4px solid {cor_risco};
            margin-bottom:1rem;
        ">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span style="font-size:1.1rem;font-weight:bold">{tip['partida']}</span>
                    <span style="color:#888;margin-left:1rem;font-size:0.85rem">{tip['competicao']}</span>
                </div>
                <div>{resultado_html}</div>
            </div>
            <div style="margin-top:0.8rem;display:flex;gap:2rem;flex-wrap:wrap">
                <div><span style="color:#888">Mercado:</span> <b>{tip['mercado_sugerido']}</b></div>
                <div><span style="color:#888">Odd:</span> <b>{tip['odd_sugerida']}</b></div>
                <div><span style="color:#888">Odd Justa:</span> <b>{tip['odd_justa']}</b></div>
                <div><span style="color:#888">EV:</span> <b style="color:#00FF87">+{tip['ev_percentual']}%</b></div>
                <div><span style="color:#888">Stake:</span> <b>{tip['stake_unidades']}U</b></div>
                <div><span style="color:{cor_risco}">● {tip['nivel_risco']}</span></div>
                <div><span style="color:#888">Telegram:</span> {telegram_icon}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Botão para atualizar resultados manualmente
    st.markdown("---")
    st.subheader("✏️ Atualizar Resultado de Tip")
    st.caption("Use para registrar Green ou Red manualmente")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        partida_sel = st.selectbox("Partida", df_tips["partida"].tolist())
    with col_b:
        resultado_novo = st.selectbox("Resultado", ["green", "red", "void"])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Salvar Resultado"):
            from pages_app.db import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE tips SET resultado = :resultado
                    WHERE partida = :partida
                    AND data_analise = :data
                """), {
                    "resultado": resultado_novo,
                    "partida":   partida_sel,
                    "data":      data_sel.isoformat(),
                })
                conn.commit()
            st.success(f"Resultado '{resultado_novo}' salvo para {partida_sel}!")
            st.rerun()
