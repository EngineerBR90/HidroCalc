# modules/database_equipamentos.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import List, Tuple, Optional, Any, Callable
from tracking import track_access
from io import StringIO
import sys
from modules.data import BANCO_FILTROS, BANCO_BOMBAS
from modules.calc_utils import ajustar_curva_pchip, encontrar_interseccao_curvas


def formatar_tabela_filtros() -> pd.DataFrame:
    """
    Formata os dados de filtros para exibição em tabela.
    
    Returns:
        pd.DataFrame: DataFrame formatado com colunas renomeadas.
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


def formatar_tabela_bombas() -> pd.DataFrame:
    """
    Formata os dados de bombas para exibição em tabela (pivot).
    Converto o formato de lista de dicionários para um DataFrame pivotado
    onde as colunas são as cargas (mca) e os valores são as vazões.
    
    Returns:
        pd.DataFrame: DataFrame formatado.
    """
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

@track_access("database_equipamentos")  # ← Decorador aplicado
def run() -> None:
    """
    Executa o módulo de Banco de Dados de Equipamentos.
    
    Exibe tabelas de especificações de filtros e curvas de desempenho de bombas.
    Permite verificar o ponto de funcionamento da bomba cruzando com a curva do sistema.
    """
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

    with st.expander("Motobombas Sodramar", expanded=True):
        st.subheader("Curvas de Desempenho das Motobombas")
        df_bombas = formatar_tabela_bombas()

        cols = st.columns([1, 3])
        with cols[0]:
            modelo_selecionado: str = st.selectbox(
                "Selecione o Modelo:",
                options=df_bombas["Modelo"].unique()
            )

            # ===== NOVO CAMPO DE VERIFICAÇÃO =====
            verificar_ponto: bool = st.checkbox("Verificação do ponto de funcionamento da MB")
            curva_instalacao: Optional[Callable[[float], float]] = None

            if verificar_ponto:
                st.markdown("**Insira os coeficientes da Curva do Sistema**")
                st.markdown("Equação: $H = A \\cdot Q^2 + B \\cdot Q + C$")
                
                col_coef1, col_coef2, col_coef3 = st.columns(3)
                with col_coef1:
                    coef_a: float = st.number_input("Coeficiente A", value=0.0023, format="%.6f", step=0.0001)
                with col_coef2:
                    coef_b: float = st.number_input("Coeficiente B", value=0.0, format="%.4f")
                with col_coef3:
                    coef_c: float = st.number_input("Coeficiente C", value=0.0, format="%.4f")

                # Função lambda segura para calcular a curva
                curva_instalacao = lambda Q: coef_a * (Q**2) + coef_b * Q + coef_c

        with cols[1]:
            df_filtrado = df_bombas[df_bombas["Modelo"] == modelo_selecionado]

            # Ordenar colunas de pressão numericamente
            colunas_pressao = df_filtrado.columns[2:]  # Ignorar as duas primeiras colunas (Modelo e Potência)

            # Extrair valores numéricos das colunas e ordenar
            colunas_ordenadas = sorted(colunas_pressao, key=lambda x: float(x.split()[0]))

            # Reordenar o dataframe
            df_ordenado = df_filtrado[['Modelo', 'Potência (cv)'] + colunas_ordenadas]

            st.dataframe(
                df_ordenado,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Potência (cv)": st.column_config.NumberColumn(format="%.2f cv")
                }
            )

            # Processamento dos dados para o gráfico

            # Extrair os pontos (vazão, pressão) dos dados filtrados
            pontos: List[Tuple[float, float]] = []
            for coluna in df_filtrado.columns[2:]:
                if pd.notna(df_filtrado[coluna].iloc[0]):
                    # Extrai a pressão a partir do nome da coluna (ex.: "2 mca")
                    pressao = float(coluna.split()[0])
                    vazao = df_filtrado[coluna].iloc[0]
                    pontos.append((vazao, pressao))

            if len(pontos) >= 2:
                q_point: Optional[float] = None
                h_point: Optional[float] = None
                # Ordenar os pontos com base na vazão (variável independente)
                pontos_ordenados = sorted(pontos, key=lambda x: x[0])
                vazoes = np.array([p[0] for p in pontos_ordenados])
                pressoes = np.array([p[1] for p in pontos_ordenados])

                try:
                    # Ajuste com PCHIP
                    vazoes_interp, pressoes_interp, _ = ajustar_curva_pchip(vazoes, pressoes)

                    # Cálculo da curva da instalação
                    # 'curva_instalacao' é uma função fornecida pelo usuário que retorna a pressão para uma dada vazão
                    pressoes_sistema = []
                    anotacoes = []
                    shapes = []

                    if verificar_ponto and curva_instalacao:
                        try:
                            # Gerar os pontos da curva de instalação para os mesmos valores de vazão interpolados
                            pressoes_sistema = [curva_instalacao(q) for q in vazoes_interp]

                            # Encontrar os pontos de interseção usando a função utilitária
                            pontos_interseccao = encontrar_interseccao_curvas(vazoes_interp, pressoes_interp, curva_instalacao)

                            for q, h in pontos_interseccao:
                                q_point = q
                                h_point = h

                                # Configurar anotações para exibir o ponto de operação
                                anotacoes.append(dict(
                                    x=q_point,
                                    y=h_point,
                                    text=f"Ponto de Operação<br>Q: {q_point:.1f} m³/h<br>H: {h_point:.1f} mca",
                                    showarrow=True,
                                    arrowhead=3,
                                    ax=20,
                                    ay=-40
                                ))

                                # Adicionar linhas auxiliares (shapes) para marcar o ponto de interseção
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

                    # Criação do gráfico com Plotly
                    fig = go.Figure()

                    # Adicionar a curva da instalação, se disponível
                    if verificar_ponto and pressoes_sistema:
                        fig.add_trace(go.Scatter(
                            x=vazoes_interp,
                            y=pressoes_sistema,
                            mode='lines',
                            name='Curva da Instalação',
                            line=dict(color='green', width=2, dash='dash')
                        ))

                    # Adicionar a curva ajustada da motobomba (utilizando PCHIP)
                    fig.add_trace(go.Scatter(
                        x=vazoes_interp,
                        y=pressoes_interp,
                        mode='lines',
                        name='Curva da Bomba (PCHIP)',
                        line=dict(color='blue', width=2)
                    ))

                    # Adicionar os pontos originais (dados do fabricante)
                    fig.add_trace(go.Scatter(
                        x=vazoes,
                        y=pressoes,
                        mode='markers',
                        name='Dados Originais',
                        marker=dict(color='red', size=8)
                    ))

                    # Adicionar anotações e linhas auxiliares, se houver interseção
                    if anotacoes:
                        fig.update_layout(
                            annotations=anotacoes,
                            shapes=shapes
                        )

                    fig.update_layout(
                        title=f'Curva de Desempenho - {modelo_selecionado}',
                        xaxis_title='Vazão (m³/h)',
                        yaxis_title='Pressão (m.c.a.)',
                        showlegend=True,
                        template='plotly_white'
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Exibir informações do ponto de operação, se encontrado
                    if anotacoes and q_point is not None:
                        st.success("**Ponto de Operação Encontrado**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Vazão Operacional", f"{q_point:.1f} m³/h")
                        with col2:
                            st.metric("Pressão Requerida", f"{h_point:.1f} mca")

                    # Exibir mensagem informativa sobre o método PCHIP
                    st.info("Ajuste realizado com PCHIP (Interpolação por Partes Cúbicas Hermite), mais detalhes em Memória de cálculo.")

                except np.linalg.LinAlgError:
                    st.error("Não foi possível calcular o ajuste. Verifique os dados.")
                    # Fallback para interpolação linear
                    vazoes_interp = np.linspace(min(vazoes), max(vazoes), 100)
                    pressoes_interp = np.interp(vazoes_interp, vazoes, pressoes)

                    # Plotar versão simples com interpolação linear
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=vazoes_interp, y=pressoes_interp, mode='lines', name='Interpolação Linear'))
                    fig.add_trace(go.Scatter(x=vazoes, y=pressoes, mode='markers', name='Dados Originais'))
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Dados insuficientes para gerar a curva")

            # Botão de download dos dados
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