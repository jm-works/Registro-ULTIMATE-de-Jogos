# 🕹️ Registro ULTIMATE de Jogos - Seu Diário de Games
> **Criado por jm-works (JMRS)**

![Badge Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 📜 Sobre o Projeto
Este programa tem como propósito catalogar jogos finalizados, inspirado na planilha de jogos do canal [Cogumelando Videogame](https://www.youtube.com/watch?v=uGLnQw6umhI). Ele oferece estatísticas básicas e detalha de forma clara todas as suas jogatinas, permitindo um acompanhamento organizado do seu progresso nos games.

**Destaques:**
- Cadastro completo de jogos, incluindo gênero, plataforma, tempo jogado e nota.
- Organização simples, com filtros para encontrar rapidamente qualquer jogo.
- Estatísticas e gráficos para visualizar seu desempenho ao longo do tempo.
- Exportação e importação de dados para Excel e PDF.
- Checklist de tarefas para acompanhar desafios dentro dos jogos.

---

## 🛠 Instalação
### Requisitos
Para rodar o software, é necessário ter **Python 3.13+** instalado.

> **Nota para usuários Linux:** Certifique-se de ter o `tkinter` instalado. Em sistemas Debian/Ubuntu, use: `sudo apt-get install python3-tk`.

### Instalando Dependências
Recomendamos o uso de um ambiente virtual para manter seu sistema organizado.

1. **Clone o repositório:**
   git clone https://github.com/jm-works/Registro-ULTIMATE-de-Jogos.git

2. **Acesse o diretório do projeto:**
   cd Registro-ULTIMATE-de-Jogos

3. **Crie e ative o ambiente virtual (Opcional, mas recomendado):**
   - **Windows:**
     python -m venv .venv
     .venv\Scripts\activate
   - **Linux/Mac:**
     python3 -m venv .venv
     source .venv/bin/activate

4. **Instale as bibliotecas:**
   
   **Opção A (Padrão com pip):**
   ```sh
   pip install pandas numpy openpyxl reportlab matplotlib pyperclip Pillow
   ```
   
   **Opção B (Se você usa uv):**
   Como o projeto já possui um arquivo `uv.lock`, você pode instalar tudo rapidamente com:
   ```sh
   uv sync
   ```

### Como Executar
Com as dependências instaladas, inicie o programa:
python main.py

---

## 🎨 Interface e Funcionalidades
O programa possui uma interface intuitiva, inspirada em menus clássicos de computadores antigos.

**Menu Principal:** (localizado no topo da tela)
- **Arquivo**: Salvar, carregar listas e exportar/importar dados, alterar plano de fundo.
- **Editar**: Alterar ou excluir jogos cadastrados.
- **Filtro**: Aplicar filtros personalizados à lista de jogos.
- **Informações**: Acessar estatísticas detalhadas.
- **Minhas Tarefas**: Gerenciar a checklist de missões.
- **Resumo da sua Jornada**: Exibir um relatório completo da sua coleção.

**Seções Principais:**
- **Lista de Jogos**: Exibe todos os títulos cadastrados.
- **Formulário de Cadastro**: Permite adicionar ou editar jogos.
- **Estatísticas**: Geração de gráficos e análises personalizadas.
- **Checklist**: Organização de missões e tarefas relacionadas aos jogos.

**Dicas de Navegação:**
- **Clique com o botão direito** sobre um jogo para abrir um menu rápido:
  - Pesquisar no Google
  - Copiar nome do jogo
  - Organizar Lista
  - Filtrar/Limpar Filtros
  - Editar Jogo
  - Excluir Jogo


## 🏆 Como Usar

### Brinque um pouco
- A lista já vem pré-configurada com alguns jogos, aproveite para testar as funções até se sentir satisfeito em criar a sua própria lista.

### Dê um reset na lista
1. Na aba superior, clique em **"Arquivo"** e selecione **"Resetar todas as listas"**.

### Adicionando um Jogo
1. Preencha os campos obrigatórios: **Título, Gênero, Plataforma e Estado**.
2. Se o jogo foi finalizado, informe **Data de Zeramento, Tempo Jogado e Nota**.
3. Clique em **"Adicionar Jogo"**.

### Editando e Excluindo Jogos
- Para editar um jogo, use o menu rápido com o botão direito em cima do jogo e clique em **"Editar"**.
- Para excluir, use o menu rápido com o botão direito em cima do jogo e clique em **"Excluir"**.

### Exportação e Importação de Dados
- Use a aba superior **"Arquivo"** e clique em **Exportar** para PDF, Excel ou JSON.
- Use a aba superior **"Arquivo"** e clique em **Importar** para Excel ou JSON.

### Filtrando e Limpando Filtros

- Para filtrar, use o menu rápido com o botão direito em cima da lista e clique em **"Filtrar"**.
- Para limpar filtro, use o menu rápido com o botão direito em cima da lista e clique em **"Limpar Filtros"**.
- **Observação:** Se nenhum jogo estiver aparecendo na lista, use as abas superiores para limpar o filtro.

### Estatísticas e Relatórios
- No menu **"Informações"**, veja gráficos detalhados sobre todas suas estatísticas.

### Checklist de Missões
- No menu **"Minhas Tarefas"**, acompanhe as missões que você poderá criar.

### Resumo da sua Jornada
- No menu **"Resumo da sua Jornada"**, veja um relatório detalhado e resumido, com todos os seus jogos registrados.

## 🚀 Contribuindo
Gostaria de ajudar no desenvolvimento do projeto? Se sim, siga estes passos:
1. Faça um Fork do repositório.
2. Crie uma branch: `git checkout -b minha-ideia`.
3. Faça um commit: `git commit -m 'Minha nova ideia'`.
4. Envie um Pull Request.
