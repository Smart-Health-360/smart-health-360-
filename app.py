import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Health 360",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Smart Health 360 — Dashboard")

DIAS_SEMANA = {
    0: "Seg", 1: "Ter", 2: "Qua",
    3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"
}

MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

# -----------------------------------------------------------------------------
# OTIMIZAÇÃO
# -----------------------------------------------------------------------------
MAX_ROWS = 50000  # limita linhas para acelerar o app


@st.cache_data(show_spinner=False)
def load_kaggle():
    cols = [
        "data_agendamento",
        "data_consulta",
        "dia_semana_consulta",
        "mes_consulta",
        "idade",
        "genero_M",
        "no_show",
        "dias_espera",
        "sms_recebido",
        "hipertensao",
        "diabetes",
        "alcoolismo",
        "deficiencia",
    ]

    df = pd.read_csv(
        "data/processed/kaggle_tratado.csv",
        usecols=cols,
        parse_dates=["data_agendamento", "data_consulta"],
        low_memory=True,
    )

    # reduz quantidade para acelerar
    if len(df) > MAX_ROWS:
        df = df.sample(MAX_ROWS, random_state=42)

    # otimização de memória
    int_cols = [
        "idade", "genero_M", "no_show", "dias_espera",
        "sms_recebido", "hipertensao",
        "diabetes", "alcoolismo", "deficiencia",
        "mes_consulta", "dia_semana_consulta"
    ]

    for col in int_cols:
        df[col] = pd.to_numeric(df[col], downcast="integer")

    df["dia_semana_label"] = df["dia_semana_consulta"].map(DIAS_SEMANA)
    df["mes_label"] = df["mes_consulta"].map(MESES)

    return df


@st.cache_data(show_spinner=False)
def load_materdei():
    cols = [
        "COMPETENCIA",
        "TIPO_AGENDA",
        "DS_UNIDADE_ATENDIMENTO",
        "CD_PACIENTE",
        "IDADE",
    ]

    df = pd.read_csv(
        "data/processed/materdei_clean.csv",
        usecols=cols,
        low_memory=True,
    )

    # reduz linhas
    if len(df) > MAX_ROWS:
        df = df.sample(MAX_ROWS, random_state=42)

    df["COMPETENCIA"] = pd.to_datetime(
        df["COMPETENCIA"],
        errors="coerce"
    )

    df["MES_ANO"] = df["COMPETENCIA"].dt.strftime("%m/%Y")

    # otimização
    df["IDADE"] = pd.to_numeric(df["IDADE"], downcast="integer")

    return df


# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs([
    "📋 Análise de No-Show",
    "🏨 Atendimentos Mater Dei"
])

# =============================================================================
# TAB 1
# =============================================================================
with tab1:

    with st.spinner("Carregando dados..."):
        df = load_kaggle()

    st.success(f"Dataset otimizado: {len(df):,} registros".replace(",", "."))

    # -------------------------------------------------------------------------
    # FILTROS
    # -------------------------------------------------------------------------
    st.subheader("Filtros")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        meses_disp = sorted(df["mes_consulta"].dropna().unique())

        mes_sel = st.multiselect(
            "Mês da consulta",
            options=meses_disp,
            format_func=lambda x: MESES.get(x, x),
            default=meses_disp
        )

    with col_f2:
        genero_sel = st.multiselect(
            "Gênero",
            options=["Masculino", "Feminino"],
            default=["Masculino", "Feminino"]
        )

    with col_f3:
        idade_range = st.slider(
            "Faixa etária",
            0,
            int(df["idade"].max()),
            (0, int(df["idade"].max()))
        )

    genero_mask = (
        ((df["genero_M"] == 1) if "Masculino" in genero_sel else False)
        |
        ((df["genero_M"] == 0) if "Feminino" in genero_sel else False)
    )

    mask = (
        df["mes_consulta"].isin(mes_sel)
        &
        genero_mask
        &
        df["idade"].between(*idade_range)
    )

    dff = df.loc[mask]

    # -------------------------------------------------------------------------
    # KPIs
    # -------------------------------------------------------------------------
    total = len(dff)
    no_show_rate = dff["no_show"].mean() * 100
    avg_espera = dff["dias_espera"].mean()
    sms_rate = dff["sms_recebido"].mean() * 100

    st.markdown("---")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Total de consultas",
        f"{total:,}".replace(",", ".")
    )

    k2.metric(
        "Taxa de No-Show",
        f"{no_show_rate:.1f}%"
    )

    k3.metric(
        "Espera média",
        f"{avg_espera:.1f} dias"
    )

    k4.metric(
        "SMS enviado",
        f"{sms_rate:.1f}%"
    )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # LINHA 1
    # -------------------------------------------------------------------------
    row1_c1, row1_c2 = st.columns(2)

    # No-show por dia
    with row1_c1:

        ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        dia_df = (
            dff.groupby("dia_semana_label")["no_show"]
            .mean()
            .reset_index()
        )

        dia_df["taxa"] = dia_df["no_show"] * 100

        dia_df["dia_semana_label"] = pd.Categorical(
            dia_df["dia_semana_label"],
            categories=ordem,
            ordered=True
        )

        dia_df = dia_df.sort_values("dia_semana_label")

        fig1 = px.bar(
            dia_df,
            x="dia_semana_label",
            y="taxa",
            text_auto=".1f",
            title="No-Show por Dia da Semana",
            color="taxa",
            color_continuous_scale="Reds",
        )

        fig1.update_coloraxes(showscale=False)

        st.plotly_chart(
            fig1,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # Comorbidades
    with row1_c2:

        comorbidades = {
            "hipertensao": "Hipertensão",
            "diabetes": "Diabetes",
            "alcoolismo": "Alcoolismo",
            "deficiencia": "Deficiência"
        }

        taxas_com = []
        taxas_sem = []

        for col in comorbidades:

            taxas_com.append(
                dff.loc[dff[col] == 1, "no_show"].mean() * 100
            )

            taxas_sem.append(
                dff.loc[dff[col] == 0, "no_show"].mean() * 100
            )

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            name="Com condição",
            x=list(comorbidades.values()),
            y=taxas_com,
        ))

        fig2.add_trace(go.Bar(
            name="Sem condição",
            x=list(comorbidades.values()),
            y=taxas_sem,
        ))

        fig2.update_layout(
            title="No-Show por Comorbidade",
            barmode="group",
            height=450
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # -------------------------------------------------------------------------
    # LINHA 2
    # -------------------------------------------------------------------------
    row2_c1, row2_c2 = st.columns(2)

    # Histograma idade
    with row2_c1:

        sample_hist = dff.sample(
            min(15000, len(dff)),
            random_state=42
        )

        sample_hist["Status"] = sample_hist["no_show"].map({
            0: "Compareceu",
            1: "No-Show"
        })

        fig3 = px.histogram(
            sample_hist,
            x="idade",
            color="Status",
            nbins=25,
            opacity=0.7,
            title="Distribuição de Idade",
        )

        st.plotly_chart(
            fig3,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # SMS
    with row2_c2:

        sms_df = (
            dff.groupby("sms_recebido")["no_show"]
            .mean()
            .reset_index()
        )

        sms_df["taxa"] = sms_df["no_show"] * 100

        sms_df["SMS"] = sms_df["sms_recebido"].map({
            0: "Não recebeu",
            1: "Recebeu"
        })

        fig4 = px.bar(
            sms_df,
            x="SMS",
            y="taxa",
            text_auto=".1f",
            title="Impacto do SMS",
            color="SMS"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # Boxplot
    espera_df = dff[dff["dias_espera"] <= 60].copy()

    espera_df["Status"] = espera_df["no_show"].map({
        0: "Compareceu",
        1: "No-Show"
    })

    sample_box = espera_df.sample(
        min(10000, len(espera_df)),
        random_state=42
    )

    fig5 = px.box(
        sample_box,
        x="Status",
        y="dias_espera",
        color="Status",
        title="Dias de Espera vs No-Show"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True,
        config={"displayModeBar": False}
    )

# =============================================================================
# TAB 2
# =============================================================================
with tab2:

    with st.spinner("Carregando dados..."):
        dm = load_materdei()

    st.success(f"Dataset otimizado: {len(dm):,} registros".replace(",", "."))

    # -------------------------------------------------------------------------
    # FILTROS
    # -------------------------------------------------------------------------
    st.subheader("Filtros")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        tipos_disp = sorted(dm["TIPO_AGENDA"].dropna().unique())

        tipo_sel = st.multiselect(
            "Tipo de Agenda",
            options=tipos_disp,
            default=tipos_disp[:5]  # limita seleção inicial
        )

    with col_f2:
        unidades_disp = sorted(
            dm["DS_UNIDADE_ATENDIMENTO"].dropna().unique()
        )

        unidade_sel = st.multiselect(
            "Unidade",
            options=unidades_disp,
            default=unidades_disp[:5]
        )

    dmf = dm[
        dm["TIPO_AGENDA"].isin(tipo_sel)
        &
        dm["DS_UNIDADE_ATENDIMENTO"].isin(unidade_sel)
    ]

    # -------------------------------------------------------------------------
    # KPIs
    # -------------------------------------------------------------------------
    total_m = len(dmf)
    pacientes_unicos = dmf["CD_PACIENTE"].nunique()
    idade_media = dmf["IDADE"].mean()

    st.markdown("---")

    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Total de Atendimentos",
        f"{total_m:,}".replace(",", ".")
    )

    k2.metric(
        "Pacientes Únicos",
        f"{pacientes_unicos:,}".replace(",", ".")
    )

    k3.metric(
        "Idade Média",
        f"{idade_media:.1f} anos"
    )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # GRÁFICOS
    # -------------------------------------------------------------------------
    row1_c1, row1_c2 = st.columns(2)

    with row1_c1:

        tipo_count = (
            dmf["TIPO_AGENDA"]
            .value_counts()
            .reset_index()
        )

        tipo_count.columns = ["Tipo", "Qtd"]

        fig_t1 = px.pie(
            tipo_count,
            names="Tipo",
            values="Qtd",
            title="Tipos de Agenda"
        )

        st.plotly_chart(
            fig_t1,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with row1_c2:

        unidade_count = (
            dmf["DS_UNIDADE_ATENDIMENTO"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        unidade_count.columns = ["Unidade", "Qtd"]

        fig_t2 = px.bar(
            unidade_count,
            x="Qtd",
            y="Unidade",
            orientation="h",
            title="Top 10 Unidades"
        )

        st.plotly_chart(
            fig_t2,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    # Evolução mensal
    mensal = (
        dmf.groupby(["MES_ANO", "TIPO_AGENDA"])
        .size()
        .reset_index(name="Qtd")
    )

    fig_t3 = px.line(
        mensal,
        x="MES_ANO",
        y="Qtd",
        color="TIPO_AGENDA",
        markers=True,
        title="Evolução Mensal"
    )

    st.plotly_chart(
        fig_t3,
        use_container_width=True,
        config={"displayModeBar": False}
    )