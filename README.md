# Análise Preditiva de Futebol — Pipeline de Dados Esportivos

Pipeline completo de dados, da coleta automatizada à predição, aplicado aos resultados da Loteca (Caixa Econômica Federal). O projeto percorre todas as etapas de um fluxo de dados real: **coleta via web scraping → processamento estatístico → análise de confrontos → modelo preditivo**.

> Projeto acadêmico desenvolvido no Bacharelado em Sistemas de Informação — Faculdade Dom Bosco de Porto Alegre.

---

## Visão geral do pipeline

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌──────────────┐
│  1. COLETA  │ →  │ 2. PROCESSAMENTO │ →  │ 3. ANÁLISE  │ →  │ 4. PREDIÇÃO  │
│  (Selenium) │    │  (estatísticas)  │    │ (confrontos)│    │(Random Forest)│
└─────────────┘    └──────────────────┘    └─────────────┘    └──────────────┘
   scraper.py        preprocessamento      analise_decisoes   modelo_preditivo
```

Cada etapa consome a saída da anterior, formando um fluxo de ponta a ponta.

---

## Etapas

### 1. Coleta — `1_coleta/`
Web scraping do site oficial da Loteca usando **Selenium** e **BeautifulSoup**. A classe `LotecaScraper` navega pelos concursos, extrai os resultados dos jogos e salva o histórico em CSV/JSON. Suporta **coleta incremental** (continua a partir do último concurso já coletado), tratamento de erros e paginação automática.

- `scraper.py` — classe `LotecaScraper`
- `main.py` — execução da coleta incremental

### 2. Processamento — `2_processamento/`
A partir do histórico bruto, gera **estatísticas consolidadas por time** (vitórias, empates, derrotas) e analisa **confrontos diretos** entre equipes, produzindo as bases que alimentam as etapas seguintes.

- `preprocessamento.ipynb`

### 3. Análise — `3_analise/`
Sistema interativo de **consulta de confrontos diretos**. Dado um par de times, calcula as probabilidades de vitória, empate e derrota com base no histórico real de enfrentamentos, classificando o equilíbrio do confronto.

- `analise_decisoes.py`

### 4. Predição — `4_predicao/`
Modelo de Machine Learning (**Random Forest**) treinado sobre o histórico para prever o resultado de partidas. Inclui codificação de times e resultados, tratamento de classes raras, avaliação de acurácia e função para prever jogos novos.

- `modelo_preditivo.py`

---

## Stack

| Etapa | Tecnologias |
|---|---|
| Coleta | Python, Selenium, BeautifulSoup, webdriver-manager |
| Processamento | Python, pandas, numpy |
| Análise | Python, pandas, numpy |
| Predição | Python, scikit-learn (Random Forest) |

---

## Como executar

### Pré-requisitos
```bash
pip install -r requirements.txt
```
A etapa de coleta requer o **Google Chrome** instalado (o `webdriver-manager` cuida do driver automaticamente).

### 1. Coletar dados
```bash
cd 1_coleta
python main.py
```
Gera `dados/loteca_historico_completo.csv`.

### 2. Processar estatísticas
Abra e execute `2_processamento/preprocessamento.ipynb`.
Gera `dados/analise_estatisticas_times.csv` e `dados/analise_estatisticas_times_confrontos.csv`.

### 3. Consultar confrontos
```bash
python 3_analise/analise_decisoes.py
```

### 4. Treinar e usar o modelo preditivo
```bash
python 4_predicao/modelo_preditivo.py
```

---

## Estrutura do projeto

```
analise-preditiva-futebol/
├── README.md
├── 1_coleta/
│   ├── scraper.py
│   └── main.py
├── 2_processamento/
│   └── preprocessamento.ipynb
├── 3_analise/
│   └── analise_decisoes.py
├── 4_predicao/
│   └── modelo_preditivo.py
├── dados/
│   └── README.md
├── requirements.txt
└── .gitignore
```

---

## Observações técnicas

- Os principais CSVs estão incluídos em `dados/`, permitindo executar as análises e o modelo sem rodar a coleta. Os dados também podem ser regenerados executando o pipeline desde a etapa de coleta.
- O modelo preditivo usa features derivadas do histórico (times codificados, gols, saldo). Como exercício acadêmico, prioriza a demonstração do fluxo completo de dados sobre a otimização do desempenho preditivo.
- A fonte de dados é pública (resultados oficiais da Loteca / Caixa Econômica Federal).

---

## Autor

**Lucas Souza Silveira Martins**
Bacharelando em Sistemas de Informação — Faculdade Dom Bosco de Porto Alegre
[LinkedIn](https://www.linkedin.com/in/lucasmartinsdev9) · [GitHub](https://github.com/martlnove)
