# 🕹️ Registro ULTIMATE de Jogos - Seu Diário de Games
---

## 📜 Sobre o Projeto
Este programa tem como propósito catalogar jogos finalizados, inspirado na planilha de jogos do canal [Cogumelando Videogame](https://www.youtube.com/watch?v=uGLnQw6umhI). Ele oferece estatísticas básicas e detalha de forma clara todas as suas jogatinas, permitindo um acompanhamento organizado do seu progresso nos games.

**Destaques:**
- Cadastro completo de jogos, incluindo gênero, plataforma, tempo jogado e nota.
- Organização simples e, com filtros para encontrar rapidamente qualquer jogo.
- Estatísticas e gráficos para visualizar seu desempenho ao longo do tempo.
- Exportação e importação de dados para Excel e PDF.
- Checklist de tarefas para acompanhar desafios dentro dos jogos.

---

## 🛠 Instalação
### Requisitos
Para rodar o software, é necessário ter **Python 3.x** instalado e as seguintes bibliotecas:
```sh
pip install pandas numpy openpyxl reportlab matplotlib pyautogui screeninfo pyperclip Pillow
```

### Como Executar
1. Clone o repositório:
   ```sh
   git clone https://github.com/jm-works/Registro-de-Jogos-Zerados-.git
   ```
2. Acesse o diretório do projeto:
   ```sh
   cd Registro-de-Jogos-Zerados-
   ```
3. Execute o programa:
   ```sh
   python Registro_ULTIMATE_de_Jogos.py
   ```

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
  - Editar jogo
  - Excluir jogo
  - Exportar/Importar

---

## 🏆 Como Usar

### Adicionando um Jogo
1. Preencha os campos obrigatórios: **Título, Gênero, Plataforma e Estado**.
2. Se o jogo foi finalizado, informe **Data de Zeramento, Tempo Jogado e Nota**.
3. Clique em **"Adicionar Jogo"**.

### Editando e Excluindo Jogos
- Para editar um jogo, use o menu rápido com o botão direito e clique em **"Editar"**.
- Para excluir, use o menu rápido com o botão direito e clique em **"Excluir"**.

### Exportação e Importação de Dados
- **Exportar** para PDF ou Excel.
- **Importar** listas prontas de jogos.

### Estatísticas e Relatórios
- No menu "Estatísticas", veja gráficos detalhados sobre:
  - Jogos zerados por ano.
  - Média de notas por plataforma.
  - Distribuição do tempo jogado.

### Checklist de Missões
- No menu "Minhas Tarefas", acompanhe desafios dentro dos jogos.

### Resumo da sua Jornada
- No menu "Resumo da sua Jornada", veja um relatório detalhado com todos os seus jogos registrados.

---

## 🚀 Contribuindo
Gostaria de ajudar no desenvolvimento do projeto? Se sim, siga estes passos:
1. Faça um Fork do repositório.
2. Crie uma branch: `git checkout -b minha-ideia`.
3. Faça um commit: `git commit -m 'Minha nova ideia'`.
4. Envie um Pull Request.

