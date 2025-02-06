# Programação Matemática - Trabalho Prático Final

![Static Badge](https://img.shields.io/badge/GCC118-UFLA-green)
![Static Badge](https://img.shields.io/badge/2024%2F2-gray)

Universidade Federal de Lavras

Instituto de Ciências Exatas e Tecnológicas

Profa. Andreza C. Beezão Moreira (DMM/UFLA)

Prof. Mayron César O. Moreira (DCC/UFLA)

## Descrição



## Diretórios

📁 A pasta `instances` apresenta as instâncias do problema proposto.

📁 A pasta `solver` apresenta os códigos utilizados no Gurobi.

📁 A pasta `heuristica` apresenta os códigos utilizados no Busca Tabu.

## Como executar

### **Pré-requisitos**

Antes de começar, você precisará ter a seguinte ferramenta instalada:

- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### **Passo 1: Clonar o Repositório**

Clone este repositório para o seu ambiente local usando o Git:

```bash
git clone https://github.com/usuario/meu_projeto.git
```

### **Passo 2: Criar o Ambiente Virtual**

Tanto dentro do diretório do `solver` quanto da `heuristica`, crie um ambiente virtual.

No **Windows**, use o seguinte comando:

```bash
python -m venv venv
```

No **Linux/Mac**, use:

```bash
python3 -m venv venv
```

### **Passo 3: Ativar o Ambiente Virtual**

- **Windows**:
  
  ```bash
  venv\Scripts\activate
  ```

- **Linux/Mac**:

  ```bash
  source venv/bin/activate
  ```

### **Passo 4: Instalar as Dependências**

Instale as dependências necessárias usando o `pip`:

```bash
pip install -r requirements.txt
```

### **Passo 5: Executar o Trabalho**

Para o caso do `solver` os arquivos são `gerar_modelo.py`, `imprimir_resultado.py` e `imprimir_log.py` (opcional). Deve-se seguir a seguinte sequência de comandos:

```bash
python gerar_modelo.py <nome_arquivo_modelo>.lp ..\instances\<nome_instancia>.dat
```

```bash
gurobi_cl LogFile=<nome_arquivo_log>.txt ResultFile=<nome_arquivo_resultado>.sol <nome_arquivo_modelo>.lp
```

```bash
python imprimir_resultado.py <nome_arquivo_resultado>.sol
```

```bash
python imprimir_log.py <nome_arquivo_log>.txt
```

---

Para o caso da `heuristica` o arquivo é `busca_tabu.py`. Deve-se executar o comando:

```bash
python busca_tabu.py <nome_arquivo_saida>.txt ..\instances\<nome_instancia>.dat
```

### **Passo 6: Desativar o Ambiente Virtual**

Quando terminar de trabalhar no trabalho, desative o ambiente virtual:

```bash
deactivate
```