# modules/memoria.py
import streamlit as st
from tracking import track_access

st.set_page_config(page_title="Memória Cálculo", layout="wide")

import pandas as pd

@track_access("memoria")
def run():

    # Seção 1: Dados Técnicos
    with st.expander("Dados Técnicos e Constantes", expanded=True):
        st.subheader("Propriedades do PVC")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("""
            **Diâmetros Nominais (mm):**
            - Dados extraídos do catálogo da Tigre
            
            | Ext. | Int. |
            |------|------|
            | 25   | 21.6 |
            | 32   | 27.8 |
            | 40   | 35.2 |
            | 50   | 44.0 |
            | 60   | 53.4 |
            | 75   | 66.6 |
            | 85   | 75.6 |
            | 110  | 97.8 |
            """)

            st.markdown("""
                        **Rugosidade Absoluta:**
                        - PVC: ε = 0.0015 mm
                       """)

        with cols[1]:
            st.markdown("""
            **Viscosidade cinemática adotada nos cálculos:**
              - 24°C: ν = 0.896 × 10⁻⁶ m²/s
           """)

            st.markdown("""
            **Tabela de Viscosidade Cinemática da Água (NIST/IAPWS)**

            | Temperatura (°C) | Viscosidade Cinemática (ν, ×10⁻⁶ m²/s) |
            |-------------------|----------------------------------------|
            | 20                | 1,004                                  |
            | 21                | 0,975                                  |
            | 22                | 0,947                                  |
            | 23                | 0,921                                  |
            | 24                | 0,896                                  |
            | 25                | 0,893                                  |
            | 26                | 0,870                                  |
            | 27                | 0,847                                  |
            | 28                | 0,826                                  |
            | 29                | 0,805                                  |
            | 30                | 0,785                                  |
            | 31                | 0,769                                  |
            | 32                | 0,753                                  |
            | 33                | 0,738                                  |
            | 34                | 0,724                                  |
            | 35                | 0,711                                  |
            """)

    # Seção 2: Equações Principais
    with st.expander("Equações Fundamentais", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Darcy-Weisbach", "Hazen-Williams", "Reynolds"])

        with tab1:
            st.markdown("""
            **Equação Geral:**
            $$
            h_f = f\\frac{L}{D}\\frac{V^2}{2g}
            $$

            **Fator de Atrito (f):**
            - Laminar (Re < 2000):  
            $$
            f = \\frac{64}{Re}
            $$
            - Turbulento (Colebrook-White):  
            $$
            \\frac{1}{\\sqrt{f}} = -2\\log\\left(\\frac{\\varepsilon}{3.7D} + \\frac{2.51}{Re\\sqrt{f}}\\right)
            $$
            """)

        with tab2:
            st.markdown("""
            **Fórmula Empírica:**
            $$
            h_f = 10.643\\cdot C^{-1.85}\\cdot D^{-4.87}\\cdot Q^{1.85}\\cdot L
            $$

            **Coeficiente C:**
            - PVC novo: 150  
            - Aço soldado: 120  
            - Cobre: 140

            *Aplicação típica:*
            - Água em temperatura ambiente
            - Diâmetros > 50 mm
            - Velocidades < 3 m/s
            """)

        with tab3:
            st.markdown("""
            **Número de Reynolds:**
            $$
            Re = \\frac{V\\,D}{\\nu}
            $$

            **Classificação:**
            - Laminar: Re < 2000  
            - Transição: 2000 ≤ Re ≤ 4000  
            - Turbulento: Re > 4000
            """)

    # Seção 3: Comparativo Teórico
    with st.expander("Comparação de Métodos"):
        st.subheader("Darcy-Weisbach vs Hazen-Williams")

        comparativo = pd.DataFrame({
            'Característica': [
                'Base Teórica',
                'Precisão',
                'Complexidade',
                'Aplicação Típica',
                'Limitações'
            ],
            'Darcy-Weisbach': [
                'Mecânica dos fluidos (teórico-experimental)',
                'Alta em todas as condições',
                'Alta (requer cálculo iterativo)',
                'Sistemas pressurizados de alta precisão',
                'Necessita dados de rugosidade'
            ],
            'Hazen-Williams': [
                'Empírico (observação de sistemas reais)',
                'Média em condições padrão',
                'Baixa (fórmula direta)',
                'Projetos prediais e distribuição de água',
                'Não considera temperatura ou viscosidade'
            ]
        })

        st.dataframe(
            comparativo,
            column_config={
                "Darcy-Weisbach": "Darcy-Weisbach",
                "Hazen-Williams": "Hazen-Williams"
            },
            hide_index=True
        )

        st.markdown("""
        **Critério de Escolha:**
        - Precisão científica → Darcy-Weisbach (recomendação de norma e a mais aceita por pesquisadores e autores)
        - Rapidez cálculo → Hazen-Williams (resultados semelhantes à Fórmula de Flamant, que serve de base para tabela da Schneider de perda % para cada 100m de tubulação, )
        """)

    # Seção 4: Fluxograma de cálculo - Módulo Perda de Carga
    with st.expander("Fluxograma de Cálculo", expanded=True):
        st.markdown("""
        ### **Fluxo de Cálculo da Perda de Carga**        
        """)

        with st.container(border=True):
            st.markdown("""
            **1. Entrada de Dados**  
            ```python
            Q_m3h = st.number_input("Vazão (m³/h)")      # Coleta da vazão
            diam_ext = st.selectbox("Diâmetro Externo")    # Seleção do diâmetro
            L_real = st.number_input("Comprimento Real")   # Comprimento da tubulação
            ```
            """)

            st.markdown("**2. Processamento para Cada Linha**")
            with st.container(border=True):
                st.markdown(r"""
                **2.1 Conversão de Diâmetro**  
                $$
                D_{int} = \frac{DIAMETROS[diam_{ext}]}{1000} \quad [m]
                $$

                **2.2 Cálculo da Velocidade**  
                $$
                Q = \frac{Q_{m³/h}}{3600} \quad [m³/s] \\\\
                V = \frac{Q}{\pi D_{int}^2/4} \quad [m/s]
                $$

                **2.3 Número de Reynolds**  
                $$
                Re = \frac{V\,D_{int}}{1.004\times10^{-6}}
                $$
                """)

            st.markdown("**3. Determinação do Fator de Atrito**")
            with st.container(border=True):
                st.markdown(r"""
                $$
                f =
                \begin{cases} 
                \frac{64}{Re}, & \text{se } Re < 2000 \\[10pt]
                \text{Colebrook-White (iterativo):} \\[10pt]
                \frac{1}{\sqrt{f}} = -2.0 \log_{10} \left( \frac{\varepsilon/D}{3.7} + \frac{2.51}{Re\,\sqrt{f}} \right), & \text{se } Re \geq 2000
                \end{cases}
                $$

                Iterativamente, utiliza-se o método de Newton-Raphson:

                $$
                x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}
                $$
                """)

            st.markdown(r"""
            **4. Cálculo de Perdas**  
            $$
            h_f = 1.05 \cdot f \cdot \frac{L_{real} + L_{eq}}{D_{int}} \cdot \frac{V^2}{2g}
            $$
            """)

        st.markdown(r"""
        **5. Verificações Pós-Cálculo**  
        ```python
        # Validação de velocidades
        if V_suc > 1.8: 
            st.error("ALERTA: Excedeu velocidade máxima!")
        if V_rec > 3.0:
            st.error("ALERTA: Excedeu velocidade máxima!")
        ```
        """)

        st.markdown(r"""
        **6. Saída de Resultados**  
        ```python
        st.metric("Perda Total", f"{total_perda:.2f} mca")
        st.json(detalhes_tecnicos)  # Exibe parâmetros calculados
        ```
        """)

        st.markdown(r"""
        ### **Diagrama de Blocos Simplificado**
        ```
        [Interface] → [Coleta Dados] → [Cálculo Linhas]  
            → [Verificação Normas] → [Saída Resultados]
              ↗         ↗ 
            (Sucção)  (Recalque)
        ```
        """)

    # Seção 5: Ajuste de Curva PCHIP
    with st.expander("Ajuste de Curva PCHIP", expanded=True):
        st.markdown("""
        ### **Ajuste de Curva PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)**
        
        O **PCHIP** é um método de interpolação que utiliza polinômios cúbicos definidos por partes para estimar valores entre pontos de dados, mantendo a monotonicidade e evitando oscilações indesejadas (overshoots). Esse método é muito utilizado quando se deseja uma curva suave que preserve a forma dos dados originais, sem criar picos artificiais.

        #### **Formulação Matemática**

        Considere um conjunto de pontos $(x_i, y_i)$, para $i = 0, 1, \\dots, n$. Para cada intervalo $[x_i, x_{i+1}]$, o polinômio interpolador é definido como:

        $$
        p_i(x) = h_{00}(t) \\; y_i + h_{10}(t) \\; (x_{i+1}-x_i) \\; m_i + h_{01}(t) \\; y_{i+1} + h_{11}(t) \\; (x_{i+1}-x_i) \\; m_{i+1},
        $$

        onde:
        
        - $t = \\dfrac{x - x_i}{x_{i+1} - x_i}$ é a variável adimensional (sem unidade), pois:
          - $x$ e $x_i$ estão na mesma unidade, normalmente metros ([m]) no padrão SI.
        - $y_i$ e $y_{i+1}$ são os valores da função nos pontos, com unidade que depende do contexto (por exemplo, [m³/s] se estivermos trabalhando com vazões).
        - $m_i$ e $m_{i+1}$ são as derivadas (inclinacões) nos pontos $x_i$ e $x_{i+1}$, com unidade de $\\dfrac{[y]}{[m]}$, isto é, a unidade de $y$ por metro.

        #### **Funções de Base de Hermite**

        As funções de base são definidas por:
        
        $$
        h_{00}(t) = 2t^3 - 3t^2 + 1,
        $$
        $$
        h_{10}(t) = t^3 - 2t^2 + t,
        $$
        $$
        h_{01}(t) = -2t^3 + 3t^2,
        $$
        $$
        h_{11}(t) = t^3 - t^2.
        $$

        #### **Resumo dos Termos e Unidades**

        - **$x$, $x_i$, $x_{i+1}$:** Variável independente (por exemplo, posição), unidade: metro ([m]).
        - **$y_i$, $y_{i+1}$:** Valores da função (por exemplo, vazão, pressão etc.), unidade: conforme o contexto (ex.: [m³/s], [mca], etc.).
        - **$m_i$, $m_{i+1}$:** Derivadas de $y$ em relação a $x$, unidade: unidade de $y$ por metro (ex.: [m³/s]/[m], [mca]/[m]).
        - **$t$:** Variável adimensional, sem unidade.
        - **$p_i(x)$:** Valor interpolado para $x$ no intervalo $[x_i, x_{i+1}]$, com mesma unidade de $y$.

        #### **Aplicação em Curvas Características de Motobombas**

        No contexto de motobombas hidráulicas, o PCHIP pode ser utilizado para interpolar curvas características (por exemplo, a relação entre vazão e pressão) de forma a preservar a forma real dos dados experimentais. Essa técnica permite estimar o desempenho da bomba em pontos intermediários sem introduzir comportamentos não físicos.

        Em resumo, o ajuste de curva PCHIP proporciona:
        - **Suavidade**: uma curva contínua e diferenciável entre os pontos.
        - **Preservação da forma**: evita oscilações artificiais e mantém a monotonicidade dos dados.
        - **Precisão**: gera valores interpolados fiéis aos dados medidos, úteis para análise e simulação de desempenho.

        **Referências:**
        - F. N. Fritsch e R. E. Carlson, "Monotone Piecewise Cubic Interpolation," SIAM Journal on Numerical Analysis, 1980.
        - Documentação de bibliotecas científicas (por exemplo, SciPy) que implementam o método PCHIP.
        """)

    # Seção 6: Referências
    with st.expander("Bibliografia Recomendada"):
        st.markdown("""
        1. **Mecânica dos Fluidos** - R. C. Hibbeler  
        2. **Hidráulica Básica** - Rodrigo de Melo Porto  
        3. **Cálculo de Perda de Carga** - Tabela de seleção Schneider (últimas páginas)  
        4. **NBR 10.339:2018** - Piscina - Projeto, execução e manutenção  
        """)


if __name__ == "__main__":
    run()
