"""
Ponto de entrada principal do Loteca Web Scraper
"""
from src.scraper import LotecaScraper
import sys


def main():
    """
    Função principal de execução
    """
    print("\n" + "" * 30)
    print("        LOTECA WEB SCRAPER")
    print("        Modo: Atualização Incremental")
    print("" * 30)

    try:
        # Criar instância do scraper
        scraper = LotecaScraper(headless=True)

        # Executar o scraping:
        # - Lê o CSV e busca o último concurso
        # - Inicia do próximo (último + 1)
        # - Extrai 50 concursos
        # - Adiciona ao CSV existente
        dados = scraper.executar(
            salvar=True,
            formatos=['csv'],
            concurso_inicial=None,  # None = busca automaticamente
            max_concursos=50
        )

        if dados:
            print(f"\nProcesso finalizado com sucesso!")
            print(f"Novos concursos adicionados: {len(dados)}")
            print(f"Arquivo: dados/loteca_historico_completo.csv\n")
            return 0
        else:
            print("\nErro: Nenhum dado foi extraído")
            return 1

    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário")
        print("Os dados coletados foram salvos\n")
        return 130

    except Exception as e:
        print(f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    codigo_saida = main()
    sys.exit(codigo_saida)