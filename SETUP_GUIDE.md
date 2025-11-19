# Guia de Configuração - Smart Glasses WhatsApp + RAG

## ✅ Pré-requisito Concluído
- [x] Ambiente Conda ativado (`smartglasses-env`)

---

## 📋 Próximos Passos

### Passo 1: Configurar a Chave da API OpenAI

1. **Obtenha sua chave OpenAI**:
   - Acesse: https://platform.openai.com/api-keys
   - Faça login e crie uma nova chave API
   - Copie a chave (começa com `sk-proj-...` ou `sk-...`)

2. **Crie o arquivo `.env`** na pasta `whatsapp-stream/`:
   ```bash
   # No terminal, dentro da pasta whatsapp-stream/
   echo OPENAI_API_KEY=sua_chave_aqui > .env
   ```

   Ou crie manualmente o arquivo `.env` com o conteúdo:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Verifique se está configurado**:
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ API Key configurada!' if os.getenv('OPENAI_API_KEY') else '✗ API Key NÃO encontrada!')"
   ```

---

### Passo 2: Verificar Estrutura de Arquivos

Certifique-se de que a estrutura está assim:

```
whatsapp-stream/
├── documents/
│   └── Xadrez.pdf          ✅ (deve existir)
├── indexes/                 ✅ (será criado automaticamente se não existir)
│   └── faiss_Xadrez/       ✅ (será criado automaticamente na 1ª execução)
├── logs/                    ✅ (criado automaticamente)
├── main.py                  ✅
├── rag_module.py           ✅
├── logger.py               ✅
├── audio.py                ✅
└── .env                    ⚠️ (VOCÊ PRECISA CRIAR - Passo 1)
```

**Verificar se o PDF existe**:
```bash
# No terminal, dentro de whatsapp-stream/
ls documents/Xadrez.pdf
```

---

### Passo 3: Configurar Cabos de Áudio Virtual (VB-Audio)

⚠️ **IMPORTANTE**: Este sistema precisa de cabos de áudio virtuais para funcionar.

1. **Instale o VB-Audio Virtual Cable**:
   - Download: https://vb-audio.com/Cable/
   - Instale CABLE-A e CABLE-B

2. **Configure o WhatsApp Desktop**:
   - Abra WhatsApp Desktop
   - Vá em Configurações → Áudio
   - Defina o dispositivo de saída como **CABLE-A Input**

3. **Verifique os dispositivos disponíveis**:
   ```bash
   python -c "import sounddevice as sd; print(sd.query_devices())"
   ```

4. **Ajuste os nomes dos dispositivos no `main.py`** (se necessário):
   - Abra `main.py`
   - Linhas 15-16, ajuste para os nomes exatos dos seus dispositivos:
   ```python
   INPUT_DEVICE = "CABLE-A Output (VB-Audio Virtua, MME"
   OUTPUT_DEVICE = 'CABLE-B Input (VB-Audio Virtual, MME'
   ```

---

### Passo 4: Executar o Sistema

1. **Navegue até a pasta whatsapp-stream**:
   ```bash
   cd whatsapp-stream
   ```

2. **Execute o programa**:
   ```bash
   python main.py
   ```

3. **O que vai acontecer**:
   ```
   ======================================================================
   SMART GLASSES - Sistema Integrado WhatsApp + RAG
   ======================================================================

   [1/3] Inicializando pipeline TTS...
   ✓ Pipeline TTS pronto

   [2/3] Inicializando sistema RAG...
   Carregando índice Xadrez...
   ✓ Sistema RAG pronto (documento: Xadrez.pdf)

   [3/3] Inicializando captura de áudio...
   Input device info: ...
   Output device info: ...
   ✓ Captura de áudio pronta

   ======================================================================
   Sistema pronto! Aguardando captura de voz...
   ======================================================================

   Record streaming started (press Ctrl+C to stop)
   Say 'banana' to start/stop query capture
   ```

---

### Passo 5: Como Usar

1. **Inicie uma chamada no WhatsApp Desktop**

2. **Diga a palavra-chave**: "**banana**"
   - O sistema começará a gravar sua pergunta

3. **Faça sua pergunta sobre xadrez**:
   - Exemplo: "Como o cavalo se move no xadrez?"
   - Exemplo: "Quais são as regras básicas do xadrez?"

4. **Diga "banana" novamente** para finalizar a captura

5. **O sistema vai**:
   - ✅ Processar sua pergunta no RAG
   - ✅ Buscar informações no documento Xadrez.pdf
   - ✅ Gerar resposta em texto
   - ✅ Converter para áudio (TTS)
   - ✅ Reproduzir a resposta na chamada
   - ✅ Salvar pergunta + resposta no log

6. **Verifique o log**:
   ```bash
   cat logs/conversation_log.txt
   ```

---

## 🔧 Troubleshooting

### Erro: "API Key não encontrada"
- Verifique se o arquivo `.env` existe em `whatsapp-stream/`
- Verifique se a chave está no formato correto: `OPENAI_API_KEY=sk-...`

### Erro: "Device not found"
- Execute: `python -c "import sounddevice as sd; print(sd.query_devices())"`
- Copie os nomes EXATOS dos dispositivos
- Atualize `INPUT_DEVICE` e `OUTPUT_DEVICE` no `main.py`

### Erro: "PDF não encontrado"
- Verifique se `documents/Xadrez.pdf` existe
- Caminho completo: `whatsapp-stream/documents/Xadrez.pdf`

### Erro: "Índice não encontrado"
- **Não se preocupe!** O sistema cria automaticamente na primeira execução
- Pode demorar alguns minutos na primeira vez (processando PDF)

### Nenhuma transcrição aparece
- Verifique se o WhatsApp está configurado para usar CABLE-A
- Verifique se há áudio chegando no cabo virtual
- Teste com volume mais alto

### TTS não reproduz
- Verifique se CABLE-B está configurado corretamente
- Verifique se o WhatsApp está recebendo áudio de CABLE-B

---

## 📊 Monitoramento

### Logs de Conversação
Todas as conversas são salvas em:
```
whatsapp-stream/logs/conversation_log.txt
```

Formato:
```
[2025-11-07 14:30:45] PERGUNTA: Como o cavalo se move? | RESPOSTA: O cavalo se move em formato de L...
```

### Logs com Erro
Erros são marcados:
```
[2025-11-07 14:35:12] [ERRO] PERGUNTA: ... | RESPOSTA: Desculpe, não consegui processar...
```

---

## 🎯 Comandos Úteis

    - conda env create -f .\environment.yml
    - conda activate smartglasses-env
    - python -c "import sounddevice as sd; print(sd.query_devices())"
    - cd whatsapp-stream
    - python main.py

```bash
# Ativar ambiente Conda
conda activate smartglasses-env

# Executar o sistema
cd whatsapp-stream
python main.py

# Ver logs
cat logs/conversation_log.txt

# Limpar logs
rm logs/conversation_log.txt

# Recriar índice (se necessário)
rm -rf indexes/faiss_Xadrez/
python main.py  # Vai recriar automaticamente

# Listar dispositivos de áudio
python -c "import sounddevice as sd; print(sd.query_devices())"

# Testar se API Key está configurada
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

---

## ✅ Checklist Final

Antes de executar, verifique:

- [ ] Ambiente Conda ativado (`smartglasses-env`)
- [ ] Arquivo `.env` criado com `OPENAI_API_KEY`
- [ ] PDF `Xadrez.pdf` existe em `documents/`
- [ ] VB-Audio Virtual Cable instalado
- [ ] WhatsApp Desktop configurado para usar CABLE-A
- [ ] Nomes dos dispositivos corretos no `main.py`

---

## 🚀 Pronto para Usar!

Se todos os passos acima estiverem OK, execute:

```bash
cd whatsapp-stream
python main.py
```

E comece a fazer perguntas sobre xadrez via voz! 🎤♟️


