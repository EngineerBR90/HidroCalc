# modules/memoria.py
import streamlit as st
import pandas as pd

def run():
    st.set_page_config(page_title="Memória Cálculo", layout="wide")

    # Seção 1: Dados Técnicos
    with st.expander("🔧 Dados Técnicos e Constantes", expanded=True):
        st.subheader("Propriedades do PVC")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("""
            **Diâmetros Nominais (mm):**
            Segundo o catálogo Tigre
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

        with cols[1]:
            st.markdown("""
            **Rugosidade Absoluta:**
            - PVC: ε = 0.0015 mm
           """)

            st.markdown("""
            **Viscosidade da Água:**
            - 20°C: ν = 1.004 × 10⁻⁶ m²/s
            - 30ºC: v = 0.798 × 10⁻⁶ m²/s
            - 40°C: ν = 0.658 × 10⁻⁶ m²/s
            """)

    # Seção 2: Equações Principais
    with st.expander("🧮 Equações Fundamentais", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Darcy-Weisbach", "Hazen-Williams", "Reynolds"])

        with tab1:
            st.markdown("""
            **Equação Geral:**
            $$
            h_f = f\\frac{L}{D}\\frac{V^2}{2g}
            $$

            **Fator de Atrito (f):**
            - Laminar (Re < 2000):  
            $$ f = \\frac{64}{Re} $$
            - Turbulento (Colebrook-White):  
            $$ \\frac{1}{\\sqrt{f}} = -2\\log\\left(\\frac{\\epsilon}{3.7D} + \\frac{2.51}{Re\\sqrt{f}}\\right) $$
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
            Re = \\frac{VD}{\\nu}
            $$

            **Classificação:**
            - Laminar: Re < 2000  
            - Transição: 2000 ≤ Re ≤ 4000  
            - Turbulento: Re > 4000
            """)

    # Seção 3: Comparativo Teórico
    with st.expander("⚖️ Comparação de Métodos"):
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
    with st.expander("📈 Fluxograma de Cálculo", expanded=True):
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

    # Seção 5: Referências
    with st.expander("📚 Bibliografia Recomendada"):
        st.markdown("""
        1. **Mecânica dos Fluidos** - R. C. Hibbeler  
        2. **Hidráulica Básica** - Rodrigo de Melo Porto  
        3. **Cálculo de Perda de Carga** - Tabela de seleção Schneider (últimas páginas)  
        4. **NBR 10.339:2018** - Piscina - Projeto, execução e manutenção  
        """)


if __name__ == "__main__":
    run()