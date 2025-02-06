import sys
import re

# Função para ler o log do Gurobi e obter as informações solução inicial e tempo computacional
def extrair_informacoes(arquivo_log):
    with open(arquivo_log, "r") as f:
        linhas = f.readlines()

    solucao_inicial = None
    tempo_computacional = None

    for linha in linhas:
        if "Found heuristic solution:" in linha:
            solucao_inicial = float(linha.split()[-1])
        
        if "Solution count" in linha and solucao_inicial is None:
            solucao_inicial = float(linha.split(":")[-1].split("...")[-1].strip())

        if "Explored" in linha and "seconds" in linha:
            match = re.search(r"(\d+\.\d+) seconds", linha)
            if match:
                tempo_computacional = float(match.group(1))

    print(f"Solução Inicial (SI): {solucao_inicial:.0f}")
    print(f"Tempo Computacional: {tempo_computacional:.2f} segundos")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python imprimir_log.py <nome_arquivo_log>.txt")
        sys.exit(1)

    extrair_informacoes(sys.argv[1])
