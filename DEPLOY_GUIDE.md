# 🚀 GUIA COMPLETO DE DEPLOY - OCEAN AI

## Passo a Passo para Deploy no Streamlit Community Cloud

### 📋 PRÉ-REQUISITOS

1. Conta no GitHub (gratuita)
2. Conta no Groq (gratuita) - https://console.groq.com/
3. Repositório Git inicializado no projeto

---

## PARTE 1: PREPARAÇÃO LOCAL

### 1.1 Obter API Key do Groq

1. Acesse: https://console.groq.com/
2. Crie uma conta (pode usar Google/GitHub)
3. Vá em **API Keys**
4. Clique em **Create API Key**
5. Copie a chave (formato: `gsk_...`)
6. Guarde em local seguro!

### 1.2 Testar localmente primeiro

```bash
# 1. Crie o arquivo .env
echo "GROQ_API_KEY=sua_chave_aqui" > .env

# 2. Instale dependências
pip install -r requirements.txt

# 3. Colete os dados
python coletar_dados_amazonia_azul.py

# 4. Teste o RAG engine
python rag_engine.py

# 5. Teste o app
streamlit run app.py
```

Se tudo funcionar localmente, prossiga!

---

## PARTE 2: PREPARAR REPOSITÓRIO GITHUB

### 2.1 Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `oceania-chatbot` (ou outro de sua escolha)
3. Descrição: "Ocean AI - Chatbot sobre o Oceano Atlântico adjacente ao Brasil com RAG"
4. Público ou Privado (sua escolha)
5. **NÃO** inicialize com README (já temos um)
6. Clique em **Create repository**

### 2.2 Verificar .gitignore

Certifique-se de que `.env` está no `.gitignore`:

```bash
# Verificar se .gitignore existe e contém .env
cat .gitignore | grep ".env"

# Se não estiver, adicione:
echo ".env" >> .gitignore
```

### 2.3 Commitar e enviar para GitHub

```bash
# 1. Inicializar git (se ainda não foi feito)
git init

# 2. Adicionar remote do GitHub
git remote add origin https://github.com/SEU_USUARIO/oceania-chatbot.git

# 3. Adicionar todos os arquivos
git add .

# 4. Verificar o que será commitado (NÃO DEVE INCLUIR .env)
git status

# 5. Commit
git commit -m "Initial commit: Ocean AI chatbot with RAG"

# 6. Push para GitHub
git branch -M main
git push -u origin main
```

### 2.4 Verificar no GitHub

Acesse seu repositório e confirme que estes arquivos estão lá:
- ✅ `app.py`
- ✅ `rag_engine.py`
- ✅ `coletar_dados_amazonia_azul.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `.streamlit/secrets.toml` (template vazio)
- ✅ `data/` (pasta com 8 JSONs)
- ❌ `.env` (NÃO DEVE ESTAR AQUI!)

---

## PARTE 3: DEPLOY NO STREAMLIT CLOUD

### 3.1 Acessar Streamlit Community Cloud

1. Vá para: https://streamlit.io/cloud
2. Clique em **Sign in**
3. Escolha **Continue with GitHub**
4. Autorize o Streamlit a acessar seus repositórios

### 3.2 Criar novo app

1. Clique em **New app** (botão azul no canto superior direito)
2. Preencha o formulário:

   ```
   Repository: seu-usuario/oceania-chatbot
   Branch: main
   Main file path: app.py
   App URL (optional): ocean-ai (ou deixe em branco)
   ```

3. **NÃO** clique em Deploy ainda!

### 3.3 Configurar Secrets (CRÍTICO!)

1. Clique em **Advanced settings**
2. Vá para a aba **Secrets**
3. Cole exatamente isso (substitua pela sua chave):

   ```toml
   GROQ_API_KEY = "gsk_sua_chave_real_aqui"
   ```

4. Clique em **Save**

### 3.4 Deploy!

1. Clique no botão **Deploy**
2. Aguarde o processo (pode levar 5-10 minutos):
   - ⏳ Cloning repository...
   - ⏳ Installing dependencies...
   - ⏳ Building FAISS index...
   - ⏳ Starting app...
   - ✅ Your app is live!

3. Seu app estará em: `https://ocean-ai.streamlit.app` (ou URL que escolheu)

---

## PARTE 4: VERIFICAÇÕES PÓS-DEPLOY

### 4.1 Teste o app

1. Acesse a URL do seu app
2. Aguarde carregar (primeira vez é mais lenta)
3. Teste com perguntas:
   - "Quais espécies foram registradas?"
   - "Onde ocorre a tartaruga verde?"
   - "Quais são os objetivos da Década dos Oceanos?"

### 4.2 Verificar logs

Se algo der errado:
1. No Streamlit Cloud, clique nos 3 pontinhos (...) do seu app
2. Selecione **Logs**
3. Procure por erros em vermelho

### 4.3 Erros comuns e soluções

#### ❌ "GROQ_API_KEY not found"

**Solução:**
1. Vá em Settings > Secrets
2. Verifique se a chave está correta
3. Formato: `GROQ_API_KEY = "gsk_..."`
4. Clique em "Reboot app"

#### ❌ "No such file or directory: 'data/obis_ocorrencias.json'"

**Solução:**
1. Verifique se a pasta `data/` está no GitHub
2. Verifique se os 8 JSONs estão dentro dela
3. Commit e push novamente se necessário

#### ❌ "Failed to load FAISS index"

**Solução:**
- Normal na primeira execução!
- O app vai criar o índice automaticamente
- Aguarde o processo completo

#### ❌ App muito lento

**Solução:**
- Primeiro acesso é sempre lento (carrega modelo de 500MB)
- Após cache, fica rápido
- Se persistir, considere usar modelo menor no `requirements.txt`

---

## PARTE 5: MANUTENÇÃO E ATUALIZAÇÕES

### 5.1 Atualizar dados

Para atualizar os JSONs:

```bash
# 1. Colete novos dados
python coletar_dados_amazonia_azul.py

# 2. Commit e push
git add data/
git commit -m "Atualizar dados - $(date +%Y-%m-%d)"
git push

# 3. No Streamlit Cloud, reboot o app
# (ou aguarde auto-deploy se estiver habilitado)
```

### 5.2 Atualizar código

```bash
# 1. Faça suas alterações
# 2. Teste localmente
streamlit run app.py

# 3. Commit e push
git add .
git commit -m "Descrição da mudança"
git push

# 4. Streamlit faz deploy automático!
```

### 5.3 Forçar rebuild do índice FAISS

No `app.py`, temporariamente mude:

```python
# Linha ~40
rag.setup(force_rebuild=True)  # Adicione True
```

Commit, push, aguarde deploy, depois volte para `False`.

---

## PARTE 6: OTIMIZAÇÕES

### 6.1 Reduzir tempo de carregamento

**Opção 1**: Usar modelo menor de embeddings

Em `rag_engine.py`, linha ~208:

```python
self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
# Menor e mais rápido que mpnet-base
```

**Opção 2**: Commitar índice FAISS pré-construído

```bash
# Gere localmente
python rag_engine.py

# Commit o índice
git add faiss_index chunks_metadata.pkl
git commit -m "Add pre-built FAISS index"
git push
```

Remova do `.gitignore` se necessário.

### 6.2 Melhorar respostas

Em `app.py`, ajuste o system prompt (linha ~90):

```python
system_prompt = """[seu prompt customizado aqui]"""
```

Experimente com:
- Temperatura (0.0 = factual, 1.0 = criativo)
- Max tokens (512 = curto, 2048 = longo)
- Modelo (llama-3.1-8b = rápido, llama-3.1-70b = melhor)

---

## PARTE 7: SEGURANÇA E BOAS PRÁTICAS

### ✅ Checklist de Segurança

- [ ] `.env` está no `.gitignore`
- [ ] Não há chaves de API no código
- [ ] Secrets configurados no Streamlit Cloud
- [ ] Repositório pode ser público (não expõe secrets)

### 🔒 Proteger API Key

Se alguém clonar seu repo e rodar localmente, eles precisarão da própria chave Groq.

### 📊 Monitorar uso do Groq

1. Acesse https://console.groq.com/
2. Vá em **Usage**
3. Monitore tokens consumidos
4. Plano gratuito: ~14,400 requests/dia

---

## 🎉 PRONTO!

Seu Ocean AI está no ar! 

**URL pública**: `https://seu-app.streamlit.app`

**Compartilhe** seu portfólio com:
- Link do app
- Link do GitHub
- Screenshots
- Descrição do projeto

---

## 📞 SUPORTE

- **Streamlit Docs**: https://docs.streamlit.io/
- **Groq Docs**: https://console.groq.com/docs
- **FAISS Docs**: https://github.com/facebookresearch/faiss
- **SentenceTransformers**: https://www.sbert.net/

---

## 🚀 PRÓXIMOS PASSOS

1. **Adicione mais fontes de dados** no `coletar_dados_amazonia_azul.py`
2. **Customize o design** no `app.py` (CSS)
3. **Adicione analytics** (Streamlit tem built-in)
4. **Crie testes automatizados**
5. **Adicione cache de respostas**
6. **Implemente feedback do usuário**

Boa sorte com seu projeto! 🌊
