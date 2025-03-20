# modules/memoria_calculo.py
import streamlit as st
import pandas as pd


def exibir_teoria_colebrook():
    with st.expander("🔍 Teoria do Método Colebrook-White"):
        st.markdown("""
        **Equação Original:**  
        $$
        \\frac{1}{\\sqrt{f}} = -2 \\log_{10}\\left( \\frac{\\varepsilon}{3.7D} + \\frac{2.51}{Re\\sqrt{f}} \\right)
        $$

        **Parâmetros:**
        - $f$: Fator de atrito de Darcy-Weisbach
        - $Re$: Número de Reynolds ($Re = \\frac{VD}{\\nu}$)
        - $\\varepsilon$: Rugosidade absoluta (PVC: 0.0000015 m)
        - $D$: Diâmetro interno (m)

        **Implementação Numérica:**
        - Método Newton-Raphson (10⁻⁸ tolerância)
        - Máximo 100 iterações
        - Chute inicial: $f_0 = 0.02$
        """)

        if st.checkbox("Mostrar algoritmo iterativo"):
            st.code("""
            def calcular_fator_atrito(Re, D_int):
                if Re < 2000:
                    return 64 / Re

                # Configuração Colebrook-White
                x = 7.071  # 1/sqrt(0.02)
                for _ in range(100):
                    termo = (epsilon/(3.7*D)) + (2.51/(Re*x))
                    f_x = x + 2*log10(termo)
                    df_x = 1 + (2.51/(Re*termo*log(10))) / x**2
                    x_novo = x - f_x/df_x

                    if abs(x_novo - x) < 1e-8:
                        break
                    x = x_novo

                return 1/x**2
            """, language='python')


def comparar_metodos(f_colebrook, Re, D_int):
    with st.expander("⚖️ Comparativo com Outros Métodos"):
        st.markdown("""
        | Método          | Tipo       | Precisão | Aplicabilidade          |
        |-----------------|------------|----------|-------------------------|
        | Colebrook-White | Iterativo  | Alta     | Todos regimes turbulentos |
        | Swamee-Jain     | Explícito  | Média    | Re > 5000               |
        | Haaland         | Explícito  | Média    | Re > 4000               |
        """)

        # Cálculos alternativos
        epsilon = 0.0000015
        D = D_int

        # Swamee-Jain
        f_swamee = 0.25 / (math.log10((epsilon / (3.7 * D)) + (5.74 / (Re ** 0.9)))) ** 2

        # Haaland
        f_haaland = 1.8 * math.log10((epsilon / (3.7 * D) ** 1.11 + 6.9 / Re)) ** -2

        # DataFrame comparativo
        df = pd.DataFrame({
            'Método': ['Colebrook-White', 'Swamee-Jain', 'Haaland'],
            'f calculado': [f_colebrook, f_swamee, f_haaland],
            'Diferença (%)': [0,
                              ((f_swamee - f_colebrook) / f_colebrook) * 100,
                              ((f_haaland - f_colebrook) / f_colebrook) * 100]
        })

        st.dataframe(df.style.format({
            'f calculado': '{:.6f}',
            'Diferença (%)': '{:.2f}%'
        }), use_container_width=True)


def exibir_detalhes_calculo(label, resultados):
    with st.expander(f"📊 Detalhes Completo - {label}"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Parâmetros de Entrada**
            - Vazão: {Q:.2f} m³/h
            - Diâmetro externo: {diam_ext} mm
            - Comprimento real: {L_real} m
            """.format(**resultados['parametros']))

            st.markdown("""
            **Conexões Equivalentes**
            - Total: {L_eq:.2f} m
            - Composição: {conexoes}
            """.format(**resultados['conexoes']))

        with col2:
            st.markdown("""
            **Resultados Intermediários**
            - Velocidade: {V:.2f} m/s
            - Reynolds: {Re:.0f}
            - Fator atrito: {f:.6f}
            """.format(**resultados['hidraulica']))

            st.markdown("""
            **Perdas de Carga**
            - Distribuída: {hf_dist:.2f} mca
            - Localizada: {hf_loc:.2f} mca
            - Total (+5%): {hf_total:.2f} mca
            """.format(**resultados['perdas']))


def memoria_calculo(suc, rec, Q_m3h, diam_ext, L_real, conexoes, linha):
    resultados = {
        'parametros': {
            'Q': Q_m3h,
            'diam_ext': diam_ext,
            'L_real': L_real
        },
        'conexoes': {
            'L_eq': suc['L_eq'] if linha == 'suc' else rec['L_eq'],
            'conexoes': dict(conexoes)
        },
        'hidraulica': {
            'V': suc['V'] if linha == 'suc' else rec['V'],
            'Re': suc['Re'] if linha == 'suc' else rec['Re'],
            'f': suc['f'] if linha == 'suc' else rec['f']
        },
        'perdas': {
            'hf_dist': 0.95 * (suc['hf_total'] if linha == 'suc' else rec['hf_total']),
            'hf_loc': 0.05 * (suc['hf_total'] if linha == 'suc' else rec['hf_total']),
            'hf_total': suc['hf_total'] if linha == 'suc' else rec['hf_total']
        }
    }

    st.subheader(f"Memória de Cálculo - Linha de {linha.capitalize()}")

    exibir_detalhes_calculo(linha.capitalize(), resultados)
    comparar_metodos(resultados['hidraulica']['f'],
                     resultados['hidraulica']['Re'],
                     resultados['hidraulica']['D_int'] / 1000)
    exibir_teoria_colebrook()

# Modificação na função main() original (no módulo principal):
# Adicionar após a exibição dos resultados:
# from modules.memoria_calculo import memoria_calculo

# if st.checkbox("Mostrar memória de cálculo completa"):
#     memoria_calculo(suc, rec, Q_m3h, diam_ext_suc, L_real_suc, conexoes_suc, 'sucção')
#     memoria_calculo(suc, rec, Q_m3h, diam_ext_rec, L_real_rec, conexoes_rec, 'recalque')