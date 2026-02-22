pt-br:

# Documentação Técnica: HidroCalc Piscinas

Esta documentação detalha a arquitetura, estrutura de arquivos e o funcionamento do sistema HidroCalc, uma aplicação voltada para o dimensionamento hidráulico de piscinas.

---

## 1. Visão Geral e Tecnologias

O HidroCalc é uma aplicação web desenvolvida em **Python** utilizando o framework **Streamlit**. Ele automatiza cálculos complexos de engenharia hidráulica baseados em normas técnicas (como a NBR 10.339:2018).

### Tecnologias Principais:
- **Streamlit**: Interface de usuário e roteamento.
- **Pandas & NumPy**: Manipulação de dados e cálculos matriciais.
- **Plotly**: Geração de gráficos dinâmicos de curvas de bombas.
- **SciPy**: Interpolação (PCHIP) para curvas suaves.
- **Bcrypt**: Segurança e hashing de senhas.

---

## 2. Estrutura de Diretórios

```text
HidroCalc/
├── main_app.py           # Ponto de entrada e roteador principal
├── login.py              # Sistema de autenticação
├── tracking.py           # Monitoramento de uso/acessos
├── requirements.txt      # Dependências do projeto
├── .streamlit/           # Configurações de tema e servidor
│   └── config.toml
├── assets/               # Imagens e recursos estáticos
└── modules/              # Módulos funcionais da aplicação
    ├── __init__.py
    ├── data.py           # Banco de dados central (Single Source of Truth)
    ├── calc_utils.py     # Funções matemáticas e utilitários de cálculo
    ├── filtragem.py      # Módulo de Dimensionamento de Filtros
    ├── transbordo.py     # Módulo de Bordas Infinitas
    ├── hidromassagem.py  # Módulo de Hidromassagem
    ├── perda_carga.py    # Cálculo de Perda de Carga (Darcy/Colebrook)
    ├── memoria.py        # Geração de Memória de Cálculo
    ├── database_equipamentos.py # Consulta técnica ao catálogo
    └── report.py         # Relatórios administrativos (Kiara)
```

---

## 3. Arquitetura do Sistema

### 3.1. Fluxo de Autenticação (`login.py`)
O sistema utiliza um controle de acesso baseado em `st.session_state`.
1. O usuário insere credenciais.
2. `login.py` valida o hash da senha usando `bcrypt`.
3. Se bem-sucedido, define `st.session_state["authenticated"] = True` e redireciona para o módulo principal.

### 3.2. Roteamento Central (`main_app.py`)
Este arquivo atua como o "maestro" da aplicação:
- Configura o layout da página (`st.set_page_config`).
- Gerencia a **Sidebar Navigation**, permitindo a troca entre módulos sem perder o estado global.
- Importa dinamicamente os módulos da pasta `modules/` conforme a seleção do usuário.

### 3.3. Base de Dados Centralizada (`modules/data.py`)
Para garantir a consistência, todos os dados técnicos (catálogos da Sodramar, Jacuzzi, Syllent, diâmetros de tubos de PVC e coeficientes de perda de carga) estão concentrados neste arquivo. Qualquer alteração em um equipamento reflete automaticamente em todos os módulos de cálculo.

---

## 4. Núcleo de Cálculos (`modules/calc_utils.py`)

A aplicação diferencia-se pela precisão técnica, implementando:
- **Equação de Colebrook-White**: Resolvida iterativamente pelo método de **Newton-Raphson** para obter o fator de atrito em regime turbulento.
- **Interpolação PCHIP**: Utilizada para gerar curvas de bombas suaves a partir de poucos pontos de dados do fabricante, garantindo que a curva não apresente oscilações irreais.
- **Intersecção de Curvas**: Algoritmo para encontrar o Ponto de Operação do sistema cruzando a Curva da Bomba com a Curva do Hệ thống (perda de carga).

---

## 5. Módulos Funcionais

- **Filtragem**: Seleciona automaticamente o conjunto Filtro + Bomba adequado ao volume da piscina para ciclos de 6 ou 8 horas.
- **Transbordo**: Calcula a vazão de lâmina de água baseada no comprimento da borda e seleciona a bomba para suprir essa vazão.
- **Perda de Carga**: Módulo complexo que permite montar o traçado hidráulico (comprimento, diâmetro e conexões) e calcula a perda total (MCA), verificando limites de velocidade por norma.
- **Memória de Cálculo**: Documenta todas as fórmulas e constantes utilizadas, servindo como auditoria técnica dos resultados apresentados.

---

## 6. Fluxo de Funcionamento (User Journey)

1. **Login**: Autenticação do usuário.
2. **Seleção**: Escolha do módulo na barra lateral (ex: Filtragem).
3. **Input**: Entrada de dados técnicos (Ex: Área, Comprimento, Vazão).
4. **Cálculo**: Processamento via `calc_utils.py` com dados de `data.py`.
5. **Output**: Exibição de resultados em métricas, tabelas detalhadas e gráficos de desempenho Plotly.
6. **Relatório**: Possibilidade de revisar a lógica em "Memória de Cálculo".

---
*Documentação gerada em Fevereiro de 2026.*


-----------------------------x---------------------------

English:

Technical Documentation: HidroCalc Piscinas
This documentation details the architecture, file structure, and system behavior of HidroCalc, an application designed for hydraulic sizing of swimming pools.

1. Overview and Technologies
HidroCalc is a web application developed in Python using the Streamlit framework. It automates complex hydraulic engineering calculations based on technical standards (such as NBR 10.339:2018).
Core Technologies:


Streamlit: User interface and routing.


Pandas & NumPy: Data manipulation and numerical computations.


Plotly: Dynamic pump curve visualization.


SciPy: Interpolation (PCHIP) for smooth curves.


Bcrypt: Security and password hashing.



2. Directory Structure
HidroCalc/
├── main_app.py                 # Entry point and main router
├── login.py                    # Authentication system
├── tracking.py                 # Usage/access monitoring
├── requirements.txt            # Project dependencies
├── .streamlit/                 # Theme and server configuration
│   └── config.toml
├── assets/                     # Images and static resources
└── modules/                    # Application functional modules
    ├── __init__.py
    ├── data.py                 # Central database (Single Source of Truth)
    ├── calc_utils.py           # Mathematical functions and calculation utilities
    ├── filtragem.py            # Filtration Sizing Module
    ├── transbordo.py           # Infinity Edge Module
    ├── hidromassagem.py        # Hydromassage Module
    ├── perda_carga.py          # Head Loss Calculation (Darcy/Colebrook)
    ├── memoria.py              # Calculation Report Generator
    ├── database_equipamentos.py # Technical catalog query
    └── report.py               # Administrative reports (Kiara)


3. System Architecture
3.1. Authentication Flow (login.py)
The system uses access control based on st.session_state:


The user enters credentials.


login.py validates the password hash using bcrypt.


If successful, it sets st.session_state["authenticated"] = True and redirects to the main module.


3.2. Central Routing (main_app.py)
This file acts as the application's orchestrator:


Configures page layout (st.set_page_config).


Manages Sidebar Navigation, allowing module switching without losing global state.


Dynamically imports modules from the modules/ directory based on user selection.


3.3. Centralized Database (modules/data.py)
To ensure consistency, all technical data (Sodramar, Jacuzzi, Syllent catalogs, PVC pipe diameters, and head loss coefficients) are centralized in this file. Any modification to equipment specifications automatically propagates across all calculation modules.

4. Calculation Core (modules/calc_utils.py)
The application emphasizes technical precision by implementing:


Colebrook-White Equation: Solved iteratively using the Newton-Raphson method to determine the friction factor in turbulent flow.


PCHIP Interpolation: Used to generate smooth pump curves from limited manufacturer data points, ensuring physically consistent behavior without unrealistic oscillations.


Curve Intersection Algorithm: Determines the system Operating Point by intersecting the Pump Curve with the System Curve (head loss curve).



5. Functional Modules


Filtration (filtragem.py): Automatically selects the appropriate Filter + Pump set according to pool volume for 6- or 8-hour turnover cycles.


Infinity Edge (transbordo.py): Calculates overflow sheet flow rate based on edge length and selects the pump required to supply this flow.


Head Loss (perda_carga.py): Advanced module that models the hydraulic layout (length, diameter, fittings) and computes total head loss (mH₂O), verifying velocity limits according to standards.


Calculation Report (memoria.py): Documents all formulas and constants used, serving as a technical audit trail of the presented results.



6. Operational Flow (User Journey)


Login: User authentication.


Selection: Module selection in the sidebar (e.g., Filtration).


Input: Entry of technical parameters (e.g., Area, Length, Flow Rate).


Calculation: Processing via calc_utils.py using data from data.py.


Output: Presentation of results in metrics, detailed tables, and Plotly performance graphs.


Report Review: Ability to review the full calculation logic in "Calculation Report".



Documentation generated in February 2026.