# modules/perda_carga.py
import math
import streamlit as st
from typing import Dict, Any, Union
from tracking import track_access
from modules.data import DIAMETROS_TUBULACAO as DIAMETROS, CONEXOES_EQUIV
from modules.calc_utils import calcular_fator_atrito


def calcular_linha(Q_m3h: float, diam_ext: str, L_real: float, conexoes: Dict[str, int]) -> Dict[str, float]:
    """
    Calcula as propriedades hidráulicas de uma linha de tubulação.
    
    Args:
        Q_m3h (float): Vazão em m³/h.
        diam_ext (str): Diâmetro externo da tubulação (chave do dicionário DIAMETROS).
        L_real (float): Comprimento real da tubulação em metros.
        conexoes (Dict[str, int]): Dicionário com quantidades de cada tipo de conexão.
        
    Returns:
        Dict[str, float]: Dicionário com resultados (D_int, V, Re, f, L_eq, hf_total).
    """
    D_int = DIAMETROS[diam_ext] / 1000  # Converter para metros
    Q = Q_m3h / 3600

    # Cálculo da velocidade
    A = math.pi * (D_int ** 2) / 4
    V = Q / A if A > 0 else 0

    # Número de Reynolds
    Re = V * D_int / 0.896e-6 if D_int > 0 else 0

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


def interface_conexoes(label: str) -> Dict[str, int]:
    """
    Gera a interface para entrada de quantidades de conexões.
    
    Args:
        label (str): Rótulo para diferenciar seções (ex: "Sucção", "Recalque").
        
    Returns:
        Dict[str, int]: Dicionário com as quantidades inseridas pelo usuário.
    """
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

@track_access("perda_carga")
def main() -> None:
    """
    Executa o módulo de cálculo de Perda de Carga.
    
    Permite calcular a perda de carga em linhas de sucção e recalque,
    verificar velocidades máximas conforme norma e gerar a função da curva do sistema.
    """
    st.title("💧 Cálculo de Perda de Carga")
    st.markdown("""
    ### Métodos Utilizados
    - **Regime Laminar:** Fator de atrito calculado por f = 64/Re  
    - **Regime Turbulento:** Solução iterativa da equação de Colebrook-White (iterações por Newton-Raphson).  
    - **Perdas Localizadas:** Método dos comprimentos equivalentes, com base em tabelas normativas.  
    - **Perda Total:** Soma das perdas distribuídas e localizadas, com margem de 5%.  
    - **Altura geométrica:** Considerada desprezível, uma vez que o sistema succiona e recalca para um mesmo tanque
    - **Velocidades Máximas:** Critérios da NBR 10.339:2018 (1,8 m/s sucção, 3,0 m/s recalque).  
    """)

    with st.form(key='main_form'):
        # Parâmetros básicos
        col1, col2 = st.columns(2)
        with col1:
            Q_m3h: float = st.number_input("Vazão (m³/h):", 0.1, 1000.0, 10.0, 0.1)

        # Configuração Sucção
        st.subheader("Linha de Sucção")
        col_suc1, col_suc2 = st.columns(2)
        with col_suc1:
            diam_ext_suc: str = st.selectbox("Diâmetro Externo (mm):", list(DIAMETROS.keys()), key='suc')
            L_real_suc: float = st.number_input("Comprimento Real (m):", 0.1, 1000.0, 6.0, 6.0, key='L_suc')
        conexoes_suc = interface_conexoes("Sucção")

        # Configuração Recalque
        st.subheader("Linha de Recalque")
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            diam_ext_rec: str = st.selectbox("Diâmetro Externo (mm):", list(DIAMETROS.keys()), key='rec')
            L_real_rec: float = st.number_input("Comprimento Real (m):", 0.1, 1000.0, 12.0, 6.0, key='L_rec')
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

                with st.expander("Função da Curva Característica da Instalação"):
                    # Calcular coeficiente K da curva (H = K*Q²)
                    try:
                        Q_ref = Q_m3h  # Vazão de referência usada no cálculo
                        H_total_ref = total_perda  # Perda total na vazão de referência
                        K = H_total_ref / (Q_ref ** 2) if Q_ref != 0 else 0

                        # Gerar função em formato Python copiável
                        funcao_curva = f"def curva_instalacao(Q):\n    return {K:.6f} * Q**2"

                        st.markdown("**Função Matemática da Curva:**")
                        st.latex(f"H_{{sistema}}(Q) = {K:.4f} \cdot Q^2")

                        st.markdown("**Código Python para Exportação:**")
                        st.code(funcao_curva, language='python')

                        st.info("""
                        **Instruções de uso:**
                        1. Copie a função acima
                        2. Cole no módulo Database_equipamentos
                        3. Compare a curva gerada com a da motobomba para determinar o ponto de funcionamento da MB
                        """)

                    except ZeroDivisionError:
                        st.error("Erro: Vazão não pode ser zero para gerar a curva!")


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