# Correção de Dependências - Erro "proxies"

## 🔴 Problema Identificado

O erro `Client.__init__() got an unexpected keyword argument 'proxies'` ocorre devido a incompatibilidade entre versões do `langchain-openai` e `openai`.

## ✅ Solução

### Opção 1: Atualizar o ambiente Conda (RECOMENDADO)

1. **Desative o ambiente atual**:
   ```bash
   conda deactivate
   ```

2. **Remova o ambiente antigo**:
   ```bash
   conda env remove -n smartglasses-env
   ```

3. **Recrie com as versões corretas** (na raiz do projeto):
   ```bash
   conda env create -f environment.yml
   ```

4. **Ative o novo ambiente**:
   ```bash
   conda activate smartglasses-env
   ```

5. **Execute o sistema**:
   ```bash
   cd whatsapp-stream
   python main.py
   ```

---

### Opção 2: Atualizar apenas os pacotes problemáticos (RÁPIDO)

Se não quiser recriar o ambiente, atualize apenas os pacotes:

```bash
conda activate smartglasses-env
pip install --upgrade langchain==0.3.7 langchain-community==0.3.7 langchain-core==0.3.15 langchain-openai==0.2.8 langchain-text-splitters==0.3.2 langchain-huggingface==0.1.2 openai==1.54.5
```

Depois execute:
```bash
cd whatsapp-stream
python main.py
```

---

## 📝 O que foi corrigido

### 1. `environment.yml` atualizado com versões compatíveis:
- `langchain==0.3.7` (era 0.2.7)
- `langchain-openai==0.2.8` (era 0.1.15)
- `openai==1.54.5` (era 1.35.13)
- Adicionado `langchain-huggingface==0.1.2`

### 2. `rag_module.py` atualizado:
- Importa `HuggingFaceEmbeddings` da nova biblioteca `langchain-huggingface`
- Fallback para versão antiga se não disponível

---

## 🎯 Após a correção

Execute novamente:

```bash
conda activate smartglasses-env
cd whatsapp-stream
python main.py
```

Você deve ver:

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
✓ Captura de áudio pronta
```

---

## ⚠️ Nota sobre dispositivos de áudio

Seus dispositivos detectados:
- **INPUT**: `CABLE-A Output (VB-Audio Virtua, MME` (índice 2)
- **OUTPUT**: `CABLE-B Input (VB-Audio Virtual, MME` (índice 11)

Os nomes no `main.py` estão corretos! ✅

---

## 🐛 Se ainda houver erro

1. Verifique se o arquivo `.env` existe com sua chave OpenAI:
   ```bash
   cat .env
   ```

2. Teste a chave:
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
   ```

3. Se a chave não aparecer, crie o arquivo `.env`:
   ```bash
   echo OPENAI_API_KEY=sua_chave_aqui > .env
   ```

