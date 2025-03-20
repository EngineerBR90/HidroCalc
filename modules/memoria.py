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
        - Precisão científica → Darcy-Weisbach  
        - Rapidez cálculo → Hazen-Williams  
        - Normativas técnicas → Verificar padrão local
        """)

    # Seção 4: Normas e Verificações
    with st.expander("📜 Critérios Normativos"):
        cols = st.columns(2)
        with cols[0]:
            st.subheader("NBR 10.339:2018")
            st.markdown("""
            - Velocidade máxima sucção: **1.8 m/s**  
            - Velocidade máxima recalque: **3.0 m/s**  
                    """)

        with cols[1]:
            st.subheader("ASME B31.3")
            st.markdown("""
            - Fator segurança material: **0.5**  
            - Pressão de teste: **1.5× operação**  
            - Temperatura máxima de serviço PVC: **60°C**
            """)

    # Seção 5: Referências
    with st.expander("📚 Bibliografia Recomendada"):
        st.markdown("""
        1. **Mecânica dos Fluidos** - R. C. Hibbeler  
        2. **Hidráulica Básica** - Rodrigo de Melo Porto  
        3. **Cálculo de Perda de Carga** - Tabela de seleção Schneider (ultimas páginas) 
        4. **NBR 10.339:2018** - Piscina - Projeto, execução e manutenção  
        """)


if __name__ == "__main__":
    run()