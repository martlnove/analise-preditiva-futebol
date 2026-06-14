"""
Modelo Preditivo de Resultados — Loteca
Quarta etapa do pipeline de dados esportivos.

Treina um modelo Random Forest para prever o resultado de partidas
(vitória do mandante / empate / vitória do visitante) a partir do
histórico de confrontos. Inclui pré-processamento, codificação de times
e resultados, avaliação de acurácia e função para prever jogos novos.

Entrada: dados/loteca_historico_completo.csv
Uso: python modelo_preditivo.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Carregar os dados
df = pd.read_csv('dados/loteca_historico_completo.csv', delimiter=';', encoding='utf-8')

# Visualizar as primeiras linhas
print("Primeiras linhas do dataset:")
print(df.head())
print("\nInformações do dataset:")
print(df.info())
# Pré-processamento dos dados
# Criar cópia do dataframe para não alterar o original
df_processed = df.copy()

# Codificar times como números
le_time1 = LabelEncoder()
le_time2 = LabelEncoder()
le_resultado = LabelEncoder()

# Combinar todos os times únicos para garantir mesma codificação
all_teams = pd.concat([df_processed['time1'], df_processed['time2']]).unique()

# Ajustar os encoders com todos os times
le_time1.fit(all_teams)
le_time2.fit(all_teams)

# Aplicar codificação
df_processed['time1_encoded'] = le_time1.transform(df_processed['time1'])
df_processed['time2_encoded'] = le_time2.transform(df_processed['time2'])
df_processed['resultado_encoded'] = le_resultado.fit_transform(df_processed['resultado'])

# Criar features adicionais
df_processed['diferenca_gols'] = df_processed['gols_time1'] - df_processed['gols_time2']
df_processed['total_gols'] = df_processed['gols_time1'] + df_processed['gols_time2']

# Features para o modelo
features = ['time1_encoded', 'time2_encoded', 'gols_time1', 'gols_time2', 'diferenca_gols', 'total_gols']
target = 'resultado_encoded'

X = df_processed[features]
y = df_processed[target]

print(f"Shape do dataset: {X.shape}")
print(f"Classes possíveis: {le_resultado.classes_}")
# Verificar a distribuição das classes
print("Distribuição das classes:")
print(y.value_counts())

# Verificar classes com poucos exemplos
class_counts = y.value_counts()
classes_com_poucos_exemplos = class_counts[class_counts < 2].index.tolist()

if classes_com_poucos_exemplos:
    print(f"\nClasses com menos de 2 exemplos: {classes_com_poucos_exemplos}")
    print("Removendo estas classes do dataset...")
    
    # Filtrar o dataset para remover classes com poucos exemplos
    mask = ~y.isin(classes_com_poucos_exemplos)
    X_filtered = X[mask]
    y_filtered = y[mask]
    
    print(f"Dataset original: {X.shape}")
    print(f"Dataset filtrado: {X_filtered.shape}")
    
    X = X_filtered
    y = y_filtered

# Agora dividir os dados sem stratify
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(f"\nTamanho do conjunto de treino: {X_train.shape}")
print(f"Tamanho do conjunto de teste: {X_test.shape}")

# Verificar distribuição nos conjuntos
print("\nDistribuição no conjunto de treino:")
print(y_train.value_counts())
print("\nDistribuição no conjunto de teste:")
print(y_test.value_counts())

# Treinar o modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Fazer previsões
y_pred = model.predict(X_test)

# Avaliar o modelo
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAcurácia do modelo: {accuracy:.4f} ({accuracy*100:.2f}%)")

# Obter as classes presentes nos dados de teste
classes_presentes = np.unique(np.concatenate([y_test, y_pred]))
target_names_presentes = le_resultado.inverse_transform(classes_presentes)

print("\nRelatório de classificação (apenas classes presentes):")
print(classification_report(y_test, y_pred, target_names=target_names_presentes, zero_division=0))

# Função atualizada para fazer previsões de novos jogos
def prever_jogo(time1, time2):
    try:
        # Codificar os times
        time1_encoded = le_time1.transform([time1])[0]
        time2_encoded = le_time2.transform([time2])[0]
        
        # Criar array de features (usando valores médios para gols)
        features_array = np.array([[time1_encoded, time2_encoded, 0, 0, 0, 0]])
        
        # Fazer previsão
        probabilidades = model.predict_proba(features_array)[0]
        
        # Mapear probabilidades para os resultados
        resultados = le_resultado.classes_
        
        print(f"\n--- Previsão para {time1} vs {time2} ---")
        for i, prob in enumerate(probabilidades):
            print(f"{resultados[i]}: {prob*100:.2f}%")
        
        # Resultado mais provável
        resultado_previsto = resultados[np.argmax(probabilidades)]
        print(f"\nResultado mais provável: {resultado_previsto}")
        
        return probabilidades, resultados
        
    except ValueError as e:
        print(f"Erro: Time não encontrado no histórico. Verifique os nomes.")
        print(f"Times disponíveis: {list(le_time1.classes_)[:10]}...")
        return None, None