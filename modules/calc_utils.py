# modules/calc_utils.py
import math
import numpy as np
from scipy.interpolate import PchipInterpolator

# ==========================================
# CÁLCULOS DE HIDRÁULICA (PERDA DE CARGA)
# ==========================================

def calcular_fator_atrito(Re, D_int, epsilon=0.0000015):
    """
    Calcula o fator de atrito de Darcy-Weisbach.
    
    Args:
        Re (float): Número de Reynolds.
        D_int (float): Diâmetro interno da tubulação (m).
        epsilon (float): Rugosidade absoluta (m). Padrão para PVC: 1.5e-6 m.
        
    Returns:
        float: Fator de atrito (f).
    """
    if Re < 2000:
        return 64 / Re if Re > 0 else 0

    # Constantes da equação de Colebrook-White
    a = epsilon / (3.7 * D_int)
    b = 2.51 / Re

    # Chute inicial (f=0.02 -> x=1/sqrt(0.02) ≈ 7.071)
    x = 7.071
    tol = 1e-8
    max_iter = 100

    for _ in range(max_iter):
        termo = a + b * x
        if termo <= 1e-12:  # Prevenção contra log(0)
            break

        # Função de Colebrook e sua derivada f(x) = x + 2*log10(a + b*x)
        f_x = x + 2 * math.log10(termo)
        df_x = 1 + (2 * b) / (termo * math.log(10) * (x ** 2)) # Derivada em relação a x

        # Atualização Newton-Raphson
        if abs(df_x) < 1e-10: # Evitar divisão por zero na derivada
             break
             
        x_novo = x - (f_x / df_x)

        if abs(x_novo - x) < tol:
            x = x_novo
            break
        x = x_novo

    return 1.0 / (x ** 2)

# ==========================================
# CÁLCULOS DE CURVAS (BOMBAS E SISTEMAS)
# ==========================================

def ajustar_curva_pchip(x_dados, y_dados, num_pontos=100):
    """
    Gera uma curva suavizada usando interpolação PCHIP.
    
    Args:
        x_dados (array-like): Pontos X originais (ex: Vazão).
        y_dados (array-like): Pontos Y originais (ex: Pressão).
        num_pontos (int): Número de pontos na curva interpolada.
        
    Returns:
        tuple: (x_interp, y_interp, interpolador_func)
    """
    # Ordenar dados
    idx = np.argsort(x_dados)
    x_sorted = np.array(x_dados)[idx]
    y_sorted = np.array(y_dados)[idx]

    # Criar interpolador
    pchip = PchipInterpolator(x_sorted, y_sorted)
    
    # Gerar pontos
    x_interp = np.linspace(min(x_sorted), max(x_sorted), num_pontos)
    y_interp = pchip(x_interp)
    
    return x_interp, y_interp, pchip

def encontrar_interseccao_curvas(x_range, y_curva1, func_curva2):
    """
    Encontra interseções entre duas curvas.
    
    Args:
        x_range (array-like): Valores de X onde as curvas estão definidas.
        y_curva1 (array-like): Valores Y da primeira curva (ex: Bomba).
        func_curva2 (callable): Função que gera Y para a segunda curva (ex: Sistema) dado X.
        
    Returns:
        list[tuple]: Lista de tuplas (x, y) dos pontos de interseção.
    """
    pontos_interseccao = []
    
    # Gerar Y para a segunda curva
    try:
        y_curva2 = np.array([func_curva2(x) for x in x_range])
    except Exception:
        return []

    # Diferença entre as curvas
    diferenca = y_curva1 - y_curva2
    
    # Identificar onde a diferença troca de sinal (cruzamento)
    cruzamentos = np.where(np.diff(np.sign(diferenca)))[0]

    for idx in cruzamentos:
        # Interpolação linear para refinar o ponto de interseção
        x0, x1 = x_range[idx], x_range[idx + 1]
        y0, y1 = diferenca[idx], diferenca[idx + 1]
        
        # Prevenção de divisão por zero
        if abs(y1 - y0) > 1e-9:
            # Raiz da diferença (onde dif = 0)
            raiz = x0 - y0 * (x1 - x0) / (y1 - y0)
            
            # Calcular Y no ponto da raiz (usando interpolação linear na curva 1)
            # Poderia usar pchip aqui se passado, mas linear é suficiente para pequenas distâncias
            y_ponto = np.interp(raiz, x_range, y_curva1)
            
            pontos_interseccao.append((raiz, y_ponto))
            
    return pontos_interseccao
