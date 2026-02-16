# modules/database_equipamentos.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
from typing import List, Tuple, Optional, Callable
from tracking import track_access
from modules.data import (
    BANCO_FILTROS,
    BANCO_BOMBAS_BMC,
    BANCO_BOMBAS_BMGC,
    BANCO_BOMBAS_BM,
    BANCO_BOMBAS_BMU,
    BANCO_BOMBAS_SYLLENT,
    BANCO_BOMBAS_JACUZZI
)
from modules.calc_utils import ajustar_curva_pchip, encontrar_interseccao_curvas


def formatar_tabela_filtros() -> pd.DataFrame:
    """
    Formata os dados de filtros para exibição em tabela.
    """
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


@st.cache_data(show_spinner=False)
def carregar_dados_bombas() -> pd.DataFrame:
    """
    Carrega e consolida os dados de todos os bancos de bombas,
    adicionando a coluna 'Linha'. O resultado é cacheado para performance.
    """
    bancos = [
        ("Sodramar - Linha BMC", BANCO_BOMBAS_BMC),
        ("Sodramar - Linha BMGC", BANCO_BOMBAS_BMGC),
        ("Sodramar - Linha BM", BANCO_BOMBAS_BM),
        ("Sodramar - Linha BMU", BANCO_BOMBAS_BMU),
        ("Syllent - Linha piscinas com pré-filtro", BANCO_BOMBAS_SYLLENT),
        ("Jacuzzi - Linha recirculação piscina", BANCO_BOMBAS_JACUZZI),
    ]

    dfs = []
    for linha, dados in bancos:
        df = pd.DataFrame(dados)
        df["Linha"] = linha
        dfs.append(df)

    df_consolidado = pd.concat(dfs, ignore_index=True)

    # Transformar para formato longo (melt)
    df_long = df_consolidado.melt(
        id_vars=["modelo", "potencia_cv", "Linha"],
        var_name="Carga",
        value_name="Vazão (m³/h)"
    )

    # Limpeza segura dos nomes das colunas de carga (sem interpretar regex)
    df_long["Carga"] = (df_long["Carga"]
                        .str.replace("vazao_", "", regex=False)
                        .str.replace("_mca", " mca", regex=False))

    # Pivot para formato wide (cada carga vira uma coluna)
    df_wide = df_long.pivot_table(
        index=["modelo", "potencia_cv", "Linha"],
        columns="Carga",
        values="Vazão (m³/h)"
    ).reset_index()

    # Renomear colunas para exibição
    df_wide = df_wide.rename(columns={
        "modelo": "Modelo",
        "potencia_cv": "Potência (cv)"
    })

    return df_wide


def ordenar_colunas_pressao(colunas):
    """
    Função auxiliar para ordenar colunas de pressão de forma robusta.
    Extrai o número inicial do nome (ex: '2 mca' -> 2.0) e usa como chave.
    Colunas que não começam com número vão para o final.
    """
    def extrair_numero(col):
        match = re.search(r"^(\d+(?:\.\d+)?)", str(col))
        return float(match.group(1)) if match else float('inf')
    return sorted(colunas, key=extrair_numero)


@track_access("database_equipamentos")
def run() -> None:
    st.title("Banco de Dados de Equipamentos")

    # ========== FILTROS ==========
    with st.expander("Filtros FM Sodramar", expanded=False):
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

    # ========== MOTOBOMBAS ==========
    with st.expander("Motobombas", expanded=True):
        st.subheader("Curvas de Desempenho das Motobombas")

        # Carregar dados consolidados (com cache)
        df_bombas_consolidado = carregar_dados_bombas()

        # Seletor de linha (inclui opção "Todas as Linhas")
        linhas_disponiveis = ["Todas as Linhas"] + sorted(df_bombas_consolidado["Linha"].unique())
        linha_selecionada = st.selectbox(
            "Selecione a Linha:",
            options=linhas_disponiveis,
            index=3  # padrão = primeira linha específica
        )

        # Filtrar DataFrame conforme linha escolhida
        if linha_selecionada == "Todas as Linhas":
            df_bombas_filtrado = df_bombas_consolidado.copy()
        else:
            df_bombas_filtrado = df_bombas_consolidado[df_bombas_consolidado["Linha"] == linha_selecionada]

        # Verificar se existem modelos para a linha selecionada
        modelos_disponiveis = df_bombas_filtrado["Modelo"].dropna().unique()
        if len(modelos_disponiveis) == 0:
            st.warning("Nenhum modelo encontrado para a linha selecionada.")
            st.stop()  # Interrompe a execução do módulo

        # Layout: coluna para controles (esquerda) e gráfico (direita)
        cols = st.columns([1, 3])

        with cols[0]:
            # Criar opções de modelo com potência para facilitar a escolha
            df_bombas_filtrado["Modelo_completo"] = (
                df_bombas_filtrado["Modelo"] + " — " + df_bombas_filtrado["Potência (cv)"].astype(str) + " cv"
            )
            opcoes_modelo = df_bombas_filtrado["Modelo_completo"].drop_duplicates().tolist()
            escolha_modelo = st.selectbox("Selecione o Modelo:", options=opcoes_modelo)

            # Extrair o nome real do modelo (parte antes do " — ")
            modelo_selecionado = escolha_modelo.split(" — ")[0]

            # ===== VERIFICAÇÃO DO PONTO DE FUNCIONAMENTO =====
            verificar_ponto = st.checkbox("Verificação do ponto de funcionamento da MB")
            curva_instalacao: Optional[Callable[[float], float]] = None

            if verificar_ponto:
                st.markdown("**Insira os coeficientes da Curva do Sistema**")
                st.markdown("Equação: $H = A \\cdot Q^2 + B \\cdot Q + C$")

                col_coef1, col_coef2, col_coef3 = st.columns(3)
                with col_coef1:
                    coef_a = st.number_input("Coeficiente A", value=0.0023, format="%.6f", step=0.0001)
                with col_coef2:
                    coef_b = st.number_input("Coeficiente B", value=0.0, format="%.4f")
                with col_coef3:
                    coef_c = st.number_input("Coeficiente C", value=0.0, format="%.4f")

                curva_instalacao = lambda Q: coef_a * (Q**2) + coef_b * Q + coef_c

        with cols[1]:
            # Dados do modelo selecionado
            df_filtrado = df_bombas_filtrado[df_bombas_filtrado["Modelo"] == modelo_selecionado]

            # Identificar colunas de pressão (todas após as três primeiras)
            colunas_pressao = df_filtrado.columns[3:]  # Ignora Modelo, Potência, Linha
            colunas_ordenadas = ordenar_colunas_pressao(colunas_pressao)

            # Preparar DataFrame para exibição (sem a coluna Linha)
            colunas_exibicao = ['Modelo', 'Potência (cv)'] + colunas_ordenadas
            df_ordenado = df_filtrado[colunas_exibicao]

            st.dataframe(
                df_ordenado,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Potência (cv)": st.column_config.NumberColumn(format="%.2f cv")
                }
            )

            # Extrair pontos (vazão, pressão) para o gráfico
            pontos: List[Tuple[float, float]] = []
            for coluna in colunas_pressao:
                valor = df_filtrado[coluna].iloc[0]
                if pd.notna(valor):
                    try:
                        pressao = float(coluna.split()[0])  # ex: "2 mca" -> 2.0
                        vazao = float(valor)
                        pontos.append((vazao, pressao))
                    except (ValueError, IndexError):
                        continue  # ignora colunas com formato inesperado

            if len(pontos) >= 2:
                q_point: Optional[float] = None
                h_point: Optional[float] = None
                pontos_ordenados = sorted(pontos, key=lambda x: x[0])
                vazoes = np.array([p[0] for p in pontos_ordenados])
                pressoes = np.array([p[1] for p in pontos_ordenados])

                try:
                    # Ajuste com PCHIP
                    vazoes_interp, pressoes_interp, _ = ajustar_curva_pchip(vazoes, pressoes)

                    pressoes_sistema = []
                    anotacoes = []
                    shapes = []

                    if verificar_ponto and curva_instalacao:
                        try:
                            pressoes_sistema = [curva_instalacao(q) for q in vazoes_interp]
                            pontos_interseccao = encontrar_interseccao_curvas(
                                vazoes_interp, pressoes_interp, curva_instalacao
                            )

                            for q, h in pontos_interseccao:
                                q_point = q
                                h_point = h
                                anotacoes.append(dict(
                                    x=q_point,
                                    y=h_point,
                                    text=f"Ponto de Operação<br>Q: {q_point:.1f} m³/h<br>H: {h_point:.1f} mca",
                                    showarrow=True,
                                    arrowhead=3,
                                    ax=20,
                                    ay=-40
                                ))
                                shapes.append(dict(
                                    type="line",
                                    x0=q_point,
                                    y0=0,
                                    x1=q_point,
                                    y1=h_point,
                                    line=dict(color="#666666", dash="dot", width=1)
                                ))
                        except Exception as e:
                            st.error(f"Erro na curva da instalação: {str(e)}")

                    # Criar gráfico
                    fig = go.Figure()

                    if verificar_ponto and pressoes_sistema:
                        fig.add_trace(go.Scatter(
                            x=vazoes_interp,
                            y=pressoes_sistema,
                            mode='lines',
                            name='Curva da Instalação',
                            line=dict(color='green', width=2, dash='dash')
                        ))

                    fig.add_trace(go.Scatter(
                        x=vazoes_interp,
                        y=pressoes_interp,
                        mode='lines',
                        name='Curva da Bomba (PCHIP)',
                        line=dict(color='blue', width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=vazoes,
                        y=pressoes,
                        mode='markers',
                        name='Dados Originais',
                        marker=dict(color='red', size=8)
                    ))

                    if anotacoes:
                        fig.update_layout(annotations=anotacoes, shapes=shapes)

                    # Título mais informativo (inclui linha)
                    titulo = f'Curva de Desempenho - {modelo_selecionado}'
                    if linha_selecionada != "Todas as Linhas":
                        titulo += f' — {linha_selecionada}'

                    fig.update_layout(
                        title=titulo,
                        xaxis_title='Vazão (m³/h)',
                        yaxis_title='Pressão (m.c.a.)',
                        showlegend=True,
                        template='plotly_white'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    if anotacoes and q_point is not None:
                        st.success("**Ponto de Operação Encontrado**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Vazão Operacional", f"{q_point:.1f} m³/h")
                        with col2:
                            st.metric("Pressão Requerida", f"{h_point:.1f} mca")

                    st.info("Ajuste realizado com PCHIP (Interpolação por Partes Cúbicas Hermite), mais detalhes em Memória de cálculo.")

                except np.linalg.LinAlgError:
                    st.error("Não foi possível calcular o ajuste. Verifique os dados.")
                    # Fallback para interpolação linear
                    vazoes_interp = np.linspace(min(vazoes), max(vazoes), 100)
                    pressoes_interp = np.interp(vazoes_interp, vazoes, pressoes)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=vazoes_interp, y=pressoes_interp, mode='lines', name='Interpolação Linear'))
                    fig.add_trace(go.Scatter(x=vazoes, y=pressoes, mode='markers', name='Dados Originais'))
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Dados insuficientes para gerar a curva (mínimo 2 pontos necessários).")

            # Botão de download dos dados consolidados (inclui coluna Linha)
            st.download_button(
                label="Baixar Dados de Motobombas (CSV)",
                data=df_bombas_consolidado.to_csv(index=False).encode('utf-8'),
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