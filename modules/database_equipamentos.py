# modules/database_equipamentos.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

BANCO_FILTROS = [
    {
        "modelo": "FM-25",
        "volume_6h": 14,
        "volume_8h": 19,
        "carga_areia_kg": 18,
        "quant_sacos_25kg": 1,
        "diametro_mm": 335,
        "altura_mm": 583,
        "peso_bruto_com_areia_kg": 23.4,
        "peso_bruto_sem_areia_kg": 5.4,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-30",
        "volume_6h": 21,
        "volume_8h": 28,
        "carga_areia_kg": 25,
        "quant_sacos_25kg": 1,
        "diametro_mm": 325,
        "altura_mm": 735,
        "peso_bruto_com_areia_kg": 34.13,
        "peso_bruto_sem_areia_kg": 9.13,
        "modelo_motobomba": "BMC-25 M"
    },
    {
        "modelo": "FM-36",
        "volume_6h": 30,
        "volume_8h": 40,
        "carga_areia_kg": 40,
        "quant_sacos_25kg": 2,
        "diametro_mm": 380,
        "altura_mm": 772,
        "peso_bruto_com_areia_kg": 50.7,
        "peso_bruto_sem_areia_kg": 10.7,
        "modelo_motobomba": "BMC-33 M"
    },
    {
        "modelo": "FM-40",
        "volume_6h": 37,
        "volume_8h": 50,
        "carga_areia_kg": 125,
        "quant_sacos_25kg": 5,
        "diametro_mm": 430,
        "altura_mm": 835,
        "peso_bruto_com_areia_kg": 142.98,
        "peso_bruto_sem_areia_kg": 17.98,
        "modelo_motobomba": "BMC-50 M"
    },
    {
        "modelo": "FM-50",
        "volume_6h": 59,
        "volume_8h": 78,
        "carga_areia_kg": 65,
        "quant_sacos_25kg": 3,
        "diametro_mm": 525,
        "altura_mm": 950,
        "peso_bruto_com_areia_kg": 77.55,
        "peso_bruto_sem_areia_kg": 12.55,
        "modelo_motobomba": "BMC-75 M"
    },
    {
        "modelo": "FM-60",
        "volume_6h": 85,
        "volume_8h": 113,
        "carga_areia_kg": 200,
        "quant_sacos_25kg": 8,
        "diametro_mm": 645,
        "altura_mm": 1000,
        "peso_bruto_com_areia_kg": 221.42,
        "peso_bruto_sem_areia_kg": 21.42,
        "modelo_motobomba": "BMC-100 M"
    },
    {
        "modelo": "FM-75",
        "volume_6h": 132,
        "volume_8h": 176,
        "carga_areia_kg": 300,
        "quant_sacos_25kg": 12,
        "diametro_mm": 770,
        "altura_mm": 1140,
        "peso_bruto_com_areia_kg": 335.74,
        "peso_bruto_sem_areia_kg": 35.74,
        "modelo_motobomba": "BMC-150 M"
    },
    {
        "modelo": "FM-100",
        "volume_6h": 234,
        "volume_8h": 312,
        "carga_areia_kg": 525,
        "quant_sacos_25kg": 21,
        "diametro_mm": 1120,
        "altura_mm": 1215,
        "peso_bruto_com_areia_kg": 579.8,
        "peso_bruto_sem_areia_kg": 54.8,
        "modelo_motobomba": "BM-300 T"
    }
]

BANCO_BOMBAS = [
    {
        "modelo": "BMC-25",
        "potencia_cv": 0.25,
        "vazao_2_mca": 12.14,
        "vazao_4_mca": 11.47,
        "vazao_6_mca": 9.02,
        "vazao_8_mca": 7.28,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-33",
        "potencia_cv": 0.33,
        "vazao_2_mca": None,
        "vazao_4_mca": 11.91,
        "vazao_6_mca": 9.44,
        "vazao_8_mca": 7.43,
        "vazao_10_mca": None,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-50",
        "potencia_cv": 0.5,
        "vazao_2_mca": None,
        "vazao_4_mca": 12.77,
        "vazao_6_mca": 10.12,
        "vazao_8_mca": 8.03,
        "vazao_10_mca": 5.23,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-75",
        "potencia_cv": 0.75,
        "vazao_2_mca": None,
        "vazao_4_mca": 16.26,
        "vazao_6_mca": 13.75,
        "vazao_8_mca": 12.24,
        "vazao_10_mca": 10.28,
        "vazao_12_mca": None,
        "vazao_14_mca": None,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-100",
        "potencia_cv": 1.0,
        "vazao_2_mca": None,
        "vazao_4_mca": 19.88,
        "vazao_6_mca": 19.38,
        "vazao_8_mca": 16.71,
        "vazao_10_mca": 14.83,
        "vazao_12_mca": 13.25,
        "vazao_14_mca": 5.75,
        "vazao_16_mca": None,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMC-150",
        "potencia_cv": 1.5,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 26.79,
        "vazao_8_mca": 23.14,
        "vazao_10_mca": 22.77,
        "vazao_12_mca": 21.95,
        "vazao_14_mca": 18.63,
        "vazao_16_mca": 12.38,
        "vazao_18_mca": 4.46
    },
    {
        "modelo": "BMC-200",
        "potencia_cv": 2.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 28.24,
        "vazao_8_mca": 27.11,
        "vazao_10_mca": 24.35,
        "vazao_12_mca": 20.94,
        "vazao_14_mca": 19.19,
        "vazao_16_mca": 15.92,
        "vazao_18_mca": 3.6
    },
       {
        "modelo": "BMU-200",
        "potencia_cv": 2.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 40.0,
        "vazao_8_mca": 38.27,
        "vazao_10_mca": 36.55,
        "vazao_12_mca": 34.82,
        "vazao_14_mca": 31.36,
        "vazao_16_mca": 27.64,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMU-300",
        "potencia_cv": 3.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 44.4,
        "vazao_8_mca": 42.26,
        "vazao_10_mca": 40.16,
        "vazao_12_mca": 38.2,
        "vazao_14_mca": 36.6,
        "vazao_16_mca": 34.31,
        "vazao_18_mca": None
    },
    {
        "modelo": "BMU-400",
        "potencia_cv": 4.0,
        "vazao_2_mca": None,
        "vazao_4_mca": None,
        "vazao_6_mca": 54.0,
        "vazao_8_mca": 50.4,
        "vazao_10_mca": 46.8,
        "vazao_12_mca": 43.2,
        "vazao_14_mca": 38.4,
        "vazao_16_mca": 35.6,
        "vazao_18_mca": None
    }
]


def formatar_tabela_filtros():
    df = pd.DataFrame(BANCO_FILTROS)
    df = df.rename(columns={
        "modelo": "Modelo",
        "volume_6h": "Volume 6h (m³)",
        "volume_8h": "Volume 8h (m³)",
        "carga_areia_kg": "Carga Areia (kg)",
        "quant_sacos_25kg": "Sacos 25kg",
        "diametro_mm": "Diâmetro (mm)",
        "altura_mm": "Altura (mm)",
        "peso_bruto_com_areia_kg": "Peso c/ Areia (kg)",
        "peso_bruto_sem_areia_kg": "Peso s/ Areia (kg)",
        "modelo_motobomba": "Motobomba"
    })
    return df


def formatar_tabela_bombas():
    df = pd.DataFrame(BANCO_BOMBAS)
    # Reformata colunas de vazão
    df = df.melt(id_vars=["modelo", "potencia_cv"],
                 var_name="Carga",
                 value_name="Vazão (m³/h)")
    df["Carga"] = df["Carga"].str.replace("vazao_", "").str.replace("_mca", " mca")
    df = df.pivot_table(index=["modelo", "potencia_cv"],
                        columns="Carga",
                        values="Vazão (m³/h)").reset_index()
    df = df.rename(columns={
        "modelo": "Modelo",
        "potencia_cv": "Potência (cv)"
    })
    return df


def run():
    st.title("Banco de Dados de Equipamentos")

    with st.expander("Filtros FM Sodramar", expanded=True):
        st.subheader("Características Técnicas dos Filtros")
        df_filtros = formatar_tabela_filtros()
        st.dataframe(
            df_filtros,
            column_config={
                "Volume 6h (m³)": st.column_config.NumberColumn(format="%.0f m³"),
                "Carga Areia (kg)": st.column_config.NumberColumn(format="%.0f kg")
            },
            hide_index=True,
            use_container_width=True
        )

        st.download_button(
            label="Baixar Dados de Filtros (CSV)",
            data=df_filtros.to_csv(index=False).encode('utf-8'),
            file_name='filtros.csv',
            mime='text/csv'
        )

    with st.expander("🔍 Detalhes da Motobomba", expanded=True):
        st.write("### Especificações Técnicas")
        st.write(f"- **Modelo:** {bomba_selecionada['modelo']}")
        st.write(f"- **Potência:** {bomba_selecionada['potencia_cv']} CV")
        st.write(
            f"- **Vazão em {pressao_selecionada} m.c.a:** {bomba_selecionada[f'vazao_{pressao_selecionada}_mca']} m³/h")

        st.write("### Curva de Desempenho")
        # Preparar os dados: coletar pontos (vazão, pressão)
        pontos = []
        possible_pressures = list(range(2, 19, 2))  # Pressões de 2 a 18 m.c.a.
        for press in possible_pressures:
            key = f'vazao_{press}_mca'
            if bomba_selecionada.get(key) is not None:
                pontos.append((bomba_selecionada[key], press))

        if len(pontos) >= 2:
            # Ordenar os pontos por vazão
            pontos_ordenados = sorted(pontos, key=lambda p: p[0])
            vazoes = np.array([p[0] for p in pontos_ordenados])
            pressoes = np.array([p[1] for p in pontos_ordenados])

            # Permitir a seleção do grau do polinômio para ajuste
            grau_polinomio = st.slider(
                "Grau do Polinômio para Ajuste",
                min_value=1,
                max_value=3,
                value=2,
                help="Selecione a complexidade da curva (1 = linear, 2 = quadrática, 3 = cúbica)"
            )

            try:
                # Ajuste polinomial com o grau selecionado
                coeficientes = np.polyfit(vazoes, pressoes, grau_polinomio)
                polinomio = np.poly1d(coeficientes)

                # Gerar pontos suaves para a curva
                vazoes_interp = np.linspace(vazoes.min(), vazoes.max(), 100)
                pressoes_interp = polinomio(vazoes_interp)

                # Criar o gráfico com Plotly
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=vazoes_interp,
                    y=pressoes_interp,
                    mode='lines',
                    name=f'Ajuste Polinomial (Grau {grau_polinomio})',
                    line=dict(color='blue', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=vazoes,
                    y=pressoes,
                    mode='markers',
                    name='Dados Originais',
                    marker=dict(color='red', size=8)
                ))
                fig.update_layout(
                    title=f'Curva de Desempenho - {bomba_selecionada["modelo"]}',
                    xaxis_title='Vazão (m³/h)',
                    yaxis_title='Pressão (m.c.a.)',
                    template='plotly_white',
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

                # Exibir a equação do polinômio
                eq_text = "Equação do Ajuste:\n"
                grau_total = len(coeficientes) - 1
                for i, coef in enumerate(coeficientes):
                    power = grau_total - i
                    eq_text += f"{coef:.3f}"
                    if power > 0:
                        eq_text += f"x^{power} + "
                st.code(eq_text.rstrip(" + "))

            except np.linalg.LinAlgError:
                st.error("Não foi possível calcular o ajuste. Tente reduzir o grau do polinômio ou verifique os dados.")
        else:
            st.warning("Dados insuficientes para gerar a curva")

                # Botão de download
                st.download_button(
                    label="Baixar Dados de Motobombas (CSV)",
                    data=df_bombas.to_csv(index=False).encode('utf-8'),
                    file_name='motobombas.csv',
                    mime='text/csv'
                )

        st.markdown("""
        **Legenda:**
        - Valores em m³/h para diferentes alturas manométricas
        - 'None' indica valor não especificado pelo fabricante
        """)


if __name__ == "__main__":
    run()