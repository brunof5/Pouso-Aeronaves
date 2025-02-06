import sys

# Função para ler e interpretar a solução do Gurobi
def ler_solucao(nome_arquivo_sol):
    with open(nome_arquivo_sol, "r") as f:
        linhas = f.readlines()

    objVal = float(linhas[0].split('=')[1].strip())

    pousos = {}
    for linha in linhas:
        partes = linha.split()
        if partes[0].startswith("t["):  # Obtém as variáveis de tempo de pouso
            idx = int(partes[0][2:-1])  # Extrai índice do avião
            tempo = float(partes[1])
            pousos[idx] = tempo

    print(f"Valor da Função Objetivo: {objVal:.0f}")
    sequencia_pouso = sorted(pousos.items(), key=lambda x: x[1])
    print("Sequência e tempos de pouso:")
    for idx, tempo in sequencia_pouso:
        print(f"Avião {idx+1}: {tempo:.0f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python gerar_modelo.py <nome_arquivo_entrada>")
        sys.exit(1)

    nome_arquivo_entrada = sys.argv[1]

    ler_solucao(nome_arquivo_entrada)
