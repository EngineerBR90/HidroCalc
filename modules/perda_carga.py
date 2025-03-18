# modules/perda_carga.py
import math
import streamlit as st

# Dicionário para conversão de diâmetro externo para interno (valores em mm)
DIAMETROS = {
    25: 21.6,
    32: 27.8,
    40: 35.2,
    50: 44.0,
    60: 53.4,
    75: 66.6,
    85: 75.6,
    110: 97.8
}

CONEXOES_EQUIV = {
    "joelho 90º": {
        25: 1.2, 32: 1.5, 40: 2.0, 50: 3.2, 60: 3.4, 75: 3.7, 85: 3.9, 110: 4.3
    },
    "joelho 45º": {
        25: 0.5, 32: 0.7, 40: 1.0, 50: 1.3, 60: 1.5, 75: 1.7, 85: 1.8, 110: 1.9
    },
    "união": {
        25: 0.1, 32: 0.1, 40: 0.1, 50: 0.1, 60: 0.1, 75: 0.15, 85: 0.2, 110: 0.25
    },
    "Tê de passagem direta": {
        25: 0.8, 32: 0.9, 40: 1.5, 50: 2.2, 60: 2.3, 75: 2.4, 85: 2.5, 110: 2.6
    },
    "Tê de saída lateral": {
        25: 2.4, 32: 3.1, 40: 4.6, 50: 7.3, 60: 7.6, 75: 7.8, 85: 8.0, 110: 8.3
    },
    "registro esfera aberto": {
        25: 0.2, 32: 0.3, 40: 0.4, 50: 0.7, 60: 0.8, 75: 0.9, 85: 0.9, 110: 1.0
    },
    "curva 90º": {
        25: 0.5, 32: 0.6, 40: 0.7, 50: 1.2, 60: 1.3, 75: 1.4, 85: 1.5, 110: 1.6
    },
    "curva 45º": {
        25: 0.3, 32: 0.4, 40: 0.5, 50: 0.6, 60: 0.7, 75: 0.8, 85: 0.9, 110: 1.0
    }
}


def calcular_fator_atrito(Re, D_int):
    if Re < 2000:
        return 64 / Re if Re > 0 else 0

    # Parâmetros para PVC
    epsilon = 0.0000015  # Rugosidade absoluta em metros
    D = D_int  # Diâmetro interno em metros

    # Constantes da equação
    a = epsilon / (3.7 * D)
    b = 2.51 / Re

    # Chute inicial (f=0.02 -> x=1/sqrt(0.02) ≈ 7.071)
    x = 7.071
    tol = 1e-8
    max_iter = 100

    for i in range(max_iter):
        termo = a + b * x
        if termo <= 1e-12:  # Prevenção contra log(0)
            break

        # Função de Colebrook e sua derivada
        f_x = x + 2 * math.log10(termo)
        df_x = 1 + (2 * b) / (termo * math.log(10) * (x ** 2))

        # Atualização Newton-Raphson
        x_novo = x - (f_x / df_x)

        if abs(x_novo - x) < tol:
            break
        x = x_novo

    return 1.0 / (x ** 2)


def calcular_linha(Q_m3h, diam_ext, L_real, conexoes):
    D_int = DIAMETROS[diam_ext] / 1000  # Converter para metros
    Q = Q_m3h / 3600

    # Cálculo da velocidade
    A = math.pi * (D_int ** 2) / 4
    V = Q / A if A > 0 else 0

    # Número de Reynolds
    Re = V * D_int / 1.004e-6 if D_int > 0 else 0

    # Fator de atrito
    f = calcular_fator_atrito(Re, D_int)

    # Comprimento equivalente das conexões
    L_eq = sum(qtd * CONEXOES_EQUIV[conexao].get(diam_ext, 0)
               for conexao, qtd in conexoes.items())

    # Perda de carga total (distribuída + localizada) com 5% de margem
    hf_total = 1.05 * f * ((L_real + L_eq) / D_int) * (V ** 2 / (2 * 9.81))

    return {
        'D_int': D_int * 1000,
        'V': V,
        'Re': Re,
        'f': f,
        'L_eq': L_eq,
        'hf_total': hf_total
    }


def interface_conexoes(label):
    with st.expander(f"Conexões - {label}"):
        conexoes = {}
        cols = st.columns(2)
        for i, (conexao, valores) in enumerate(CONEXOES_EQUIV.items()):
            with cols[i % 2]:
                conexoes[conexao] = st.number_input(
                    f"{conexao}:",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"{label}_{conexao}"
                )
        return conexoes


def main():
    st.title("💧 Cálculo de Perda de Carga")
    st.markdown("""
    ### Métodos Utilizados
    - **Regime Laminar:** Fator de atrito calculado por f = 64/Re  
    - **Regime Turbulento:** Solução iterativa da equação de Colebrook-White (iterações por Newton-Raphson).  
    - **Perdas Localizadas:** Método dos comprimentos equivalentes, com base em tabelas normativas.  
    - **Perda Total:** Soma das perdas distribuídas e localizadas, com margem de 5%.  
    - **Altura geométrica:** Considerada desprezível, uma vez que o sistema succiona e recalca para um mesmo tanque
    - **Velocidades Máximas:** Critérios da NBR 10.339 (1,8 m/s sucção, 3,0 m/s recalque).  
    """)

    with st.form(key='main_form'):
        # Parâmetros básicos
        col1, col2 = st.columns(2)
        with col1:
            Q_m3h = st.number_input("Vazão (m³/h):", 0.1, 1000.0, 10.0, 0.1)

        # Configuração Sucção
        st.subheader("Linha de Sucção")
        col_suc1, col_suc2 = st.columns(2)
        with col_suc1:
            diam_ext_suc = st.selectbox("Diâmetro Externo (mm):", DIAMETROS.keys(), key='suc')
            L_real_suc = st.number_input("Comprimento Real (m):", 0.1, 1000.0, 10.0, 0.1, key='L_suc')
        conexoes_suc = interface_conexoes("Sucção")

        # Configuração Recalque
        st.subheader("Linha de Recalque")
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            diam_ext_rec = st.selectbox("Diâmetro Externo (mm):", DIAMETROS.keys(), key='rec')
            L_real_rec = st.number_input("Comprimento Real (m):", 0.1, 1000.0, 50.0, 0.1, key='L_rec')
        conexoes_rec = interface_conexoes("Recalque")

        if st.form_submit_button("Calcular", type="primary"):
            try:
                # Cálculos para cada linha
                suc = calcular_linha(Q_m3h, diam_ext_suc, L_real_suc, conexoes_suc)
                rec = calcular_linha(Q_m3h, diam_ext_rec, L_real_rec, conexoes_rec)

                # Alertas de velocidade
                alerta_suc = suc['V'] > 1.8
                alerta_rec = rec['V'] > 3.0

                # Exibição de resultados
                st.success("**Resultados do Cálculo**")

                cols = st.columns(2)
                with cols[0]:
                    st.subheader("Sucção")
                    st.metric("Diâmetro Interno", f"{suc['D_int']:.1f} mm")
                    st.metric("Velocidade", f"{suc['V']:.2f} m/s",
                              delta="ALERTA!" if alerta_suc else "OK")
                    st.metric("Perda Total", f"{suc['hf_total']:.2f} mca")

                with cols[1]:
                    st.subheader("Recalque")
                    st.metric("Diâmetro Interno", f"{rec['D_int']:.1f} mm")
                    st.metric("Velocidade", f"{rec['V']:.2f} m/s",
                              delta="ALERTA!" if alerta_rec else "OK")
                    st.metric("Perda Total", f"{rec['hf_total']:.2f} mca")

                # ===== NOVO BLOCO ADICIONADO =====
                st.markdown("---")
                st.subheader("🔥 Resultado Total da Instalação")

                total_perda = suc['hf_total'] + rec['hf_total']
                cols_total = st.columns([1, 2])
                with cols_total[0]:
                    st.metric(
                            label="**Perda de Carga Total**",
                            value=f"{total_perda:.2f} mca",
                            help="Soma das perdas de sucção e recalque"
                        )
                with cols_total[1]:
                        st.write("**Composição:**")
                        st.info(f"""
                                  - Sucção: {suc['hf_total']:.2f} mca  
                                  - Recalque: {rec['hf_total']:.2f} mca
                                  - Altura geométrica: Considerada desprezível, uma vez que o sistema succiona e recalca para um mesmo tanque  
                                  *Inclui perdas distribuídas, localizadas e margem de 5%*
                                  """)

                # Detalhes técnicos
                with st.expander("Detalhes Técnicos"):
                    st.write("**Sucção:**")
                    st.json({
                        "Reynolds": f"{suc['Re']:.0f}",
                        "Fator Atrito": f"{suc['f']:.6f}",
                        "Comp. Equivalente": f"{suc['L_eq']:.2f} m"
                    })
                    st.write("**Recalque:**")
                    st.json({
                        "Reynolds": f"{rec['Re']:.0f}",
                        "Fator Atrito": f"{rec['f']:.6f}",
                        "Comp. Equivalente": f"{rec['L_eq']:.2f} m"
                    })



                # Alertas normativos
                if alerta_suc or alerta_rec:
                    st.error("""
                    **Limites de velocidade fluxo excedidos (NBR 10.339:2018):**
                    - Sucção: Máx 1.8 m/s
                    - Recalque: Máx 3.0 m/s
                    
                    Ajuste os diâmetros da linha ou motobomba para de menor vazão!
                    """)

            except Exception as e:
                st.error(f"Erro nos cálculos: {str(e)}")
                st.stop()


if __name__ == "__main__":
    main()