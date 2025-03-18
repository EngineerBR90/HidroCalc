# modules/perda_carga.py
import math
import streamlit as st

# Estrutura de dados para comprimentos equivalentes (em metros por unidade)
COMPRIMENTOS_EQUIVALENTES = {
    "PVC": {
        "joelho_90": {
            20: 0.8, 25: 1.0, 32: 1.4, 40: 1.7, 50: 2.1,
            60: 2.7, 75: 3.4, 85: 4.0, 110: 5.2
        },
        "joelho_45": {
            20: 0.4, 25: 0.5, 32: 0.7, 40: 0.8, 50: 1.0,
            60: 1.3, 75: 1.6, 85: 1.9, 110: 2.4
        },
        "valvula_esfera": {
            20: 1.2, 25: 1.5, 32: 2.0, 40: 2.4, 50: 3.0,
            60: 3.8, 75: 4.7, 85: 5.5, 110: 7.1
        },
        "tee_passagem_direta": {
            20: 0.6, 25: 0.8, 32: 1.0, 40: 1.2, 50: 1.5,
            60: 1.9, 75: 2.4, 85: 2.8, 110: 3.6
        },
        "tee_saida_lateral": {
            20: 2.5, 25: 3.1, 32: 4.2, 40: 5.0, 50: 6.3,
            60: 7.9, 75: 9.8, 85: 11.5, 110: 14.8
        },
        "curva_90": {
            20: 0.7, 25: 0.9, 32: 1.2, 40: 1.4, 50: 1.8,
            60: 2.3, 75: 2.9, 85: 3.4, 110: 4.4
        },
        "curva_45": {
            20: 0.3, 25: 0.4, 32: 0.5, 40: 0.6, 50: 0.8,
            60: 1.0, 75: 1.3, 85: 1.5, 110: 1.9
        }
    },
    "Aço": {
        # Adicione valores equivalentes para aço conforme necessário
    }
}

DIAMETROS_PVC = {
    20: 17.0, 25: 21.6, 32: 27.8, 40: 35.2,
    50: 44.0, 60: 53.4, 75: 66.6, 85: 75.6, 110: 97.8
}


def interface_conexoes(tipo_linha, material, diametro_ext):
    with st.expander(f"Conexões - Linha de {tipo_linha}"):
        cols = st.columns(2)
        conexoes = {}

        # Obter diâmetro interno correspondente
        diametro_int = DIAMETROS_PVC[diametro_ext] if material == "PVC" else diametro_ext

        for i, (conexao, valores) in enumerate(COMPRIMENTOS_EQUIVALENTES[material].items()):
            with cols[i % 2]:
                label = conexao.replace("_", " ").title()
                qtd = st.number_input(
                    f"{label} ({valores[diametro_ext]:.1f}m/un):",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"{tipo_linha}_{conexao}"
                )
                conexoes[conexao] = {
                    'quantidade': qtd,
                    'comprimento_unitario': valores[diametro_ext],
                    'comprimento_total': qtd * valores[diametro_ext]
                }
        return conexoes


def calcular_comprimento_equivalente(conexoes):
    return sum([v['comprimento_total'] for v in conexoes.values()])


def main():
    st.title("📉 Cálculo Completo de Perda de Carga")
    st.markdown("---")

    with st.form(key='main_form'):
        # Seção de parâmetros básicos
        col1, col2 = st.columns(2)
        with col1:
            vazao = st.number_input("Vazão (m³/h):", min_value=0.1, value=10.0, step=0.1)
            material_suc = st.selectbox("Material da Sucção:", ["PVC"], index=0)
            diam_ext_suc = st.selectbox("Diâmetro Externo Sucção (mm):", list(DIAMETROS_PVC.keys()))

        with col2:
            comprimento_real_suc = st.number_input("Comprimento Real Sucção (m):", min_value=0.0, value=10.0)
            material_rec = st.selectbox("Material do Recalque:", ["PVC"], index=0)
            diam_ext_rec = st.selectbox("Diâmetro Externo Recalque (mm):", list(DIAMETROS_PVC.keys()))

        # Conexões
        conexoes_suc = interface_conexoes("Sucção", material_suc, diam_ext_suc)
        conexoes_rec = interface_conexoes("Recalque", material_rec, diam_ext_rec)

        if st.form_submit_button("Calcular", type="primary"):
            try:
                # Cálculos preliminares
                diam_int_suc = DIAMETROS_PVC[diam_ext_suc]
                diam_int_rec = DIAMETROS_PVC[diam_ext_rec]

                # Comprimentos equivalentes
                L_eq_suc = calcular_comprimento_equivalente(conexoes_suc)
                L_eq_rec = calcular_comprimento_equivalente(conexoes_rec)

                # Comprimentos totais
                L_total_suc = comprimento_real_suc + L_eq_suc
                L_total_rec = comprimento_real_suc + L_eq_rec

                # Velocidades
                V_suc = (vazao / 3600) / (math.pi * (diam_int_suc / 1000) ** 2 / 4)
                V_rec = (vazao / 3600) / (math.pi * (diam_int_rec / 1000) ** 2 / 4)

                # Alertas de velocidade
                alerta_suc = V_suc > 1.8
                alerta_rec = V_rec > 3.0

                # Exibição dos resultados
                st.success("**Resultados do Cálculo**")
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Velocidade Sucção", f"{V_suc:.2f} m/s",
                              delta="ALERTA!" if alerta_suc else "OK")
                    st.metric("Compr. Equivalente Sucção", f"{L_eq_suc:.1f} m")

                with cols[1]:
                    st.metric("Velocidade Recalque", f"{V_rec:.2f} m/s",
                              delta="ALERTA!" if alerta_rec else "OK")
                    st.metric("Compr. Equivalente Recalque", f"{L_eq_rec:.1f} m")

                # Detalhes técnicos
                with st.expander("Detalhes Completos"):
                    st.write("**Sucção:**")
                    st.json(conexoes_suc)
                    st.write("**Recalque:**")
                    st.json(conexoes_rec)

                if alerta_suc or alerta_rec:
                    st.error("""
                    **Atenção aos limites de velocidade!**
                    - Sucção: Máx 1.8 m/s (NBR 10.339)
                    - Recalque: Máx 3.0 m/s (NBR 10.339)
                    """)

            except Exception as e:
                st.error(f"Erro nos cálculos: {str(e)}")


if __name__ == "__main__":
    main()