import sys
import numpy as np
from gurobipy import Model, GRB, quicksum

def ler_instancia(nomeArquivo):
    with open(nomeArquivo, 'r') as file:
        linhas = file.readlines()

    n = int(linhas[0].split()[0])   # Quantidade de aviões
    avioes = []
    matriz_separacao = np.zeros((n, n))

    idx_linha = 1
    for i in range(n):
        # Preenchendo os parâmetros
        dados = list(map(float, linhas[idx_linha].split()))
        avioes.append({
        'R': dados[0], 'E': dados[1], 'T': dados[2], 'L': dados[3], 'g': dados[4], 'h': dados[5]
        })
        idx_linha += 1

        # Preenchendo a matriz de separação
        linha_atual = []
        while len(linha_atual) < n:
            linha_atual.extend(map(float, linhas[idx_linha].split()))
            idx_linha += 1
        matriz_separacao[i] = linha_atual[:n]

    return n, avioes, matriz_separacao

def criar_modelo_lp(nome_arquivo_entrada, nome_arquivo_lp):
    # Leitura do arquivo
    n, avioes, s = ler_instancia(nome_arquivo_entrada)

    # Criando o modelo
    modelo = Model("aeroporto")

    # Variáveis de decisão
    t = modelo.addVars(n, vtype=GRB.INTEGER, lb=0, name="t")
    a = modelo.addVars(n, vtype=GRB.INTEGER, lb=0, name="a")
    d = modelo.addVars(n, vtype=GRB.INTEGER, lb=0, name="d")
    x = modelo.addVars(n, n, vtype=GRB.BINARY, name="x")

    # Função objetivo
    modelo.setObjective(
        quicksum(avioes[i]['g'] * a[i] + avioes[i]['h'] * d[i] for i in range(n)), 
        GRB.MINIMIZE
    )

    for i in range(n):
    # Restrição 1
        modelo.addConstr(t[i] >= avioes[i]['E'])
        modelo.addConstr(t[i] <= avioes[i]['L'])
        # Restrição 2
        modelo.addConstr(a[i] >= avioes[i]['T'] - t[i])
        modelo.addConstr(d[i] >= t[i] - avioes[i]['T'])

    for i in range(n):
        for j in range(n):
            if i != j:
                # Restrição 3
                modelo.addConstr(t[j] >= t[i] + s[i][j] - 10000 * (1 - x[i, j]))
                # Restrição 4
                modelo.addConstr(x[i, j] + x[j, i] == 1)

    # Salvando o modelo no formato LP
    modelo.write(nome_arquivo_lp)
    print(f"Modelo salvo em {nome_arquivo_lp}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python gerar_modelo.py <nome_arquivo_saida> <nome_arquivo_entrada>")
        sys.exit(1)

    nome_arquivo_lp = sys.argv[1]
    nome_arquivo_entrada = sys.argv[2]

    criar_modelo_lp(nome_arquivo_entrada, nome_arquivo_lp)
