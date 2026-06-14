"""
Módulo para web scraping da Loteca (Caixa Econômica Federal)
Usa Selenium para lidar com conteúdo dinâmico (AngularJS)
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import os
import time


class LotecaScraper:
    def __init__(self, url=None, headless=True):
        self.url = url or "https://loterias.caixa.gov.br/Paginas/Loteca.aspx"
        self.headless = headless
        self.driver = None
        self.dados = None

        self._criar_diretorio_data()

    def _criar_diretorio_data(self):
        if not os.path.exists('dados'):
            os.makedirs('dados')
            print("Diretório 'dados/' criado")

    def _iniciar_driver(self):
        "Inicializa o WebDriver do Chrome"
        try:
            print("Configurando navegador...")

            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # Aumentar timeouts para evitar desconexões
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # Manter a sessão ativa
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })

            # Instalar e configurar o ChromeDriver automaticamente
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Definir timeouts
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)

            print("Navegador configurado com sucesso!")

        except Exception as e:
            print(f"Erro ao inicializar navegador: {e}")
            raise

    def _fechar_driver(self):
        "Fecha o WebDriver"
        if self.driver:
            self.driver.quit()
            self.driver = None

    def obter_pagina(self):
        "Faz a requisição HTTP e aguarda o carregamento do JavaScript"
        try:
            if not self.driver:
                self._iniciar_driver()

            print(f"Acessando: {self.url}")
            self.driver.get(self.url)

            # Aguardar o carregamento da tabela de jogos (AngularJS)
            print("Aguardando carregamento dos dados...")
            wait = WebDriverWait(self.driver, 20)

            # Aguardar o loading desaparecer primeiro
            try:
                loading = self.driver.find_element(By.ID, 'loading')
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element(loading)
                )
            except:
                pass  # Loading não existe ou já está invisível

            # Esperar até que a tabela tenha linhas com dados reais
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-d tr.ng-scope')))
            time.sleep(2)

            print("Página carregada com sucesso!")
            return self.driver.page_source

        except Exception as e:
            print(f"Erro ao acessar a página: {e}")
            return None

    def extrair_dados(self, html):
        if not html:
            print("️  HTML vazio ou inválido")
            return None

        try:
            soup = BeautifulSoup(html, 'html.parser')

            dados = {
                'concurso': None,
                'data_sorteio': None,
                'data_extracao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'jogos': [],
            }

            print("Extraindo dados da página...")

            # Extrair concurso e data do elemento <span class="ng-binding">
            # Formato esperado: "Concurso 1213 (29/09/2025)"
            concurso_elemento = soup.find('span', class_='ng-binding')
            if concurso_elemento:
                texto_completo = concurso_elemento.text.strip()
                print(f"   Texto do concurso encontrado: {texto_completo}")

                # Verificar se não é um template AngularJS
                if '{{' not in texto_completo and 'inexistente' not in texto_completo.lower():
                    # Extrair número do concurso e data usando regex
                    import re
                    match = re.search(r'Concurso\s+(\d+)\s+\((\d{2}/\d{2}/\d{4})\)', texto_completo)
                    if match:
                        dados['concurso'] = match.group(1)
                        dados['data_sorteio'] = match.group(2)
                        print(f"   Concurso: {dados['concurso']}")
                        print(f"   Data: {dados['data_sorteio']}")
                    else:
                        # Fallback: usar o texto completo
                        dados['concurso'] = texto_completo
                else:
                    print("   ️  Concurso ainda não carregado (template AngularJS detectado)")
            else:
                print("   ️  Elemento do concurso não encontrado")

            # Extrair jogos da tabela
            tabela = soup.find('table', class_='table-d')

            if tabela:
                # Encontrar todas as linhas com ng-repeat (apenas linhas de jogos, sem header)
                linhas = tabela.find_all('tr', class_='ng-scope')
                print(f"   Encontradas {len(linhas)} linhas de jogos")

                for linha in linhas:
                    colunas = linha.find_all('td')

                    if len(colunas) >= 6:
                        # Extrair textos
                        numero_jogo = colunas[0].text.strip()
                        gols_time1 = colunas[1].text.strip()
                        time1 = colunas[2].text.strip()
                        time2 = colunas[4].text.strip()
                        gols_time2 = colunas[5].text.strip()

                        # Verificar se não são templates AngularJS
                        if '{{' in numero_jogo or '{{' in time1 or '{{' in time2:
                            print("   ️  Dados ainda não carregados (templates AngularJS)")
                            continue

                        # Determinar o resultado pela classe 'selected'
                        resultado = None
                        if 'selected' in colunas[1].get('class', []):
                            resultado = time1  # Time 1 venceu
                        elif 'selected' in colunas[3].get('class', []):
                            resultado = 'EMPATE'  # Empate
                        elif 'selected' in colunas[5].get('class', []):
                            resultado = time2  # Time 2 venceu

                        jogo = {
                            'numero': numero_jogo,
                            'time1': time1,
                            'gols_time1': gols_time1,
                            'time2': time2,
                            'gols_time2': gols_time2,
                            'resultado': resultado
                        }

                        dados['jogos'].append(jogo)

                print(f"{len(dados['jogos'])} jogos extraídos com sucesso")
            else:
                print("   ️  Tabela de jogos não encontrada")

            self.dados = dados
            return dados

        except Exception as e:
            print(f"Erro inesperado ao extrair dados: {e}")
            import traceback
            traceback.print_exc()
            return None

    def salvar_json(self, dados=None, nome_arquivo=None):
        dados = dados or self.dados

        if not dados:
            print("️  Nenhum dado para salvar em JSON")
            return None

        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concurso = dados.get('concurso', 'sem_concurso')
            concurso_limpo = ''.join(c for c in str(concurso) if c.isalnum() or c in ('_', '-'))
            nome_arquivo = f"dados/loteca_{concurso_limpo}_{timestamp}.json"

        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            print(f"JSON salvo: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")
            return None

    def salvar_csv(self, dados=None, nome_arquivo=None):
        dados = dados or self.dados

        if not dados or not dados.get('jogos'):
            print("️  Nenhum dado de jogos para salvar em CSV")
            return None

        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            concurso = dados.get('concurso', 'sem_concurso')
            concurso_limpo = ''.join(c for c in str(concurso) if c.isalnum() or c in ('_', '-'))
            nome_arquivo = f"dados/loteca_jogos_{concurso_limpo}_{timestamp}.csv"

        try:
            df = pd.DataFrame(dados['jogos'])
            df['concurso'] = dados.get('concurso')
            df['data_sorteio'] = dados.get('data_sorteio')
            df['data_extracao'] = dados.get('data_extracao')

            colunas_ordem = ['concurso', 'data_sorteio', 'data_extracao', 'numero',
                           'time1', 'gols_time1', 'time2', 'gols_time2', 'resultado', 'dia']
            colunas_existentes = [col for col in colunas_ordem if col in df.columns]
            df = df[colunas_existentes]

            df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
            print(f"CSV salvo: {nome_arquivo}")
            return nome_arquivo

        except Exception as e:
            print(f"Erro ao salvar CSV: {e}")
            return None

    def salvar_dados(self, dados=None, formatos=['json', 'csv']):
        dados = dados or self.dados
        arquivos_salvos = {}

        if 'json' in formatos:
            arquivo_json = self.salvar_json(dados)
            if arquivo_json:
                arquivos_salvos['json'] = arquivo_json

        if 'csv' in formatos:
            arquivo_csv = self.salvar_csv(dados)
            if arquivo_csv:
                arquivos_salvos['csv'] = arquivo_csv

        return arquivos_salvos

    def buscar_concurso(self, numero_concurso):
        try:
            wait = WebDriverWait(self.driver, 15)

            # Aguardar o loading desaparecer (se existir)
            try:
                loading = self.driver.find_element(By.ID, 'loading')
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element(loading)
                )
            except:
                pass

            # Encontrar o campo de busca
            campo_busca = wait.until(
                EC.presence_of_element_located((By.ID, 'buscaConcurso'))
            )

            # Limpar e digitar o número do concurso
            campo_busca.clear()
            campo_busca.send_keys(str(numero_concurso))

            # Pressionar Enter
            from selenium.webdriver.common.keys import Keys
            campo_busca.send_keys(Keys.RETURN)

            print(f"Buscando concurso {numero_concurso}...")

            # Aguardar o carregamento
            time.sleep(3)

            # Aguardar loading desaparecer
            try:
                loading = self.driver.find_element(By.ID, 'loading')
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element(loading)
                )
            except:
                pass

            return True

        except Exception as e:
            print(f"Erro ao buscar concurso: {e}")
            return False

    def clicar_proximo(self):
        try:
            # Verificar se o driver ainda está ativo
            if not self.driver or not self.driver.session_id:
                print("Sessão do navegador perdida, reiniciando...")
                self._iniciar_driver()
                return False

            wait = WebDriverWait(self.driver, 15)

            # Aguardar o loading desaparecer (se existir)
            try:
                loading = self.driver.find_element(By.ID, 'loading')
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element(loading)
                )
            except:
                pass

            time.sleep(1)

            # Encontrar o botão Próximo
            botao_proximo = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Próximo')]"))
            )

            # Scroll até o botão
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_proximo)
            time.sleep(0.5)

            # Tentar clicar
            try:
                botao_proximo.click()
            except:
                print("Usando clique via JavaScript...")
                self.driver.execute_script("arguments[0].click();", botao_proximo)

            # Aguardar o carregamento
            time.sleep(3)

            # Aguardar loading desaparecer após o clique
            try:
                loading = self.driver.find_element(By.ID, 'loading')
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element(loading)
                )
            except:
                pass

            return True

        except Exception as e:
            print(f"Não foi possível clicar em 'Próximo': {e}")
            return False

    def obter_ultimo_concurso(self, arquivo_csv='dados/loteca_historico_completo.csv'):
        try:
            if not os.path.exists(arquivo_csv):
                print(f"Arquivo {arquivo_csv} não encontrado. Iniciando do concurso 1.")
                return 0

            df = pd.read_csv(arquivo_csv, sep=';', encoding='utf-8-sig')

            if df.empty or 'concurso' not in df.columns:
                print("CSV vazio ou sem coluna 'concurso'. Iniciando do concurso 1.")
                return 0

            # Converter para numérico e pegar o maior
            df['concurso'] = pd.to_numeric(df['concurso'], errors='coerce')
            ultimo_concurso = int(df['concurso'].max())

            print(f"Último concurso encontrado no CSV: {ultimo_concurso}")
            return ultimo_concurso

        except Exception as e:
            print(f"Erro ao ler CSV: {e}. Iniciando do concurso 1.")
            return 0

    def executar(self, salvar=True, formatos=['json', 'csv'], concurso_inicial=None, max_concursos=50):
        print("\n" + "=" * 60)
        print("   INICIANDO SCRAPING DA LOTECA")
        print("=" * 60 + "\n")

        # Se não especificou concurso inicial, buscar do CSV
        if concurso_inicial is None:
            ultimo_concurso = self.obter_ultimo_concurso()
            concurso_inicial = ultimo_concurso + 1
            print(f"Iniciando do concurso: {concurso_inicial}")

        print(f"Modo: Ordem Crescente (Concurso {concurso_inicial} até +{max_concursos})")
        print("=" * 60 + "\n")

        todos_dados = []
        contador = 0

        try:
            # 1. Acessar a página inicial
            if not self.driver:
                self._iniciar_driver()

            print(f"Acessando: {self.url}")
            self.driver.get(self.url)
            time.sleep(3)

            # 2. Buscar o concurso inicial
            if not self.buscar_concurso(concurso_inicial):
                print("\nFalha ao buscar concurso inicial")
                return None

            tentativas_falhas = 0
            max_tentativas = 3

            # Loop para coletar dados em ordem crescente
            while contador < max_concursos:
                try:
                    # Obter HTML da página atual
                    html = self.driver.page_source

                    # Extrair os dados do concurso atual
                    dados = self.extrair_dados(html)

                    if not dados or not dados.get('jogos'):
                        print("\nFalha ao extrair dados, pulando...")
                        tentativas_falhas += 1

                        if tentativas_falhas >= max_tentativas:
                            print(f"\n{max_tentativas} tentativas falhas consecutivas. Encerrando...")
                            break
                    else:
                        tentativas_falhas = 0
                        concurso_atual = dados.get('concurso')
                        contador += 1

                        print(f"\n[{contador}/{max_concursos}] Concurso {concurso_atual} extraído!")
                        todos_dados.append(dados)

                        # Verificar se atingiu o máximo
                        if contador >= max_concursos:
                            print(f"\nLimite de {max_concursos} concursos atingido!")
                            break

                    # Clicar no botão Próximo
                    print(f"Navegando para o próximo concurso...")
                    if not self.clicar_proximo():
                        print("\nNão há mais concursos ou erro ao clicar em Próximo")
                        break

                except Exception as e:
                    print(f"\nErro durante o loop: {e}")
                    tentativas_falhas += 1

                    if tentativas_falhas >= max_tentativas:
                        print(f"\nMuitos erros consecutivos. Salvando dados coletados...")
                        break

            # Salvar os dados (adicionar aos existentes)
            if salvar and todos_dados:
                print(f"\nSalvando dados de {len(todos_dados)} concursos...")

                if 'json' in formatos:
                    self._salvar_json_consolidado(todos_dados)

                if 'csv' in formatos:
                    self._adicionar_ao_csv(todos_dados)

            print("\n" + "=" * 60)
            print(f"   SCRAPING CONCLUÍDO - {len(todos_dados)} CONCURSOS")
            print("=" * 60)

            # Exibir resumo
            if todos_dados:
                self.exibir_resumo(todos_dados)

            return todos_dados

        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário!")
            print(f"Salvando {len(todos_dados)} concursos coletados...")

            if todos_dados and salvar:
                self._adicionar_ao_csv(todos_dados)

            raise

        except Exception as e:
            print(f"\nErro crítico: {e}")
            print(f"Salvando {len(todos_dados)} concursos coletados...")

            if todos_dados and salvar:
                self._adicionar_ao_csv(todos_dados)

            import traceback
            traceback.print_exc()
            return todos_dados if todos_dados else None

        finally:
            self._fechar_driver()

    def _salvar_json_consolidado(self, lista_dados, nome_arquivo='dados/loteca_historico_completo.json'):
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(lista_dados, f, ensure_ascii=False, indent=4)
            print(f"   JSON consolidado salvo: {nome_arquivo}")
        except Exception as e:
            print(f"   Erro ao salvar JSON consolidado: {e}")

    def _adicionar_ao_csv(self, lista_dados, nome_arquivo='dados/loteca_historico_completo.csv'):
        try:
            todos_jogos = []

            # Consolidar todos os jogos dos novos concursos
            for dados in lista_dados:
                concurso = dados.get('concurso')
                data_sorteio = dados.get('data_sorteio')
                data_extracao = dados.get('data_extracao')

                for jogo in dados.get('jogos', []):
                    jogo_completo = jogo.copy()
                    jogo_completo['concurso'] = concurso
                    jogo_completo['data_sorteio'] = data_sorteio
                    jogo_completo['data_extracao'] = data_extracao
                    todos_jogos.append(jogo_completo)

            # Criar DataFrame com novos dados
            df_novos = pd.DataFrame(todos_jogos)

            # Reordenar colunas
            colunas_ordem = ['concurso', 'data_sorteio', 'data_extracao', 'numero',
                           'time1', 'gols_time1', 'time2', 'gols_time2', 'resultado']
            colunas_existentes = [col for col in colunas_ordem if col in df_novos.columns]
            df_novos = df_novos[colunas_existentes]

            # Verificar se o arquivo já existe
            if os.path.exists(nome_arquivo):
                # Ler arquivo existente
                df_existente = pd.read_csv(nome_arquivo, sep=';', encoding='utf-8-sig')

                # Concatenar dados antigos + novos
                df_final = pd.concat([df_existente, df_novos], ignore_index=True)

                print(f"   Adicionando {len(todos_jogos)} novos jogos ao CSV existente")
            else:
                df_final = df_novos
                print(f"   Criando novo CSV com {len(todos_jogos)} jogos")

            # Salvar
            df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
            print(f"   CSV salvo: {nome_arquivo} (Total: {len(df_final)} jogos)")

        except Exception as e:
            print(f"   Erro ao adicionar ao CSV: {e}")
            import traceback
            traceback.print_exc()

    def _salvar_csv_consolidado(self, lista_dados, nome_arquivo='dados/loteca_historico_completo.csv'):
        try:
            todos_jogos = []

            # Consolidar todos os jogos dos novos concursos
            for dados in lista_dados:
                concurso = dados.get('concurso')
                data_sorteio = dados.get('data_sorteio')
                data_extracao = dados.get('data_extracao')

                for jogo in dados.get('jogos', []):
                    jogo_completo = jogo.copy()
                    jogo_completo['concurso'] = concurso
                    jogo_completo['data_sorteio'] = data_sorteio
                    jogo_completo['data_extracao'] = data_extracao
                    todos_jogos.append(jogo_completo)

            # Criar DataFrame com novos dados
            df_novos = pd.DataFrame(todos_jogos)

            # Reordenar colunas
            colunas_ordem = ['concurso', 'data_sorteio', 'data_extracao', 'numero',
                           'time1', 'gols_time1', 'time2', 'gols_time2', 'resultado']
            colunas_existentes = [col for col in colunas_ordem if col in df_novos.columns]
            df_novos = df_novos[colunas_existentes]

            # Verificar se o arquivo já existe
            if os.path.exists(nome_arquivo):
                # Ler arquivo existente
                df_existente = pd.read_csv(nome_arquivo, sep=';', encoding='utf-8-sig')

                # Concatenar dados antigos + novos
                df_final = pd.concat([df_existente, df_novos], ignore_index=True)

                print(f"   Adicionando {len(todos_jogos)} novos jogos ao CSV existente")
            else:
                df_final = df_novos
                print(f"   Criando novo CSV com {len(todos_jogos)} jogos")

            # Salvar
            df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
            print(f"   CSV salvo: {nome_arquivo} (Total: {len(df_final)} jogos)")

        except Exception as e:
            print(f"   Erro ao adicionar ao CSV: {e}")
            import traceback
            traceback.print_exc()
        try:
            todos_jogos = []

            # Consolidar todos os jogos
            for dados in lista_dados:
                concurso = dados.get('concurso')
                data_sorteio = dados.get('data_sorteio')
                data_extracao = dados.get('data_extracao')

                for jogo in dados.get('jogos', []):
                    jogo_completo = jogo.copy()
                    jogo_completo['concurso'] = concurso
                    jogo_completo['data_sorteio'] = data_sorteio
                    jogo_completo['data_extracao'] = data_extracao
                    todos_jogos.append(jogo_completo)

            # Criar DataFrame
            df = pd.DataFrame(todos_jogos)

            # Reordenar colunas
            colunas_ordem = ['concurso', 'data_sorteio', 'data_extracao', 'numero',
                           'time1', 'gols_time1', 'time2', 'gols_time2', 'resultado']
            colunas_existentes = [col for col in colunas_ordem if col in df.columns]
            df = df[colunas_existentes]

            # Salvar
            df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
            print(f"   CSV consolidado salvo: {nome_arquivo} ({len(todos_jogos)} jogos)")

        except Exception as e:
            print(f"   Erro ao salvar CSV consolidado: {e}")

    def obter_resumo(self, dados=None, total_concursos=None):
        if isinstance(dados, list):
            # Se for uma lista de concursos
            return {
                'total_concursos': len(dados),
                'concurso_mais_recente': dados[0].get('concurso') if dados else None,
                'concurso_mais_antigo': dados[-1].get('concurso') if dados else None,
                'total_jogos': sum(len(d.get('jogos', [])) for d in dados)
            }
        else:
            # Se for um único concurso
            dados = dados or self.dados

            if not dados:
                return None

            resumo = {
                'concurso': dados.get('concurso'),
                'data_sorteio': dados.get('data_sorteio'),
                'data_extracao': dados.get('data_extracao'),
                'total_jogos': len(dados.get('jogos', []))
            }

            if total_concursos:
                resumo['total_concursos'] = total_concursos

            return resumo

    def exibir_resumo(self, dados=None, total_concursos=None):
        resumo = self.obter_resumo(dados, total_concursos)

        if not resumo:
            print("️  Nenhum dado disponível para exibir")
            return

        print("\n" + "=" * 60)
        print("   RESUMO DOS DADOS EXTRAÍDOS")
        print("=" * 60)

        if 'total_concursos' in resumo and resumo['total_concursos'] > 1:
            # Resumo de múltiplos concursos
            print(f"Total de Concursos:   {resumo['total_concursos']}")
            print(f"Concurso Mais Recente: {resumo['concurso_mais_recente']}")
            print(f"Concurso Mais Antigo:  {resumo['concurso_mais_antigo']}")
            print(f"Total de Jogos:        {resumo['total_jogos']}")
        else:
            # Resumo de um único concurso
            print(f"Concurso:         {resumo['concurso']}")
            print(f"Data do Sorteio:  {resumo['data_sorteio']}")
            print(f"Data da Extração: {resumo['data_extracao']}")
            print(f"Total de Jogos:   {resumo['total_jogos']}")
            if 'total_concursos' in resumo:
                print(f"Total de Concursos: {resumo['total_concursos']}")

        print("=" * 60)