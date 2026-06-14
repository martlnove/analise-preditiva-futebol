"""
Análise de Confrontos Diretos — Loteca
Terceira etapa do pipeline de dados esportivos.

Carrega as estatísticas de confrontos diretos (geradas pela etapa de
processamento) e oferece um sistema interativo de consulta que calcula
as probabilidades de vitória, empate e derrota entre dois times com base
no histórico real de enfrentamentos.

Entrada: dados/analise_estatisticas_times_confrontos.csv
Uso: python analise_decisoes.py
"""

import pandas as pd
import numpy as np

def carregar_confrontos_diretos():
    """Carrega a planilha de confrontos diretos"""
    try:
        df = pd.read_csv('dados/analise_estatisticas_times_confrontos.csv', encoding='utf-8')
        print(f"Planilha carregada com {len(df)} confrontos diretos")
        return df
    except FileNotFoundError:
        print("Arquivo 'analise_estatisticas_times_confrontos.csv' não encontrado!")
        print("Execute primeiro a análise completa para gerar as estatísticas.")
        return None

def buscar_confronto(df, time1, time2):
    """Busca confronto direto entre dois times"""
    confronto = df[
        ((df['Time 1 - Nome'] == time1) & (df['Time 2 - Nome'] == time2)) |
        ((df['Time 1 - Nome'] == time2) & (df['Time 2 - Nome'] == time1))
    ]

    return confronto.iloc[0] if len(confronto) > 0 else None

def calcular_probabilidades_confronto(confronto):
    """Calcula probabilidades baseadas no confronto direto"""
    if confronto is None:
        return None

    vitorias_time1 = confronto['Time 1 - Vitoria']
    empates = confronto['Time 1 - Empate']
    vitorias_time2 = confronto['Time 1 - Derrota']

    total_jogos = vitorias_time1 + empates + vitorias_time2

    if total_jogos == 0:
        return None

    prob_vitoria_time1 = (vitorias_time1 / total_jogos) * 100
    prob_empate = (empates / total_jogos) * 100
    prob_vitoria_time2 = (vitorias_time2 / total_jogos) * 100

    return {
        'vitoria_time1': prob_vitoria_time1,
        'empate': prob_empate,
        'vitoria_time2': prob_vitoria_time2,
        'total_jogos': total_jogos
    }

def listar_times_disponiveis(df):
    """Lista todos os times disponíveis na planilha"""
    times_time1 = df['Time 1 - Nome'].unique()
    times_time2 = df['Time 2 - Nome'].unique()
    todos_times = sorted(set(list(times_time1) + list(times_time2)))

    return todos_times

def mostrar_resultados_analise(time1, time2, probabilidades, confronto):
    """Mostra os resultados da análise de forma organizada"""

    print(f"\n{'='*80}")
    print(f"ANÁLISE DE CONFRONTO DIRETO: {time1} vs {time2}")
    print(f"{'='*80}")

    if probabilidades is None:
        print("Nenhum histórico de confronto encontrado entre estes times.")
        return

    # Estatísticas do confronto
    print(f"\nHISTÓRICO DE CONFRONTOS DIRETOS:")
    print(f"Total de jogos: {probabilidades['total_jogos']}")
    print(f"{'-'*50}")

    # Determinar qual time é qual no registro
    if confronto['Time 1 - Nome'] == time1:
        vitorias_time1 = confronto['Time 1 - Vitoria']
        empates = confronto['Time 1 - Empate']
        vitorias_time2 = confronto['Time 1 - Derrota']
    else:
        vitorias_time1 = confronto['Time 1 - Derrota']
        empates = confronto['Time 1 - Empate']
        vitorias_time2 = confronto['Time 1 - Vitoria']

    print(f"Vitórias {time1}: {vitorias_time1}")
    print(f"Empates: {empates}")
    print(f"Vitórias {time2}: {vitorias_time2}")

    print(f"\nPROBABILIDADES BASEADAS NO HISTÓRICO:")
    print(f"{'-'*50}")

    resultados = [
        (f"Vitória {time1}", probabilidades['vitoria_time1']),
        ("Empate", probabilidades['empate']),
        (f"Vitória {time2}", probabilidades['vitoria_time2'])
    ]

    # Ordenar por probabilidade (maior primeiro)
    resultados.sort(key=lambda x: x[1], reverse=True)

    for resultado, probabilidade in resultados:
        if probabilidade == max(probabilidades.values()):
            indicador = "[MAIS PROVÁVEL] "
        elif probabilidade > 30:
            indicador = "[ALTA]          "
        elif probabilidade > 20:
            indicador = "[MÉDIA]         "
        else:
            indicador = "[BAIXA]         "

        print(f"{indicador}{resultado:<25} {probabilidade:>6.1f}%")

    print(f"\nANÁLISE ESTATÍSTICA:")
    print(f"{'-'*50}")

    maior_prob = max(probabilidades.items(), key=lambda x: x[1])

    if maior_prob[0] == 'vitoria_time1':
        print(f"{time1} tem vantagem histórica sobre {time2}")
        print(f"Probabilidade de vitória: {maior_prob[1]:.1f}%")
    elif maior_prob[0] == 'vitoria_time2':
        print(f"{time2} tem vantagem histórica sobre {time1}")
        print(f"Probabilidade de vitória: {maior_prob[1]:.1f}%")
    else:
        print(f"Histórico mostra tendência para empates")
        print(f"Probabilidade de empate: {maior_prob[1]:.1f}%")

    # Balanceamento do confronto
    diferenca = abs(probabilidades['vitoria_time1'] - probabilidades['vitoria_time2'])
    if diferenca < 10:
        print("Confronto equilibrado (diferença < 10%)")
    elif diferenca < 20:
        print("Confronto com leve vantagem de um dos times")
    else:
        print("Confronto com vantagem significativa de um dos times")

def buscar_times_sugeridos(df, termo):
    """Busca times que contenham o termo pesquisado"""
    todos_times = listar_times_disponiveis(df)
    termo = termo.upper()

    sugeridos = [time for time in todos_times if termo in time.upper()]
    return sugeridos

def sistema_consultas_interativo():
    """Sistema interativo para consultar confrontos"""

    print("Carregando base de dados de confrontos...")
    df = carregar_confrontos_diretos()

    if df is None:
        return

    print(f"{len(listar_times_disponiveis(df))} times disponíveis para consulta")

    print("\n" + "="*80)
    print("SISTEMA DE CONSULTA - CONFRONTOS DIRETOS")
    print("="*80)
    print("Digite os nomes dos times exatamente como constam na planilha")
    print("Digite 'lista' para ver todos os times disponíveis")
    print("Digite 'sair' para encerrar")
    print("="*80)

    while True:
        print(f"\n{'─'*50}")
        print("NOVA CONSULTA")
        print(f"{'─'*50}")

        # Solicitar Time 1
        time1 = input("\nTime 1: ").strip()

        if time1.lower() == 'sair':
            break
        elif time1.lower() == 'lista':
            todos_times = listar_times_disponiveis(df)
            print(f"\nTimes disponíveis ({len(todos_times)}):")
            print("-" * 50)
            for i in range(0, len(todos_times), 3):
                linha = ""
                for j in range(3):
                    if i + j < len(todos_times):
                        linha += f"• {todos_times[i+j]:<25}"
                print(linha)
            continue

        # Buscar sugestões se time não for encontrado
        confrontos_time1 = df[(df['Time 1 - Nome'] == time1) | (df['Time 2 - Nome'] == time1)]
        if len(confrontos_time1) == 0:
            sugeridos = buscar_times_sugeridos(df, time1)
            if sugeridos:
                print(f"Time '{time1}' não encontrado. Sugestões:")
                for sug in sugeridos[:5]:  # Mostrar até 5 sugestões
                    print(f"   • {sug}")
            else:
                print(f"Time '{time1}' não encontrado.")
            continue

        # Solicitar Time 2
        time2 = input("Time 2: ").strip()

        if time2.lower() == 'sair':
            break
        elif time2.lower() == 'lista':
            todos_times = listar_times_disponiveis(df)
            print(f"\nTimes disponíveis ({len(todos_times)}):")
            print("-" * 50)
            for i in range(0, len(todos_times), 3):
                linha = ""
                for j in range(3):
                    if i + j < len(todos_times):
                        linha += f"• {todos_times[i+j]:<25}"
                print(linha)
            continue

        if time1 == time2:
            print("Os times não podem ser iguais!")
            continue

        # Buscar confronto direto
        confronto = buscar_confronto(df, time1, time2)

        if confronto is None:
            print(f"Nenhum confronto histórico encontrado entre {time1} e {time2}")

            # Mostrar times que cada um já enfrentou
            oponentes_time1 = set(df[df['Time 1 - Nome'] == time1]['Time 2 - Nome']) | set(df[df['Time 2 - Nome'] == time1]['Time 1 - Nome'])
            oponentes_time2 = set(df[df['Time 1 - Nome'] == time2]['Time 2 - Nome']) | set(df[df['Time 2 - Nome'] == time2]['Time 1 - Nome'])

            print(f"{time1} já enfrentou {len(oponentes_time1)} times diferentes")
            print(f"{time2} já enfrentou {len(oponentes_time2)} times diferentes")
            continue

        probabilidades = calcular_probabilidades_confronto(confronto)
        mostrar_resultados_analise(time1, time2, probabilidades, confronto)

        continuar = input("\nFazer outra consulta? (s/n): ").strip().lower()
        if continuar != 's':
            break

    print("\nObrigado por usar o sistema de análise de confrontos!")

# EXECUÇÃO PRINCIPAL
if __name__ == "__main__":
    sistema_consultas_interativo()