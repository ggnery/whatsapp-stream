# Pipeline de Transcrição e Resumo de Reels do Instagram

Este projeto automatiza o processo de baixar, transcrever e resumir vídeos de Reels de um perfil específico do Instagram. Ele utiliza uma sequência de scripts para orquestrar todo o fluxo de trabalho, desde a coleta dos links até a geração de um documento Markdown com a transcrição e um resumo detalhado gerado por IA.

## Funcionalidades

- **Coleta de Links:** Navega automaticamente pela página de Reels de um perfil alvo e coleta os links de todos os vídeos.
- **Download de Vídeos:** Baixa os vídeos dos Reels coletados.
- **Extração de Áudio:** Converte os arquivos de vídeo `.mp4` para formatos de áudio (`.m4a` ou `.mp3`).
- **Transcrição Inteligente:** Utiliza a API da AssemblyAI para transcrever o áudio, incluindo a identificação de diferentes falantes (diarização).
- **Resumo com IA:** Emprega a API do Google Gemini para gerar um resumo coeso e uma lista de pontos-chave a partir da transcrição.
- **Processamento Otimizado:** O pipeline foi projetado para pular arquivos que já foram processados, economizando tempo e recursos em execuções futuras.

## Como Funciona

O processo é orquestrado pelo script `main.py` e segue os seguintes passos:

1.  `scraper-reels.py`: Acessa o Instagram, faz login, navega até o perfil alvo e salva os links dos Reels em um arquivo `.txt`.
2.  `download-reels.py`: Lê o arquivo `.txt` e baixa os vídeos que ainda não existem localmente.
3.  `video-to-audio.py`: Verifica a pasta de vídeos e converte os novos arquivos para áudio.
4.  `doc-generator.py`: Examina a pasta de áudios e processa os novos arquivos, enviando-os para as APIs de transcrição e resumo, e salvando o resultado final em formato `.md`.

## Instalação e Configuração

Siga os passos abaixo para configurar e rodar o projeto.

**1. Clone o Repositório**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

**2. Crie um Ambiente Conda e Instale as Dependências**

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto. Este guia usa `conda`.

```bash
# Crie o ambiente conda 
conda create --name metaglass-env python=3.10

# Ative o ambiente
conda activate metaglass-env

# Instale as bibliotecas necessárias
pip install -r requirements.txt
```

**3. Configure o ChromeDriver**

O projeto usa o Selenium para automatizar a navegação no Instagram, o que requer o ChromeDriver.

-   **Passo 1: Encontre o Caminho do ChromeDriver**
    -   Abra e execute o notebook `webdriver-download-test.ipynb`. Ele foi configurado para usar a biblioteca `chromedriver-autoinstaller`, que irá baixar a versão correta do driver para o seu navegador Chrome e **exibirá o caminho completo** para o executável.

-   **Passo 2: Atualize o Script**
    -   Copie o caminho que foi exibido no notebook.
    -   Abra o arquivo `scraper-reels.py` e cole o caminho na variável `CHROMEDRIVER_PATH`.

    ```python
    # Em scraper-reels.py
    CHROMEDRIVER_PATH = r"COLE_O_SEU_CAMINHO_AQUI"
    ```

**4. Configure as Variáveis de Ambiente e Credenciais**

-   **Passo 1: Crie o arquivo `.env`**
    -   Crie um arquivo chamado `.env` na raiz do projeto. Ele será usado para armazenar suas chaves de API de forma segura. Adicione o seguinte conteúdo a ele:

    ```
    ASSEMBLYAI_API_KEY="SUA_CHAVE_DE_API_DO_ASSEMBLYAI"
    GEMINI_API_KEY="SUA_CHAVE_DE_API_DO_GEMINI"
    ```

-   **Passo 2: Configure o Scraper**
    -   Abra o arquivo `scraper-reels.py` e atualize as variáveis a seguir com suas credenciais do Instagram e o perfil que você deseja analisar.
    -   Já adicionei as infos da conta de login (conta criada somente para isso)

    ```python
    # Em scraper-reels.py
    USERNAME = "seu_usuario_instagram"
    PASSWORD = "sua_senha_instagram"
    TARGET_PROFILE = "perfil_alvo_sem_@"
    ```

## Como Executar

Após concluir toda a configuração, você pode iniciar o pipeline completo com um único comando:

```bash
python main.py
```

O script irá executar cada etapa em sequência, e você verá o progresso diretamente no terminal. Os arquivos gerados serão salvos nas pastas correspondentes: `link-reels/`, `videos/`, `audios/` e `transcriptions/`.
