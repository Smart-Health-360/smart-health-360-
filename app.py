import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Smart Health 360",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 Smart Health 360 — Dashboard")

DIAS_SEMANA = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

@st.cache_data
def load_kaggle():
    df = pd.read_csv("data/processed/kaggle_tratado.csv", parse_dates=["data_agendamento", "data_consulta"])
    df["dia_semana_label"] = df["dia_semana_consulta"].map(DIAS_SEMANA)
    df["mes_label"] = df["mes_consulta"].map(MESES)
    bairro_cols = [c for c in df.columns if c.startswith("bairro_")]
    df["bairro"] = df[bairro_cols].idxmax(axis=1).str.replace("bairro_", "", regex=False)
    return df

@st.cache_data
def load_materdei():
    df = pd.read_csv("data/processed/materdei_clean.csv")
    df["COMPETENCIA"] = pd.to_datetime(df["COMPETENCIA"], format="%m/%d/%Y")
    df["MES_ANO"] = df["COMPETENCIA"].dt.strftime("%m/%Y")
    return df

tab1, tab2 = st.tabs(["📋 Análise de No-Show", "🏨 Atendimentos Mater Dei"])

# ── TAB 1: KAGGLE ─────────────────────────────────────────────────────────────
with tab1:
    df = load_kaggle()

    st.subheader("Filtros")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        meses_disp = sorted(df["mes_consulta"].unique())
        mes_sel = st.multiselect("Mês da consulta", options=meses_disp,
                                  format_func=lambda x: MESES.get(x, x),
                                  default=meses_disp)
    with col_f2:
        genero_sel = st.multiselect("Gênero", options=["Masculino", "Feminino"],
                                     default=["Masculino", "Feminino"])
    with col_f3:
        idade_range = st.slider("Faixa etária", int(df["idade"].min()), int(df["idade"].max()),
                                 (0, int(df["idade"].max())))

    genero_mask = (
        ((df["genero_M"] == 1) if "Masculino" in genero_sel else False) |
        ((df["genero_M"] == 0) if "Feminino" in genero_sel else False)
    )
    mask = (
        df["mes_consulta"].isin(mes_sel) &
        genero_mask &
        df["idade"].between(*idade_range)
    )
    dff = df[mask]

    total = len(dff)
    no_show_rate = dff["no_show"].mean() * 100
    avg_espera = dff["dias_espera"].mean()
    sms_rate = dff["sms_recebido"].mean() * 100

    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de consultas", f"{total:,}".replace(",", "."))
    k2.metric("Taxa de No-Show", f"{no_show_rate:.1f}%")
    k3.metric("Espera média (dias)", f"{avg_espera:.1f}")
    k4.metric("SMS enviado", f"{sms_rate:.1f}%")
    st.markdown("---")

    row1_c1, row1_c2 = st.columns(2)

    # No-show por dia da semana
    with row1_c1:
        ordem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        dia_df = (
            dff.groupby("dia_semana_label")["no_show"]
            .agg(["sum", "count"])
            .rename(columns={"sum": "no_show", "count": "total"})
            .reset_index()
        )
        dia_df["taxa"] = dia_df["no_show"] / dia_df["total"] * 100
        dia_df["dia_semana_label"] = pd.Categorical(dia_df["dia_semana_label"], categories=ordem, ordered=True)
        dia_df = dia_df.sort_values("dia_semana_label")
        fig1 = px.bar(dia_df, x="dia_semana_label", y="taxa",
                      labels={"dia_semana_label": "Dia da semana", "taxa": "Taxa No-Show (%)"},
                      title="No-Show por Dia da Semana",
                      color="taxa", color_continuous_scale="Reds", text_auto=".1f")
        fig1.update_coloraxes(showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    # No-show: comorbidades
    with row1_c2:
        comorbidades = ["hipertensao", "diabetes", "alcoolismo", "deficiencia"]
        labels = ["Hipertensão", "Diabetes", "Alcoolismo", "Deficiência"]
        taxas_com = []
        taxas_sem = []
        for col in comorbidades:
            taxas_com.append(dff[dff[col] == 1]["no_show"].mean() * 100)
            taxas_sem.append(dff[dff[col] == 0]["no_show"].mean() * 100)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Com condição", x=labels, y=taxas_com,
                               marker_color="#EF553B", text=[f"{v:.1f}%" for v in taxas_com],
                               textposition="outside"))
        fig2.add_trace(go.Bar(name="Sem condição", x=labels, y=taxas_sem,
                               marker_color="#636EFA", text=[f"{v:.1f}%" for v in taxas_sem],
                               textposition="outside"))
        fig2.update_layout(title="No-Show por Comorbidade", barmode="group",
                            yaxis_title="Taxa No-Show (%)", legend_title="Condição")
        st.plotly_chart(fig2, use_container_width=True)

    row2_c1, row2_c2 = st.columns(2)

    # Distribuição de idade
    with row2_c1:
        fig3 = px.histogram(dff, x="idade", color=dff["no_show"].map({0: "Compareceu", 1: "No-Show"}),
                             nbins=30, barmode="overlay", opacity=0.7,
                             labels={"idade": "Idade", "color": "Status"},
                             title="Distribuição de Idade por Status",
                             color_discrete_map={"Compareceu": "#636EFA", "No-Show": "#EF553B"})
        st.plotly_chart(fig3, use_container_width=True)

    # SMS vs no-show
    with row2_c2:
        sms_df = (
            dff.groupby("sms_recebido")["no_show"]
            .agg(["sum", "count"])
            .reset_index()
            .rename(columns={"sum": "no_show", "count": "total"})
        )
        sms_df["taxa"] = sms_df["no_show"] / sms_df["total"] * 100
        sms_df["SMS"] = sms_df["sms_recebido"].map({0: "Não recebeu", 1: "Recebeu"})
        fig4 = px.bar(sms_df, x="SMS", y="taxa", text_auto=".1f",
                      color="SMS", color_discrete_sequence=["#EF553B", "#00CC96"],
                      labels={"taxa": "Taxa No-Show (%)"},
                      title="Impacto do SMS no No-Show")
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # Tempo de espera por no-show
    st.markdown("#### Dias de Espera vs No-Show")
    espera_df = dff[dff["dias_espera"] <= 60].copy()
    espera_df["Status"] = espera_df["no_show"].map({0: "Compareceu", 1: "No-Show"})
    fig5 = px.box(espera_df, x="Status", y="dias_espera",
                  color="Status",
                  color_discrete_map={"Compareceu": "#636EFA", "No-Show": "#EF553B"},
                  labels={"dias_espera": "Dias de espera", "Status": ""},
                  title="Distribuição dos Dias de Espera")
    st.plotly_chart(fig5, use_container_width=True)


# ── TAB 2: MATER DEI ─────────────────────────────────────────────────────────
with tab2:
    dm = load_materdei()

    st.subheader("Filtros")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipos_disp = sorted(dm["TIPO_AGENDA"].dropna().unique())
        tipo_sel = st.multiselect("Tipo de Agenda", options=tipos_disp, default=tipos_disp)
    with col_f2:
        unidades_disp = sorted(dm["DS_UNIDADE_ATENDIMENTO"].dropna().unique())
        unidade_sel = st.multiselect("Unidade de Atendimento", options=unidades_disp, default=unidades_disp)

    dmf = dm[dm["TIPO_AGENDA"].isin(tipo_sel) & dm["DS_UNIDADE_ATENDIMENTO"].isin(unidade_sel)]

    total_m = len(dmf)
    pacientes_unicos = dmf["CD_PACIENTE"].nunique()
    idade_media = dmf["IDADE"].mean()

    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total de Atendimentos", f"{total_m:,}".replace(",", "."))
    k2.metric("Pacientes Únicos", f"{pacientes_unicos:,}".replace(",", "."))
    k3.metric("Idade Média", f"{idade_media:.1f} anos")
    st.markdown("---")

    row1_c1, row1_c2 = st.columns(2)

    # Atendimentos por tipo de agenda
    with row1_c1:
        tipo_count = dmf["TIPO_AGENDA"].value_counts().reset_index()
        tipo_count.columns = ["Tipo", "Qtd"]
        fig_t1 = px.pie(tipo_count, names="Tipo", values="Qtd",
                        title="Atendimentos por Tipo de Agenda",
                        color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_t1.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_t1, use_container_width=True)

    # Atendimentos por unidade
    with row1_c2:
        unidade_count = dmf["DS_UNIDADE_ATENDIMENTO"].value_counts().reset_index()
        unidade_count.columns = ["Unidade", "Qtd"]
        fig_t2 = px.bar(unidade_count, x="Qtd", y="Unidade", orientation="h",
                        title="Atendimentos por Unidade",
                        color="Qtd", color_continuous_scale="Blues",
                        text_auto=True)
        fig_t2.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_t2.update_coloraxes(showscale=False)
        st.plotly_chart(fig_t2, use_container_width=True)

    row2_c1, row2_c2 = st.columns(2)

    # Evolução mensal
    with row2_c1:
        mensal = (
            dmf.groupby(["COMPETENCIA", "TIPO_AGENDA"])
            .size()
            .reset_index(name="Qtd")
        )
        mensal = mensal.sort_values("COMPETENCIA")
        mensal["MES"] = mensal["COMPETENCIA"].dt.strftime("%b/%Y")
        fig_t3 = px.bar(mensal, x="MES", y="Qtd", color="TIPO_AGENDA",
                        barmode="group",
                        title="Evolução Mensal de Atendimentos",
                        labels={"MES": "Mês", "Qtd": "Atendimentos", "TIPO_AGENDA": "Tipo"},
                        color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_t3, use_container_width=True)

    # Distribuição de idade
    with row2_c2:
        fig_t4 = px.histogram(dmf, x="IDADE", nbins=30,
                               color="TIPO_AGENDA",
                               barmode="overlay", opacity=0.7,
                               title="Distribuição de Idade por Tipo de Agenda",
                               labels={"IDADE": "Idade", "TIPO_AGENDA": "Tipo"},
                               color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_t4, use_container_width=True)

    # Top unidades por mês
    st.markdown("#### Volume por Unidade ao Longo do Tempo")
    unidade_mensal = (
        dmf.groupby(["COMPETENCIA", "DS_UNIDADE_ATENDIMENTO"])
        .size()
        .reset_index(name="Qtd")
        .sort_values("COMPETENCIA")
    )
    unidade_mensal["MES"] = unidade_mensal["COMPETENCIA"].dt.strftime("%b/%Y")
    fig_t5 = px.line(unidade_mensal, x="MES", y="Qtd",
                     color="DS_UNIDADE_ATENDIMENTO",
                     markers=True,
                     title="Atendimentos por Unidade — Evolução Mensal",
                     labels={"MES": "Mês", "Qtd": "Atendimentos", "DS_UNIDADE_ATENDIMENTO": "Unidade"})
    st.plotly_chart(fig_t5, use_container_width=True)
