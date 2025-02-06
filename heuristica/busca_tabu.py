import sys
import time
import numpy as np

def ler_instancia(nomeArquivo):
    with open(nomeArquivo, 'r') as file:
        linhas = file.readlines()

    n = int(linhas[0].split()[0])  # Quantidade de aviões
    avioes = []
    matriz_separacao = np.zeros((n, n))

    idx_linha = 1
    for i in range(n):
        # Preenchendo os parâmetros
        dados = list(map(float, linhas[idx_linha].split()))
        avioes.append({
            'id': i,
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

def calcular_objValue(n, avioes, tempos):
    objValue = sum(avioes[i]['g'] * max(0, avioes[i]['T'] - tempos[i]) + avioes[i]['h'] * max(0, tempos[i] - avioes[i]['T']) for i in range(n))
    return objValue

def calcular_tempos_pouso(n, avioes, s, ordem):
    tempos_pouso_atraso = [0] * n
    tempos_pouso_adiantado = [0] * n

    # Construção da primeira solução inicial (atrasos)
    tempos_pouso_atraso[ordem[0]] = avioes[ordem[0]]['T']
    for i in range(1, n):
        prev, atual = ordem[i-1], ordem[i]
        tempos_pouso_atraso[atual] = max(avioes[atual]['T'], tempos_pouso_atraso[prev] + s[prev][atual])
        if not (avioes[atual]['E'] <= tempos_pouso_atraso[atual] <= avioes[atual]['L']):
            tempos_pouso_atraso = None
            break

    # Construção da segunda solução inicial (adiantamentos)
    tempos_pouso_adiantado[ordem[-1]] = avioes[ordem[-1]]['T']
    for i in range(n-2, -1, -1):
        prox, atual = ordem[i+1], ordem[i]
        tempos_pouso_adiantado[atual] = min(avioes[atual]['T'], tempos_pouso_adiantado[prox] - s[atual][prox])
        if not (avioes[atual]['E'] <= tempos_pouso_adiantado[atual] <= avioes[atual]['L']):
            tempos_pouso_adiantado = None
            break

    # Determinação de qual solução será retornada
    if tempos_pouso_atraso is None and tempos_pouso_adiantado is None:
        return None
    
    if tempos_pouso_atraso is not None and tempos_pouso_adiantado is None:
        return tempos_pouso_atraso
    
    if tempos_pouso_atraso is None and tempos_pouso_adiantado is not None:
        return tempos_pouso_adiantado
    
    objValue_atraso = calcular_objValue(n, avioes, tempos_pouso_atraso)
    objValue_adiantado = calcular_objValue(n, avioes, tempos_pouso_adiantado)
    return tempos_pouso_atraso if objValue_atraso < objValue_adiantado else tempos_pouso_adiantado

# Gera-se uma solução inicial baseado em uma heurística gulosa
def gerar_solucao_inicial(n, avioes, s):
    # Ordena-se os aviões em ordem crescente de tempo ideal de pouso
    ordem = sorted(range(n), key=lambda i: avioes[i]['T'])
    tempos_pouso = calcular_tempos_pouso(n, avioes, s, ordem)
    
    if tempos_pouso is None:
        print("Não foi possível encontrar uma solução inicial viável")
        sys.exit(1)

    return ordem, tempos_pouso

def gerar_vizinhos(n, avioes, s, ordem_atual, lista_tabu):
    vizinhos = []
    for i in range(n):
        for j in range(i + 1, n):
            nova_ordem = ordem_atual[:]
            nova_ordem[i], nova_ordem[j] = nova_ordem[j], nova_ordem[i]
            tempos_pouso = calcular_tempos_pouso(n, avioes, s, nova_ordem)

            if tempos_pouso is not None and (nova_ordem, tempos_pouso) not in lista_tabu:
                vizinhos.append((nova_ordem, tempos_pouso))

    return vizinhos

def verificar_sequencia_crescente(tempos, idx_atual, ordem, s):
    n = len(ordem)
    atual = ordem[idx_atual]
    
    indices_verificar = []
    
    if idx_atual > 1:
        indices_verificar.append(ordem[idx_atual - 2])
    if idx_atual > 0:
        indices_verificar.append(ordem[idx_atual - 1])
    
    indices_verificar.append(atual)
    
    if idx_atual < n - 1:
        indices_verificar.append(ordem[idx_atual + 1])
    if idx_atual < n - 2:
        indices_verificar.append(ordem[idx_atual + 2])
    
    # Verifica se a sequência é crescente e respeita a matriz de separação
    for j in range(len(indices_verificar) - 1):
        aviao1 = indices_verificar[j]
        aviao2 = indices_verificar[j + 1]
        
        if tempos[aviao1] > tempos[aviao2]:
            return False
        
        if tempos[aviao2] < tempos[aviao1] + s[aviao1][aviao2]:
            return False
    
    return True

def aplicar_intensificacao(n, avioes, s, ordem, tempos_pouso):
    memoria_intensificacao = []

    for i in range(n):
        novo_tempos_base = tempos_pouso[:]
        atual = ordem[i]
        novo_tempos_base[atual] = avioes[atual]['T']  # Força o tempo ideal para o avião i (respeitando a ordem)
        
        if i < n - 1:   # Ajusta o próximo
            novo_tempos_prox = novo_tempos_base[:]
            prox = ordem[i + 1]
            novo_tempos_prox[prox] = novo_tempos_prox[atual] + s[atual][prox]
            if (
                avioes[prox]['E'] <= novo_tempos_prox[prox] <= avioes[prox]['L'] and
                verificar_sequencia_crescente(novo_tempos_prox, i, ordem, s)
            ):
                memoria_intensificacao.append((ordem, novo_tempos_prox, calcular_objValue(n, avioes, novo_tempos_prox)))
        
        if i > 0:   # Ajusta o anterior
            novo_tempos_prev = novo_tempos_base[:]
            prev = ordem[i - 1]
            novo_tempos_prev[prev] = novo_tempos_prev[atual] - s[atual][prev]
            if (
                avioes[prev]['E'] <= novo_tempos_prev[prev] <= avioes[prev]['L'] and
                verificar_sequencia_crescente(novo_tempos_prev, i, ordem, s)
            ):
                memoria_intensificacao.append((ordem, novo_tempos_prev, calcular_objValue(n, avioes, novo_tempos_prev)))

        # Ajuste de ambos (próximo e anterior)
        if i < n - 1 and i > 0:
            novo_tempo_ambos = novo_tempos_base[:]
            prev = ordem[i - 1]
            prox = ordem[i + 1]

            novo_tempo_ambos[prox] = novo_tempo_ambos[atual] + s[atual][prox]
            novo_tempo_ambos[prev] = novo_tempo_ambos[atual] - s[atual][prev]

            if (
                avioes[prox]['E'] <= novo_tempo_ambos[prox] <= avioes[prox]['L'] and
                avioes[prev]['E'] <= novo_tempo_ambos[prev] <= avioes[prev]['L'] and
                verificar_sequencia_crescente(novo_tempo_ambos, i, ordem, s)
            ):
                memoria_intensificacao.append((ordem, novo_tempo_ambos, calcular_objValue(n, avioes, novo_tempo_ambos)))

    if memoria_intensificacao:
        memoria_intensificacao.sort(key=lambda x: x[2])  # Ordena pela melhor penalidade
        return memoria_intensificacao[0]  # Retorna melhor solução
    return None

def busca_tabu(n, avioes, s, ordem_atual, tempos_atual, objValue_atual, max_iter_sem_melhoria=20):
    # Solução global
    solucao_global = (ordem_atual, tempos_atual, objValue_atual)

    # Inicialização da Lista Tabu
    lista_tabu = []
    tabu_tenure = n // 2

    iter_sem_melhoria = 0
    while iter_sem_melhoria < max_iter_sem_melhoria:
        # Gera-se todos os vizinhos viáveis
        vizinhos = gerar_vizinhos(n, avioes, s, ordem_atual, lista_tabu)
        melhor_vizinho = None
        melhor_vizinho_objValue = float('inf')

        # Busca-se a melhor solução vizinha viável
        if vizinhos:
            melhor_vizinho = min(vizinhos, key=lambda x: calcular_objValue(n, avioes, x[1]))
            melhor_vizinho_objValue = calcular_objValue(n, avioes, melhor_vizinho[1])

        # Se a melhor solução vizinha viável melhorar a solução atual, altera-se a solução atual
        if melhor_vizinho is not None and melhor_vizinho_objValue <= objValue_atual:
            lista_tabu.append(((ordem_atual, tempos_atual), 0))
            ordem_atual, tempos_atual = melhor_vizinho
            objValue_atual = melhor_vizinho_objValue

        # Atualizando Lista Tabu e verificando tabu_tenure
        lista_tabu = [(sol, cont + 1) for sol, cont in lista_tabu if cont < tabu_tenure]

        # Aplica-se a intensificação
        intensificacao = aplicar_intensificacao(n, avioes, s, ordem_atual, tempos_atual)
        if intensificacao:
            ordem_intensificada, tempos_pouso_intensificado, objValue_intensificado = intensificacao
            if objValue_intensificado <= objValue_atual and (ordem_intensificada, tempos_pouso_intensificado) not in lista_tabu:
                ordem_atual = ordem_intensificada
                tempos_atual = tempos_pouso_intensificado
                objValue_atual = objValue_intensificado

        # Atualiza os dados da solução global
        if objValue_atual < solucao_global[2]:
            solucao_global = (ordem_atual, tempos_atual, objValue_atual)
            iter_sem_melhoria = 0
        else:
            iter_sem_melhoria += 1

    return solucao_global

def salvar_resultado(arquivo_saida, n, ordem_inicial, tempos_inicial, objValue_inicial, ordem, tempos, objValue, tempo_computacional):
    with open(arquivo_saida, 'w') as f:
        f.write("### Solucao Inicial ###\n")
        f.write("Sequencia de Pouso: " + str([i+1 for i in ordem_inicial]) + "\n")
        f.write("Tempos de Pouso:\n")
        for i in range(n):
            f.write(f"Aviao {ordem_inicial[i]+1}: {tempos_inicial[ordem_inicial[i]]:.0f}\n")
        f.write("Funcao Objetivo: " + str(objValue_inicial) + "\n\n")
        
        f.write("### Solucao Final ###\n")
        print("Sequência de Pouso:", [i+1 for i in ordem])
        f.write("Sequencia de Pouso: " + str([i+1 for i in ordem]) + "\n")
        print("Tempos de Pouso:")
        f.write("Tempos de Pouso:\n")
        for i in range(n):
            print(f"Avião {ordem[i]+1}: {tempos[ordem[i]]:.0f}")
            f.write(f"Aviao {ordem[i]+1}: {tempos[ordem[i]]:.0f}\n")
        print("Função Objetivo:", objValue)
        f.write("Funcao Objetivo: " + str(objValue) + "\n")

        f.write(f"\nTempo Computacional: {tempo_computacional:.4f} segundos\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python busca_tabu.py <arquivo_saida> <arquivo_instancia>")
        sys.exit(1)

    arquivo_saida = sys.argv[1]
    arquivo_instancia = sys.argv[2]

    # Lê a instância do problema
    n, avioes, s = ler_instancia(arquivo_instancia)

    # Inicia a contagem do tempo
    tempo_inicio = time.time()

    # Gera solução inicial
    ordem_inicial, tempos_inicial = gerar_solucao_inicial(n, avioes, s)
    objValue_inicial = calcular_objValue(n, avioes, tempos_inicial)

    # Executa a Busca Tabu
    ordem_encontrada, tempos_encontrados, objValue_encontrado = busca_tabu(n, avioes, s, ordem_inicial, tempos_inicial, objValue_inicial)

    # Calcula o tempo computacional
    tempo_fim = time.time()
    tempo_computacional = tempo_fim - tempo_inicio

    # Salva e imprime os resultados
    salvar_resultado(arquivo_saida, n, ordem_inicial, tempos_inicial, objValue_inicial, ordem_encontrada, tempos_encontrados, objValue_encontrado, tempo_computacional)
