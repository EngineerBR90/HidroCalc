# Guia de Cálculos Manuais: HidroCalc Piscinas

Este documento fornece o passo a passo detalhado e as fórmulas utilizadas em cada módulo do HidroCalc, permitindo a reprodução manual dos resultados com o auxílio de uma calculadora científica ou planilha.

---

## 1. Constantes e Dados Base

Para todos os cálculos, as seguintes constantes são adotadas conforme normas técnicas e catálogos de fabricantes:

*   **Aceleração da Gravidade ($g$):** $9,81 \text{ m/s}^2$
*   **Viscosidade Cinemática da Água ($\nu$):** $0,896 \times 10^{-6} \text{ m}^2\text{/s}$ (adotada para 24°C)
*   **Rugosidade Absoluta do PVC ($\epsilon$):** $0,0000015 \text{ m}$ (ou $0,0015 \text{ mm}$)
*   **Margem de Segurança:** $1,05$ ($5\%$) aplicada sobre a perda de carga final.

### Tabela de Diâmetros PVC (Tigre/Sodramar)
| Diâmetro Externo (mm) | Diâmetro Interno ($D$) (mm) |
| :--- | :--- |
| 25 | 21,6 |
| 32 | 27,8 |
| 40 | 35,2 |
| 50 | 44,0 |
| 60 | 53,4 |
| 75 | 66,6 |
| 85 | 75,6 |
| 110 | 97,8 |

---

## 2. Módulo: Filtragem

O objetivo é selecionar o filtro adequado com base no volume da piscina.

1.  **Entrada:** Volume da piscina em $m^3$ ($V_{\text{p}}$).
2.  **Critério:** O filtro deve ser capaz de recircular o volume total em 6 horas (padrão residencial).
3.  **Procedimento:**
    *   Consulte o banco de filtros (ex: Linha FM Sodramar).
    *   Selecione o primeiro modelo onde a **Capacidade (6h)** seja $\ge V_{\text{p}}$.
4.  **Cálculo da Vazão de Projeto ($Q$):**
    $$Q = \frac{\text{Capacidade (6h) do Filtro Selecionado}}{6} \quad [m^3/h]$$

---

## 3. Módulo: Transbordo (Borda Infinita)

Calcula a vazão necessária para manter a lâmina de água sobre a borda e o volume do cocho de compensação.

1.  **Entradas:**
    *   $H$: Altura da lâmina desejada ($mm$).
    *   $L$: Comprimento da borda ($m$).
    *   $A$: Área da superfície da piscina ($m^2$).
2.  **Cálculo da Vazão Necessária ($Q_{\text{nec}}$):**
    *   Converta $H$ para metros: $H_m = H / 1000$.
    *   Aplique a fórmula de vertedouro (com fatores de conversão para $m^3/h$):
    $$Q_{\text{nec}} = (1608 \cdot H_m \cdot L) \cdot \sqrt{2 \cdot g \cdot H_m} \quad [m^3/h]$$
3.  **Cálculo do Volume do Cocho ($V_{\text{cocho}}$):**
    *   A reserva deve ser 3x o volume da lâmina da piscina:
    $$V_{\text{cocho}} = A \cdot H_m \cdot 3 \cdot 1000 \quad [Litri]$$

---

## 4. Módulo: Hidromassagem

Baseado na quantidade de dispositivos e vazão nominal.

1.  **Entradas:** Quantidade de dispositivos ($N$) e Marca (Sodramar/Albacete).
2.  **Vazão por Dispositivo ($q$):**
    *   Sodramar: $4,5 \text{ m}^3\text{/h}$
    *   Albacete: $3,3 \text{ m}^3\text{/h}$
3.  **Vazão Total ($Q$):**
    $$Q = N \cdot q \quad [m^3/h]$$

---

## 5. Módulo: Aquecimento (Trocador de Calor)

Calcula a necessidade térmica da piscina e seleciona o trocador de calor Sodramar.

1.  **Entradas Principais:**
    *   Dimensões ($L, W, D$) e Temperatura Desejada ($T_{\text{água}}$).
    *   Região Climática (Fatores Climáticos e Temperaturas Médias).
    *   Condições: Vento, Incidência Solar e Horas de Capa Térmica.
2.  **Cálculo da Energia Dissipada ($E_{\text{btu/h}}$):**
    *   $E_{\text{btu/h}} = \text{Perda}_{\text{base}} \cdot F_{\text{capa}} \cdot F_{\text{vento}} \cdot F_{\text{solar}} \cdot \text{Área}$
3.  **Critérios de Seleção:**
    *   **Capacidade:** $Capacidade_{\text{modelo}} \ge E_{\text{btu/h}}$
    *   **Tempo de Uso:** O equipamento deve suprir a demanda operando no máximo 17 horas/dia no inverno.
4.  **Consumo e Economia:**
    *   $Consumo_{\text{real}} = \frac{Capacidade}{COP_{\text{real}}}$
    *   Economia calculada em relação à resistência elétrica convencional (rendimento 80%).

---

## 6. Módulo: Perda de Carga (Darcy-Weisbach)

Este é o cálculo mais complexo, realizado para cada trecho (Sucção e Recalque).

### Passo 1: Velocidade do Fluxo ($V$)
Converta a vazão $Q$ de $m^3/h$ para $m^3/s$: $Q_s = Q / 3600$.
Obtenha o diâmetro interno $D$ (em metros) na tabela.
$$V = \frac{Q_s}{\frac{\pi \cdot D^2}{4}} \quad [m/s]$$

### Passo 2: Número de Reynolds ($Re$)
$$Re = \frac{V \cdot D}{\nu} = \frac{V \cdot D}{0,896 \times 10^{-6}}$$

### Passo 3: Fator de Atrito ($f$)
*   **Regime Laminar ($Re < 2000$):** $f = 64 / Re$.
*   **Regime Turbulento ($Re \ge 2000$):** Utilizar a Equação de Colebrook-White:
    $$\frac{1}{\sqrt{f}} = -2 \cdot \log_{10} \left( \frac{\epsilon}{3,7 \cdot D} + \frac{2,51}{Re \cdot \sqrt{f}} \right)$$
    *(Nota: Requer iteração. Comece com $f = 0,02$ e substitua no lado direito até o valor convergir).*

### Passo 4: Comprimento Equivalente ($L_{eq}$)
Some o comprimento real dos canos ($L_{\text{real}}$) aos comprimentos equivalentes das conexões (joelhos, registros, etc.) da tabela de projeto.
$$L_{\text{total}} = L_{\text{real}} + \sum L_{eq\_conexões}$$

### Passo 5: Perda de Carga Total ($h_f$)
$$h_f = 1,05 \cdot \left( f \cdot \frac{L_{\text{total}}}{D} \cdot \frac{V^2}{2 \cdot g} \right) \quad [mca]$$

---

## 7. Verificações de Norma (NBR 10.339)

Após os cálculos, compare a velocidade ($V$) com os limites:
*   **Sucção:** $V \le 1,8 \text{ m/s}$
*   **Recalque:** $V \le 3,0 \text{ m/s}$

---
*Manual técnico para uso em paralelo com a aplicação HidroCalc.*
