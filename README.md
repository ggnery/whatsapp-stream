# Pipeline Completo: Instagram Reels → Documentos para RAG

Este projeto automatiza todo o fluxo de trabalho desde a coleta de Reels do Instagram até a publicação no YouTube, para no final obtermos PDFs completos, com o máximo de informação do vídeo para utilizar no RAG.

## 🎯 Visão Geral

O pipeline realiza as seguintes etapas de forma automatizada:

1. **Coleta de Links** - Scraping dos Reels de um perfil do Instagram
2. **Download de Vídeos** - Download automático dos Reels coletados
3. **Extração de Áudio** - Conversão de vídeos para formato de áudio
4. **Transcrição Inteligente** - Transcrição com identificação de falantes (AssemblyAI)
5. **Resumo por IA** - Geração de resumos e pontos-chave (Google Gemini)
6. **Upload para YouTube** - Publicação automática dos vídeos
7. **Análise de Vídeo** - Resumo do vídeo publicado com timestamps (Gemini)
8. **Geração de PDFs** - Documentação completa em PDF

## 🚀 Funcionalidades Principais

### Processamento Inteligente
- ✅ **Sistema de Registro (CSV)**: Mantém controle de todos os vídeos processados
- ✅ **Idempotência**: Execuções múltiplas não causam duplicatas
- ✅ **Nomeação Única**: Múltiplos vídeos na mesma data recebem numeração automática
- ✅ **Processamento Otimizado**: Pula arquivos já processados

### Integração com APIs
- 🎙️ **AssemblyAI**: Transcrição com diarização (identificação de falantes)
- 🤖 **Google Gemini**: Resumos contextuais e análise de vídeo
- 📺 **YouTube Data API v3**: Upload automático com espera dinâmica de processamento

### Geração de Conteúdo
- 📝 Transcrições em Markdown com timestamps
- 📊 Resumos detalhados e pontos principais
- 🎬 Análise do vídeo no YouTube com timestamps
- 📄 PDFs com todo o conteúdo do vídeo

## 📁 Estrutura do Projeto

```
reels-pipeline/
├── info-reels/
│   └── registry.csv              # Registro de todos os vídeos processados
├── videos/                        # Vídeos baixados (.mp4)
├── audios/                        # Áudios extraídos (.m4a/.mp3)
├── transcriptions/                # Transcrições em Markdown (.md)
├── transcriptions-pdf/            # Documentação em PDF (.pdf)
│
├── main.py                        # Orquestrador principal do pipeline
├── scraper-reels.py              # Coleta links dos Reels
├── download-reels.py             # Download dos vídeos
├── video-to-audio.py             # Conversão vídeo → áudio
├── doc-generator.py              # Transcrição + resumo inicial
├── youtube_workflow.py           # Upload para YouTube
├── youtube_uploader.py           # Funções de upload e autenticação
├── gemini_summary.py             # Análise do vídeo no YouTube
├── resumo_video.py               # Interface com API Gemini
├── pdf_generator.py              # Geração de PDFs
├── csv_manager.py                # Gerenciamento do registro
│
├── client.json                   # Credenciais OAuth YouTube (você cria)
├── token.json                    # Token de autenticação (gerado automaticamente)
├── .env                          # Chaves de API (você cria)
├── requirements.txt              # Dependências Python
└── webdriver-download-test.ipynb # Auxiliar para configurar ChromeDriver
```

## 🔧 Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/reels-pipeline.git
cd reels-pipeline
```

### 2. Crie o Ambiente Virtual

É altamente recomendado usar um ambiente virtual (conda ou venv).

**Com Conda:**
```bash
conda create --name metaglass-env python=3.10
conda activate metaglass-env
pip install -r requirements.txt
```

**Com venv:**
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure as APIs

#### 3.1. API do YouTube (Google Cloud)

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou use um existente
3. Ative a **"YouTube Data API v3"** em "APIs e Serviços" → "Biblioteca"
4. Vá para "Credenciais" → "Criar Credenciais" → "ID do cliente OAuth"
5. Configure a "Tela de permissão OAuth":
   - Tipo: **Externo**
   - Adicione seu e-mail em "Usuários de teste"
6. Crie as credenciais do tipo **"Computador" (Desktop App)**
7. Baixe o JSON e renomeie para **`client.json`**
8. Coloque o arquivo na raiz do projeto

#### 3.2. API do Gemini (Google AI Studio)

1. Acesse o [Google AI Studio](https://aistudio.google.com/)
2. Clique em "Get API key"
3. Crie uma nova chave de API
4. Guarde a chave para o próximo passo

#### 3.3. API do AssemblyAI

1. Acesse o [AssemblyAI](https://www.assemblyai.com/)
2. Crie uma conta e obtenha sua API Key
3. Guarde a chave para o próximo passo

#### 3.4. Crie o arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` com o seguinte conteúdo:

```env
ASSEMBLYAI_API_KEY="sua_chave_assemblyai_aqui"
GEMINI_API_KEY="sua_chave_gemini_aqui"
```

### 4. Configure o ChromeDriver

O Selenium precisa do ChromeDriver para automatizar o Instagram.

1. Abra e execute o notebook `webdriver-download-test.ipynb`
2. Ele baixará automaticamente o ChromeDriver e exibirá o caminho
3. Copie o caminho exibido
4. Abra `scraper-reels.py` e cole o caminho em:

```python
CHROMEDRIVER_PATH = r"COLE_O_CAMINHO_AQUI"
```

### 5. Configure o Instagram

Abra `scraper-reels.py` e configure:

```python
USERNAME = "seu_usuario_instagram"
PASSWORD = "sua_senha_instagram"
TARGET_PROFILE = "perfil_alvo_sem_@"
```

⚠️ **Recomendação**: Use uma conta secundária do Instagram para evitar problemas.

## ▶️ Como Executar

Após concluir toda a configuração:

```bash
python main.py
```

### Primeira Execução

Na primeira execução, você precisará autorizar o aplicativo no YouTube:

1. Seu navegador será aberto automaticamente
2. Faça login com a conta Google configurada como "Usuário de teste"
3. Autorize as permissões:
   - "Fazer upload de vídeos para sua conta do YouTube"
   - "Ver seus vídeos do YouTube"
4. Feche o navegador após autorizar
5. O arquivo `token.json` será criado automaticamente

### O que Esperar

O terminal mostrará o progresso de cada etapa:

```
Iniciando o pipeline de processamento de reels

>>> scraper-reels.py
✅ Sucesso: execução finalizada.
📦 Total de links coletados da página: 5

>>> download-reels.py
✅ Sucesso: execução finalizada.
Concluído: 5 baixados, 0 falharam, 0 pulados.

>>> video-to-audio.py
✅ Sucesso: execução finalizada.
Concluído: 5 convertidos, 0 falhas, 0 pulados.

>>> doc-generator.py
✅ Sucesso: execução finalizada.
Concluído. 5 novos áudios processados, 0 pulados.

>>> youtube_workflow.py
✅ Sucesso: execução finalizada.
[YouTubeWorkflow] Processamento concluído!
   Sucesso: 5
   Falhas: 0

>>> gemini_summary.py
✅ Sucesso: execução finalizada.
[GeminiSummary] Processamento concluído!
   Sucesso: 5
   Falhas: 0

>>> pdf_generator.py
✅ Sucesso: execução finalizada.
[PDFGenerator] Processamento concluído!
   PDFs gerados: 5

Pipeline concluído com sucesso!
```

## 📊 Sistema de Registro (CSV)

O arquivo `info-reels/registry.csv` mantém o controle de todo o pipeline:

| Coluna | Descrição |
|--------|-----------|
| `insta_link` | URL original do Reel no Instagram |
| `insta_shortcode` | Identificador único do Instagram |
| `filename` | Nome do arquivo de vídeo (ex: `18-11-2025.mp4`) |
| `download_status` | `discovered` ou `downloaded` |
| `youtube_id` | ID do vídeo no YouTube |
| `youtube_status` | `processing`, `uploaded` ou `failed` |

### Estados do Vídeo

1. **discovered**: Link coletado, aguardando download
2. **downloaded**: Vídeo baixado com sucesso
3. **processing**: Upload para YouTube em andamento
4. **uploaded**: Vídeo publicado e processado no YouTube

## 🔄 Fluxo Detalhado do Pipeline

### 1. scraper-reels.py
- Faz login no Instagram usando Selenium
- Navega até o perfil alvo
- Coleta todos os links de Reels
- Registra no CSV com status `discovered`

### 2. download-reels.py
- Lê links com status `discovered` do CSV
- Baixa vídeos usando Instaloader
- Renomeia para formato `dd-mm-yyyy.mp4` (ou `-2`, `-3` se houver múltiplos)
- Atualiza CSV para status `downloaded`
- **Evita duplicatas**: Verifica nomes já usados na execução

### 3. video-to-audio.py
- Localiza vídeos `.mp4` que não têm áudio correspondente
- Extrai áudio usando FFmpeg
- Tenta formato `.m4a` (stream copy, sem re-encode)
- Fallback para `.mp3` se necessário

### 4. doc-generator.py
- Processa áudios que não têm `.md` correspondente
- Envia para **AssemblyAI** para transcrição com diarização
- Envia transcrição para **Gemini** para resumo e pontos-chave
- Gera arquivo `.md` com:
  - Transcrição com timestamps e falantes
  - Resumo detalhado
  - Pontos principais

### 5. youtube_workflow.py
- Busca vídeos com status `downloaded` sem `youtube_status='uploaded'`
- Autentica via OAuth 2.0 (usa ou cria `token.json`)
- Faz upload de cada vídeo
- **Espera dinâmica**: Monitora API do YouTube até processamento concluir
- Atualiza CSV com `youtube_id` e status `uploaded`
- **Evita duplicatas**: Verifica arquivos já enviados na execução

### 6. gemini_summary.py
- Busca vídeos com `youtube_status='uploaded'`
- Verifica se `.md` já tem seção "Resumo do Vídeo (YouTube - Gemini)"
- Envia URL do YouTube para **Gemini** analisar o vídeo
- Recebe resumo com timestamps dos tópicos
- Adiciona seção ao final do `.md`

### 7. pdf_generator.py
- Localiza arquivos `.md` que não têm `.pdf` correspondente
- Converte Markdown para PDF usando ReportLab
- Processa formatação:
  - Títulos (`# Título`)
  - Subtítulos (`## Subtítulo`)
  - Listas (`- item`)
  - Negrito (`**texto**`)
- Salva em `transcriptions-pdf/`

## 🔄 Execuções Subsequentes

O pipeline é inteligente e idempotente:

- **Scraping**: Só adiciona links novos ao CSV
- **Download**: Pula vídeos já baixados
- **Conversão**: Pula áudios já existentes
- **Transcrição**: Pula `.md` já existentes
- **YouTube**: Pula vídeos já enviados
- **Gemini**: Pula resumos já adicionados
- **PDF**: Pula PDFs já gerados

Você pode executar `python main.py` quantas vezes quiser!

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---