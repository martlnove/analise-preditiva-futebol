# Dados

Esta pasta contém os datasets do pipeline. Os arquivos abaixo já estão incluídos no repositório, permitindo executar as etapas de análise e predição sem precisar rodar a coleta.

## Arquivos incluídos

### `loteca_historico_completo.csv`
Histórico bruto de concursos da Loteca, gerado pela etapa de **coleta** (`1_coleta/`).
- **Separador:** ponto-e-vírgula (`;`)
- **Encoding:** UTF-8
- **Conteúdo:** resultados dos jogos (times, gols, resultado) por concurso
- **Usado por:** etapa 2 (processamento) e etapa 4 (modelo preditivo)

### `analise_estatisticas_times_confrontos.csv`
Estatísticas de confrontos diretos entre times, gerado pela etapa de **processamento** (`2_processamento/`).
- **Separador:** vírgula (`,`)
- **Encoding:** UTF-8
- **Conteúdo:** histórico de vitórias, empates e derrotas entre cada par de times
- **Usado por:** etapa 3 (análise de confrontos)

## Arquivo gerado ao executar o pipeline

### `analise_estatisticas_times.csv`
Estatísticas consolidadas por time. **Não está incluído** no repositório — é gerado ao executar o notebook `2_processamento/preprocessamento.ipynb`.

## Regenerando os dados

Todo o conjunto de dados pode ser regenerado do zero executando o pipeline na ordem:

1. `1_coleta/main.py` — coleta o histórico a partir do site da Loteca
2. `2_processamento/preprocessamento.ipynb` — gera as estatísticas e confrontos

## Observação

Os dados são resultados públicos da Loteca (Caixa Econômica Federal). Arquivos JSON intermediários gerados pela coleta não são versionados (ver `.gitignore`).
